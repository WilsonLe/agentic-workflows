from __future__ import annotations

import importlib.util
import json
import stat
import tempfile
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "calorie-tracker"
SKILL = PLUGIN / "skills" / "calorie-tracker"
HELPER = PLUGIN / "scripts" / "calorie_tracker.py"
SPEC = importlib.util.spec_from_file_location("calorie_tracker_tests", HELPER)
assert SPEC is not None and SPEC.loader is not None
tracker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracker)

FIXED_TIME = "2026-01-01T00:00:00Z"
ENTRY_ID = "00000000-0000-4000-8000-000000000001"


def analysis_fixture() -> dict[str, object]:
    return json.loads(
        (SKILL / "examples" / "synthetic-meal-analysis.json").read_text(encoding="utf-8")
    )


def contract_candidate() -> dict[str, object]:
    return {
        "google_provider": "google-drive-connector",
        "spreadsheet_id": "SYNTHETIC_SHEET_ID",
        "meals_tab": "Meals",
        "meals_sheet_id": 101,
        "items_tab": "Meal Items",
        "items_sheet_id": 102,
        "drive_folder_id": "SYNTHETIC_FOLDER_ID",
        "timezone": "Australia/Brisbane",
        "column_schema_version": 1,
        "write_mode": "append-only",
        "image_link_policy": "private-drive-url",
        "verified_at": FIXED_TIME,
    }


def stored_contract(root: Path) -> dict[str, object]:
    return tracker.set_storage_contract(
        contract_candidate(), root=root, confirm=True, timestamp=FIXED_TIME
    )


class FakeTransport:
    def __init__(self, responses: list[tuple[int, dict[str, str], object]]):
        self.responses = list(responses)
        self.calls: list[tuple[str, str, dict[str, str], bytes | None]] = []

    def __call__(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes | None,
        timeout: float,
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append((method, url, dict(headers), body))
        status, response_headers, payload = self.responses.pop(0)
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        return status, response_headers, data


class CalorieTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_json(self, name: str, payload: object, *, mode: int = 0o600) -> Path:
        path = self.root / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        path.chmod(mode)
        return path

    def install_synthetic_credential(self) -> Path:
        source = self.write_json("usda-key.json", {"api_key": "test_" + "x" * 24})
        tracker.install_usda_credential(
            source, root=self.root / "config", timestamp=FIXED_TIME
        )
        return self.root / "config"

    def test_schema_accepts_all_synthetic_examples(self) -> None:
        schema = json.loads(
            (SKILL / "schemas" / "calorie-tracker-v1.schema.json").read_text()
        )
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        for path in sorted((SKILL / "examples").glob("*.json")):
            with self.subTest(path=path.name):
                validator.validate(json.loads(path.read_text()))

    def test_credential_install_is_private_and_failed_rotation_preserves_old_record(self) -> None:
        config = self.install_synthetic_credential()
        target = config / "usda-credential.json"
        before = target.read_bytes()
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        invalid = self.root / "invalid-key.txt"
        invalid.write_text("too-short", encoding="utf-8")
        invalid.chmod(0o600)
        with self.assertRaisesRegex(tracker.TrackerError, "format is invalid"):
            tracker.install_usda_credential(invalid, root=config)
        self.assertEqual(target.read_bytes(), before)
        status = tracker.usda_credential_status(root=config)
        self.assertEqual(status["configured"], True)
        self.assertNotIn("api_key", status)

    def test_credential_source_rejects_weak_permissions_and_symlink(self) -> None:
        weak = self.root / "weak.txt"
        weak.write_text("test_" + "x" * 24, encoding="utf-8")
        weak.chmod(0o644)
        with self.assertRaisesRegex(tracker.TrackerError, "owner-readable only"):
            tracker.install_usda_credential(weak, root=self.root / "config")
        link = self.root / "link.txt"
        link.symlink_to(weak)
        with self.assertRaisesRegex(tracker.TrackerError, "non-symlink"):
            tracker.install_usda_credential(link, root=self.root / "config")

    def test_managed_private_records_fail_closed_after_permission_drift(self) -> None:
        config = self.install_synthetic_credential()
        credential = config / "usda-credential.json"
        credential.chmod(0o644)
        with self.assertRaisesRegex(tracker.TrackerError, "permissions are too broad"):
            tracker.usda_credential_status(root=config)

        contract_root = self.root / "contract"
        stored_contract(contract_root)
        contract = contract_root / "storage-contract.json"
        contract.chmod(0o644)
        with self.assertRaisesRegex(tracker.TrackerError, "permissions are too broad"):
            tracker.show_storage_contract(root=contract_root)

    def test_contract_replacement_is_revisioned_atomic_and_fail_closed(self) -> None:
        config = self.root / "config"
        first = tracker.set_storage_contract(
            contract_candidate(), root=config, confirm=True, timestamp=FIXED_TIME
        )
        self.assertEqual(first["contract_revision"], 1)
        target = config / "storage-contract.json"
        before = target.read_bytes()
        invalid = contract_candidate()
        invalid["items_sheet_id"] = invalid["meals_sheet_id"]
        with self.assertRaisesRegex(tracker.TrackerError, "must differ"):
            tracker.set_storage_contract(invalid, root=config, confirm=True)
        self.assertEqual(target.read_bytes(), before)
        replacement = contract_candidate()
        replacement["drive_folder_id"] = "SYNTHETIC_FOLDER_TWO"
        second = tracker.set_storage_contract(
            replacement,
            root=config,
            confirm=True,
            timestamp="2026-01-02T00:00:00Z",
        )
        self.assertEqual(second["contract_revision"], 2)
        self.assertEqual(second["created_at"], first["created_at"])
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_contract_set_and_clear_require_explicit_confirmation(self) -> None:
        with self.assertRaisesRegex(tracker.TrackerError, "requires confirmation"):
            tracker.set_storage_contract(contract_candidate(), root=self.root / "config")
        stored_contract(self.root / "config")
        with self.assertRaisesRegex(tracker.TrackerError, "requires confirmation"):
            tracker.clear_storage_contract(root=self.root / "config")

    def test_platform_paths_are_posix_and_windows_safe(self) -> None:
        self.assertEqual(
            tracker.resolve_config_root(
                env={"XDG_CONFIG_HOME": "/tmp/config"}, platform="darwin"
            ),
            Path("/tmp/config/amsoft/calorie-tracker"),
        )
        self.assertEqual(
            tracker.resolve_config_root(
                env={"LOCALAPPDATA": "C:/Local"}, platform="win32"
            ).as_posix(),
            "C:/Local/AMSoft/calorie-tracker",
        )

    def test_usda_normalization_scales_units_and_preserves_stated_energy(self) -> None:
        response = {
            "fdcId": 123456,
            "description": "Synthetic cooked grain",
            "foodNutrients": [
                {"nutrient": {"number": "208", "name": "Energy", "unitName": "kcal"}, "amount": 130},
                {"nutrient": {"number": "203", "name": "Protein", "unitName": "g"}, "amount": 2.5},
                {"nutrient": {"number": "205", "name": "Carbohydrate", "unitName": "g"}, "amount": 28},
                {"nutrient": {"number": "204", "name": "Total lipid", "unitName": "g"}, "amount": 0.4},
                {"nutrient": {"number": "307", "name": "Sodium", "unitName": "g"}, "amount": 0.002},
            ],
        }
        result = tracker.normalize_usda_record(response, 150, retrieved_at=FIXED_TIME)
        self.assertEqual(result["macros_for_amount"]["calories_kcal"], 195)
        self.assertEqual(result["macros_per_100g"]["sodium_mg"], 2)
        self.assertEqual(result["provider_food_id"], "123456")
        self.assertIn(result["energy_consistency"]["status"], {"plausible", "flag"})

    def test_open_food_facts_normalization_preserves_nulls(self) -> None:
        response = {
            "status": "success",
            "code": "0000000000000",
            "product": {
                "product_name": "Synthetic package",
                "nutriments": {
                    "energy-kcal_100g": 200,
                    "proteins_100g": 10,
                    "carbohydrates_100g": 20,
                    "fat_100g": 8,
                    "sodium_100g": 0.4,
                },
            },
        }
        result = tracker.normalize_off_record(response, 50, retrieved_at=FIXED_TIME)
        self.assertEqual(result["macros_for_amount"]["calories_kcal"], 100)
        self.assertEqual(result["macros_per_100g"]["sodium_mg"], 400)
        self.assertIsNone(result["macros_per_100g"]["fiber_g"])

    def test_visible_label_needs_no_external_lineage(self) -> None:
        analysis = analysis_fixture()
        item = analysis["items"][0]
        item["provider"] = "visible_label"
        item["provider_food_id"] = "synthetic-label-serving"
        item["provider_url"] = None
        item["retrieved_at"] = None
        record = tracker.build_meal_record(
            analysis, entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        self.assertIn(
            "visible_label:synthetic-label-serving",
            record["meal"]["source_summary"],
        )

    def test_external_provider_lineage_requires_exact_host_and_evidence(self) -> None:
        analysis = analysis_fixture()
        item = analysis["items"][0]
        item["provider"] = "usda"
        item["provider_food_id"] = "123456"
        item["provider_url"] = "https://example.test/food/123456"
        item["retrieved_at"] = FIXED_TIME
        item["evidence"].append(
            {"type": "provider", "statement": "Synthetic USDA record selected."}
        )
        with self.assertRaisesRegex(tracker.TrackerError, "does not match"):
            tracker.validate_analysis(analysis)

        item["provider_url"] = (
            "https://fdc.nal.usda.gov/fdc-app.html#/food-details/123456/nutrients"
        )
        item["evidence"] = [
            evidence
            for evidence in item["evidence"]
            if evidence["type"] != "provider"
        ]
        with self.assertRaisesRegex(tracker.TrackerError, "provider evidence"):
            tracker.validate_analysis(analysis)

    def test_provider_plan_deduplicates_through_cache_and_sets_user_agent(self) -> None:
        response = {
            "status": "success",
            "code": "0000000000000",
            "product": {"product_name": "Synthetic", "nutriments": {}},
        }
        transport = FakeTransport(
            [(200, {"Content-Type": "application/json"}, response)]
        )
        request = {
            "provider": "open_food_facts",
            "operation": "product",
            "barcode": "0000000000000",
        }
        client = tracker.ProviderClient(
            cache_root=self.root / "cache",
            transport=transport,
            now=lambda: FIXED_TIME,
        )
        result = client.execute({"schema_version": 1, "requests": [request, request]})
        self.assertEqual(result["request_count"], 1)
        self.assertEqual([item["cache"] for item in result["results"]], ["miss", "hit"])
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0][2]["User-Agent"], tracker.OFF_USER_AGENT)

    def test_provider_429_is_not_retried_and_retains_retry_after(self) -> None:
        transport = FakeTransport(
            [(429, {"Content-Type": "application/json", "Retry-After": "60"}, {})]
        )
        client = tracker.ProviderClient(
            cache_root=self.root / "cache", transport=transport, now=lambda: FIXED_TIME
        )
        with self.assertRaises(tracker.TrackerError) as raised:
            client.execute(
                {
                    "schema_version": 1,
                    "requests": [
                        {
                            "provider": "open_food_facts",
                            "operation": "product",
                            "barcode": "0000000000000",
                        }
                    ],
                }
            )
        self.assertEqual(raised.exception.category, "rate_limited")
        self.assertEqual(raised.exception.retry_after, "60")
        self.assertEqual(len(transport.calls), 1)

    def test_provider_5xx_has_one_bounded_retry(self) -> None:
        transport = FakeTransport(
            [
                (503, {"Content-Type": "application/json"}, {}),
                (200, {"Content-Type": "application/json"}, {"status": "success"}),
            ]
        )
        client = tracker.ProviderClient(
            cache_root=self.root / "cache", transport=transport, now=lambda: FIXED_TIME
        )
        result = client.execute(
            {
                "schema_version": 1,
                "requests": [
                    {
                        "provider": "open_food_facts",
                        "operation": "product",
                        "barcode": "0000000000000",
                    }
                ],
            }
        )
        self.assertEqual(result["request_count"], 2)
        self.assertEqual(len(transport.calls), 2)

    def test_usda_provider_output_does_not_echo_credential(self) -> None:
        config = self.install_synthetic_credential()
        transport = FakeTransport(
            [
                (
                    200,
                    {"Content-Type": "application/json"},
                    {"foods": [{"fdcId": 123456, "description": "Synthetic"}]},
                )
            ]
        )
        client = tracker.ProviderClient(
            credential_root=config,
            cache_root=self.root / "cache",
            transport=transport,
            now=lambda: FIXED_TIME,
        )
        result = client.execute(
            {
                "schema_version": 1,
                "requests": [
                    {"provider": "usda", "operation": "search", "query": "synthetic grain"}
                ],
            }
        )
        self.assertNotIn("test_", json.dumps(result))
        self.assertNotIn("api_key", json.dumps(result))

    def test_record_totals_ranges_and_optional_null_semantics(self) -> None:
        record = tracker.build_meal_record(
            analysis_fixture(), entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        self.assertEqual(record["meal"]["calories_kcal"], 299)
        self.assertEqual(record["meal"]["calories_low_kcal"], 230.75)
        self.assertEqual(record["meal"]["calories_high_kcal"], 370.5)
        self.assertEqual(record["meal"]["total_sugar_g"], 0.18)
        tracker.validate_meal_record(record)

    def test_recomputed_digest_cannot_hide_invalid_meal_row_types(self) -> None:
        record = tracker.build_meal_record(
            analysis_fixture(), entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        record["meal"]["calories_kcal"] = "299"
        record["record_digest"] = tracker.digest_payload(
            {"meal": record["meal"], "items": record["items"]}
        )
        with self.assertRaisesRegex(tracker.TrackerError, "must be numeric"):
            tracker.validate_meal_record(record)

    def test_analysis_only_cannot_build_a_google_write(self) -> None:
        analysis = analysis_fixture()
        analysis["intent"] = "analyze"
        analysis["image"]["storage_authorized"] = False
        record = tracker.build_meal_record(
            analysis, entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        with self.assertRaisesRegex(tracker.TrackerError, "analysis-only"):
            tracker.build_sheet_batch(record, stored_contract(self.root / "config"))

    def test_sheet_batch_is_atomic_typed_and_formula_safe(self) -> None:
        record = tracker.build_meal_record(
            analysis_fixture(), entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        record = tracker.bind_drive_image(
            record,
            "SYNTHETIC_FILE_ID",
            "https://drive.google.com/file/d/SYNTHETIC_FILE_ID/view",
        )
        batch = tracker.build_sheet_batch(record, stored_contract(self.root / "config"))
        self.assertEqual(len(batch["requests"]), 2)
        self.assertEqual(
            [request["appendCells"]["sheetId"] for request in batch["requests"]],
            [101, 102],
        )
        item_description_index = tracker.ITEM_COLUMNS.index("description")
        cell = batch["requests"][1]["appendCells"]["rows"][0]["values"][item_description_index]
        self.assertEqual(cell, {"userEnteredValue": {"stringValue": "=synthetic cooked rice"}})
        serialized = json.dumps(batch)
        self.assertNotIn("formulaValue", serialized)
        self.assertNotIn("IMAGE(", serialized)

    def test_journal_reuses_stable_identity_and_blocks_blind_retry(self) -> None:
        record = tracker.build_meal_record(
            analysis_fixture(), entry_id=ENTRY_ID, timestamp=FIXED_TIME
        )
        contract = stored_contract(self.root / "config")
        state = self.root / "state"
        journal = tracker.create_journal(
            record, contract, root=state, timestamp=FIXED_TIME
        )
        self.assertEqual(journal["state"], "planned")
        with self.assertRaisesRegex(tracker.TrackerError, "already exists"):
            tracker.create_journal(record, contract, root=state)
        uploaded = tracker.transition_journal(
            ENTRY_ID,
            "image_uploaded",
            root=state,
            drive_file_id="SYNTHETIC_FILE_ID",
            drive_url="https://drive.google.com/file/d/SYNTHETIC_FILE_ID/view",
        )
        self.assertEqual(uploaded["drive_file_id"], "SYNTHETIC_FILE_ID")
        batch_digest = "sha256:" + "1" * 64
        tracker.transition_journal(
            ENTRY_ID,
            "sheet_written_unverified",
            root=state,
            sheet_batch_digest=batch_digest,
        )
        verified = tracker.transition_journal(ENTRY_ID, "verified", root=state)
        self.assertEqual(verified["state"], "verified")
        with self.assertRaisesRegex(tracker.TrackerError, "cannot transition"):
            tracker.transition_journal(ENTRY_ID, "failed_recoverable", root=state)

    def test_catalog_declares_standalone_central_mirror_and_helper(self) -> None:
        catalog = yaml.safe_load((ROOT / "catalog" / "plugins-v1.yaml").read_text())
        package = next(item for item in catalog["packages"] if item["name"] == "calorie-tracker")
        self.assertEqual([item["name"] for item in package["skills"]], ["calorie-tracker"])
        central = next(
            item for item in catalog["packages"] if item["name"] == "amsoft-agentic-workflows"
        )
        self.assertIn("amsoft-calorie-tracker", {item["name"] for item in central["skills"]})
        self.assertIn("scripts/calorie_tracker.py", central["executables"])
        mirrors = {item["name"] for item in catalog["mirrors"]}
        self.assertIn("calorie-tracker-skill", mirrors)
        self.assertIn("calorie-tracker-helper", mirrors)

    def test_source_and_central_portable_files_are_identical(self) -> None:
        central = ROOT / "plugins" / "amsoft-agentic-workflows" / "skills" / "amsoft-calorie-tracker"
        for directory in ("examples", "references", "schemas"):
            source_files = {
                path.relative_to(SKILL / directory): path.read_bytes()
                for path in (SKILL / directory).rglob("*")
                if path.is_file()
            }
            central_files = {
                path.relative_to(central / directory): path.read_bytes()
                for path in (central / directory).rglob("*")
                if path.is_file()
            }
            self.assertEqual(source_files, central_files)
        self.assertEqual(
            HELPER.read_bytes(),
            (ROOT / "plugins" / "amsoft-agentic-workflows" / "scripts" / "calorie_tracker.py").read_bytes(),
        )

    def test_repository_examples_contain_only_synthetic_identifiers(self) -> None:
        combined = "\n".join(path.read_text() for path in (SKILL / "examples").glob("*.json"))
        self.assertIn("synthetic", combined.lower())
        self.assertNotIn("ya29.", combined)
        self.assertNotIn("AIza", combined)
        self.assertNotIn("gho_", combined)

    def test_helper_has_no_google_mutation_or_image_upload_client(self) -> None:
        text = HELPER.read_text(encoding="utf-8")
        self.assertNotIn("sheets.googleapis.com", text)
        self.assertNotIn("www.googleapis.com/upload", text)
        self.assertNotIn("share_file", text)
        self.assertIn('"appendCells"', text)
        self.assertIn("MAX_PROVIDER_REQUESTS = 20", text)


if __name__ == "__main__":
    unittest.main()
