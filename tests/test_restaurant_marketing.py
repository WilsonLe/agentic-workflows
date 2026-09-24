from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (
    ROOT
    / "plugins"
    / "restaurant-marketing"
    / "skills"
    / "restaurant-marketing-management"
)
HELPER = SKILL / "scripts" / "restaurant_marketing.py"
EXAMPLES = SKILL / "examples"
TEMPLATES = SKILL / "templates"

SPEC = importlib.util.spec_from_file_location("restaurant_marketing", HELPER)
assert SPEC is not None and SPEC.loader is not None
restaurant_marketing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(restaurant_marketing)


def fixture(name: str) -> dict[str, object]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class RestaurantMarketingTests(unittest.TestCase):
    def test_all_templates_and_examples_validate(self) -> None:
        for path in sorted([*TEMPLATES.glob("*.json"), *EXAMPLES.glob("*.json")]):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(restaurant_marketing.validate_record(payload), payload)

    def test_offer_economics_are_recalculated_from_inputs(self) -> None:
        result = restaurant_marketing.economics_summary(fixture("offer-campaign.json"))
        self.assertEqual(result["baseline_contribution_per_unit"], "22.00")
        self.assertEqual(result["promoted_contribution_per_incremental_unit"], "19.00")
        self.assertEqual(result["contribution_change_per_unit"], "-3.00")
        self.assertEqual(result["incremental_units_to_cover_fixed_cost"], 13)
        self.assertEqual(
            [scenario["incremental_contribution_after_fixed_cost"] for scenario in result["scenarios"]],
            ["-50.00", "235.00", "615.00"],
        )

    def test_utm_is_stable_and_contains_no_personal_data(self) -> None:
        record = fixture("new-dish-campaign.json")
        self.assertEqual(
            restaurant_marketing.build_utm(record),
            "https://example.invalid/menu/winter-noodle-bowl"
            "?utm_id=winter_noodle_launch&utm_source=website&utm_medium=owned"
            "&utm_campaign=winter_noodle_launch&utm_content=dish_page",
        )

    def test_offer_requires_economics(self) -> None:
        record = fixture("offer-campaign.json")
        record["economics"] = None
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "required for an offer"):
            restaurant_marketing.validate_record(record)

    def test_publication_ready_campaign_rejects_unknowns(self) -> None:
        record = fixture("new-dish-campaign.json")
        record["campaign"]["status"] = "approved"
        record["unknowns"] = ["Final owner confirmation"]
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "blockers or unknowns"):
            restaurant_marketing.validate_record(record)

    def test_high_risk_claim_requires_source_and_verification(self) -> None:
        record = fixture("seasonal-dish-campaign.json")
        record["campaign"]["status"] = "approved"
        record["claims"][0]["source"] = None
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "high-risk claim"):
            restaurant_marketing.validate_record(record)

    def test_mutating_deliverable_requires_exact_target_approval(self) -> None:
        record = fixture("new-dish-campaign.json")
        record["deliverables"][0]["status"] = "scheduled"
        record["approvals"][0]["status"] = "approved"
        record["approvals"][0]["target"] = "different_deliverable"
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "exact-target approval"):
            restaurant_marketing.validate_record(record)

    def test_vanity_metric_cannot_be_primary_kpi(self) -> None:
        record = fixture("new-dish-campaign.json")
        record["measurement"]["primary_kpi"] = "Impressions"
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "business outcome"):
            restaurant_marketing.validate_record(record)

    def test_review_policy_invariants_cannot_be_disabled(self) -> None:
        record = fixture("new-dish-campaign.json")
        record["compliance"]["review_policy"]["no_review_gating"] = False
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "must be true"):
            restaurant_marketing.validate_record(record)

    def test_unknown_fields_fail_closed(self) -> None:
        record = fixture("new-dish-campaign.json")
        record["invented_field"] = "must fail"
        with self.assertRaisesRegex(restaurant_marketing.RecordError, "unknown field"):
            restaurant_marketing.validate_record(record)

    def test_compact_summary_preserves_blockers_and_pending_approvals(self) -> None:
        record = json.loads((TEMPLATES / "campaign-plan.json").read_text(encoding="utf-8"))
        summary = restaurant_marketing.compact_summary(record)
        self.assertIn("Final operational dates", summary["blockers"])
        self.assertEqual(summary["pending_approvals"], ["approve_owned_menu_draft"])
        self.assertEqual(summary["next_boundary"], "Resolve blockers")

    def test_helper_has_no_network_or_mutation_commands(self) -> None:
        text = HELPER.read_text(encoding="utf-8")
        self.assertNotIn("requests", text)
        self.assertNotIn("subprocess", text)
        self.assertNotIn("urllib.request", text)
        self.assertIn('for command in ("validate", "economics", "utm", "summary"):', text)

    def test_source_and_central_portable_files_are_identical(self) -> None:
        central = (
            ROOT
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "restaurant-marketing-management"
        )
        portable = ["examples", "references", "schemas", "scripts", "templates"]
        source_files = {
            path.relative_to(SKILL): path.read_bytes()
            for directory in portable
            for path in (SKILL / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        central_files = {
            path.relative_to(central): path.read_bytes()
            for directory in portable
            for path in (central / directory).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(source_files, central_files)


if __name__ == "__main__":
    unittest.main()
