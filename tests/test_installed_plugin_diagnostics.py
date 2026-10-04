from __future__ import annotations

import importlib.util
import copy
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "plugins" / "agentic-workflows" / "scripts" / "diagnose_installed_plugins.py"
)
SPEC = importlib.util.spec_from_file_location("diagnose_installed_plugins", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
DIAGNOSTIC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTIC)


class InstalledPluginDiagnosticTests(unittest.TestCase):
    def test_duplicate_enabled_names_and_cache_state_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cache_root = Path(temporary)
            expected_cache = cache_root / "agentic-workflows" / "example" / "2.0.0"
            expected_cache.mkdir(parents=True)
            payload = {
                "installed": [
                    {
                        "pluginId": "example@personal",
                        "name": "example",
                        "marketplaceName": "personal",
                        "version": "1.0.0",
                        "installed": True,
                        "enabled": True,
                        "source": {"path": temporary},
                    },
                    {
                        "pluginId": "example@agentic-workflows",
                        "name": "example",
                        "marketplaceName": "agentic-workflows",
                        "version": "2.0.0",
                        "installed": True,
                        "enabled": True,
                        "source": {"path": temporary},
                    },
                ]
            }
            report = DIAGNOSTIC.analyze_plugin_list(payload, cache_root)
        self.assertEqual(
            report["duplicate_enabled_names"]["example"],
            ["example@personal", "example@agentic-workflows"],
        )
        self.assertEqual(
            [item["version"] for item in report["provider_conflicts"]["example"]],
            ["1.0.0", "2.0.0"],
        )
        self.assertTrue(report["plugins"][1]["cache_exists"])

    def test_disabled_provider_is_not_a_duplicate(self) -> None:
        payload = {
            "installed": [
                {
                    "pluginId": "example@personal",
                    "name": "example",
                    "marketplaceName": "personal",
                    "version": "1.0.0",
                    "installed": True,
                    "enabled": False,
                },
                {
                    "pluginId": "example@agentic-workflows",
                    "name": "example",
                    "marketplaceName": "agentic-workflows",
                    "version": "2.0.0",
                    "installed": True,
                    "enabled": True,
                },
            ]
        }
        report = DIAGNOSTIC.analyze_plugin_list(payload, Path("/missing-cache"))
        self.assertEqual(report["duplicate_enabled_names"], {})

    def test_broken_launcher_does_not_hide_later_working_candidate(self) -> None:
        def runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            if command[0] == "/broken/codex":
                raise OSError("missing")
            return subprocess.CompletedProcess(command, 0, "codex 1.2.3\n", "")

        selected, probes = DIAGNOSTIC.probe_codex_candidates(
            ["/broken/codex", "/working/codex"],
            runner=runner,
        )
        self.assertEqual(selected, "/working/codex")
        self.assertFalse(probes[0]["usable"])
        self.assertTrue(probes[1]["usable"])

    def test_required_skill_availability_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill = Path(temporary) / "SKILL.md"
            skill.write_text("skill")
            report = DIAGNOSTIC.analyze_required_skills(
                [f"present={skill}", f"missing={skill.parent / 'missing.md'}"]
            )
        self.assertTrue(report[0]["available"])
        self.assertFalse(report[1]["available"])
        self.assertIn("repository catalog", report[1]["fallback"])

    def test_authoritative_provider_version_and_parity_are_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected = root / "expected"
            source = root / "source"
            cache_root = root / "cache"
            cache = cache_root / "agentic-workflows" / "example" / "2.0.0"
            for package in (expected, source, cache):
                (package / ".codex-plugin").mkdir(parents=True)
                (package / ".codex-plugin" / "plugin.json").write_text(
                    json.dumps({"name": "example", "version": "2.0.0"})
                )
                (package / "content.txt").write_text("same")
            payload = {
                "installed": [
                    {
                        "pluginId": "example@agentic-workflows",
                        "name": "example",
                        "marketplaceName": "agentic-workflows",
                        "version": "2.0.0",
                        "installed": True,
                        "enabled": True,
                        "source": {"path": str(source)},
                    }
                ]
            }
            report = DIAGNOSTIC.analyze_plugin_list(
                payload,
                cache_root,
                "agentic-workflows",
                {"example": expected},
            )
        selected = report["authoritative_providers"]["example"]
        self.assertTrue(selected["version_matches"])
        self.assertTrue(selected["source_parity"]["matches"])
        self.assertTrue(selected["cache_parity"]["matches"])

    def test_malformed_plugin_list_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "installed array"):
            DIAGNOSTIC.analyze_plugin_list({}, Path("/missing-cache"))


class RequestedVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.expected = root / "expected"
        self.source = root / "source"
        self.cache_root = root / "cache"
        self.cache = self.cache_root / "authority/example/2.0.0"
        for package in (self.expected, self.source, self.cache):
            (package / ".codex-plugin").mkdir(parents=True)
            (package / ".codex-plugin/plugin.json").write_text(
                json.dumps({"name": "example", "version": "2.0.0"})
            )
            (package / "skills/test-skill").mkdir(parents=True)
            (package / "skills/test-skill/SKILL.md").write_text("matching skill")
        self.payload = {
            "installed": [
                {
                    "pluginId": "example@authority",
                    "name": "example",
                    "marketplaceName": "authority",
                    "version": "2.0.0",
                    "installed": True,
                    "enabled": True,
                    "source": {"path": str(self.source)},
                }
            ]
        }
        self.discovery = {
            "task_id": "fresh-task",
            "created_at": "2026-10-04T02:00:00Z",
            "observed_at": "2026-10-04T02:01:00Z",
            "skills": [
                {
                    "name": "test-skill",
                    "plugin_id": "example@authority",
                    "path": str(self.cache / "skills/test-skill/SKILL.md"),
                }
            ],
        }
        self.boundary = "2026-10-04T01:00:00Z"

    def analyze(self):
        return DIAGNOSTIC.analyze_plugin_list(
            self.payload, self.cache_root, "authority", {"example": self.expected}
        )

    def discovery_report(self):
        return DIAGNOSTIC.analyze_discovery(
            self.discovery, self.analyze(), {"example": self.expected}, self.boundary
        )

    def test_empty_absent_disabled_or_not_installed_expected_package_fails(self):
        variants = [{"installed": []}]
        for field in ("enabled", "installed"):
            payload = copy.deepcopy(self.payload)
            payload["installed"][0][field] = False
            variants.append(payload)
        for payload in variants:
            self.payload = payload
            report = self.analyze()
            self.assertEqual(report["requested_verification"], "failed")
            self.assertEqual(
                report["authoritative_providers"]["example"]["status"], "missing"
            )

    def test_requested_provider_conflict_and_ambiguity_fail(self):
        original = copy.deepcopy(self.payload)
        for marketplace in ("authority", "legacy"):
            self.payload = copy.deepcopy(original)
            duplicate = copy.deepcopy(self.payload["installed"][0])
            duplicate.update(
                marketplaceName=marketplace, pluginId=f"duplicate@{marketplace}"
            )
            self.payload["installed"].append(duplicate)
            self.assertEqual(self.analyze()["requested_verification"], "failed")

    def test_wrong_version_missing_source_cache_and_different_bytes_fail(self):
        original = copy.deepcopy(self.payload)
        for change in ("version", "source", "cache", "bytes"):
            self.payload = copy.deepcopy(original)
            with self.subTest(change=change):
                if change == "version":
                    self.payload["installed"][0]["version"] = "1.0.0"
                elif change == "source":
                    self.payload["installed"][0].pop("source")
                elif change == "cache":
                    self.cache_root = Path(self.temporary.name) / "absent-cache"
                else:
                    self.source.joinpath("skills/test-skill/SKILL.md").write_text(
                        "different"
                    )
                self.assertEqual(self.analyze()["requested_verification"], "failed")
                self.cache_root = self.cache.parents[2]

    def test_matching_provider_and_discovery_pass(self):
        self.assertEqual(self.analyze()["requested_verification"], "verified")
        self.assertEqual(self.discovery_report()["verification"], "verified")

    def test_qualified_catalog_names_match_selected_package_and_catch_duplicates(self):
        self.discovery["skills"][0]["name"] = "example:test-skill"
        self.assertEqual(self.discovery_report()["verification"], "verified")
        self.discovery["skills"][0]["name"] = "legacy:test-skill"
        self.assertEqual(self.discovery_report()["verification"], "failed")
        self.discovery["skills"][0]["name"] = "example:test-skill"
        duplicate = dict(self.discovery["skills"][0], name="legacy:test-skill")
        self.discovery["skills"].append(duplicate)
        self.assertEqual(self.discovery_report()["verification"], "failed")

    def test_discovery_missing_duplicate_wrong_provider_old_path_and_stale_task_fail(
        self
    ):
        original = copy.deepcopy(self.discovery)
        for change in ("missing", "duplicate", "provider", "path", "time"):
            self.discovery = copy.deepcopy(original)
            with self.subTest(change=change):
                if change == "missing":
                    self.discovery["skills"] = []
                elif change == "duplicate":
                    self.discovery["skills"] *= 2
                elif change == "provider":
                    self.discovery["skills"][0]["plugin_id"] = "example@legacy"
                elif change == "path":
                    self.discovery["skills"][0]["path"] = str(
                        self.source / "skills/test-skill/SKILL.md"
                    )
                else:
                    self.discovery["created_at"] = "2026-10-03T00:00:00Z"
                self.assertEqual(self.discovery_report()["verification"], "failed")

    def test_cli_fails_requested_parity_and_preserves_unrequested_behavior(self):
        file = Path(self.temporary.name) / "plugins.json"
        file.write_text(json.dumps({"installed": []}))
        common = [
            "diagnostic",
            "--plugin-list-file",
            str(file),
            "--cache-root",
            str(self.cache_root),
        ]
        requested = [
            "--authoritative-marketplace",
            "authority",
            "--expected-package",
            f"example={self.expected}",
        ]
        for args, expected_exit, state in (
            (common, 0, "unobserved"),
            (common + requested, 3, "failed"),
        ):
            output = io.StringIO()
            with patch("sys.argv", args), patch.object(
                DIAGNOSTIC, "candidate_paths", return_value=[]
            ), contextlib.redirect_stdout(output):
                self.assertEqual(DIAGNOSTIC.main(), expected_exit)
            report = json.loads(output.getvalue())
            self.assertEqual(report["installed_state"]["requested_verification"], state)
            self.assertEqual(report["fresh_discovery"]["verification"], "unobserved")

    def test_expectations_without_marketplace_or_discovery_boundary_rejected(self):
        with self.assertRaises(ValueError):
            DIAGNOSTIC.analyze_plugin_list(
                self.payload,
                self.cache_root,
                expected_packages={"example": self.expected},
            )
        with self.assertRaises(ValueError):
            DIAGNOSTIC.analyze_discovery(
                self.discovery, self.analyze(), {"example": self.expected}, None
            )

    def test_cli_matching_then_changed_bytes_and_stale_discovery_exit(self):
        file = Path(self.temporary.name) / "plugins.json"
        discovery = Path(self.temporary.name) / "discovery.json"
        file.write_text(json.dumps(self.payload))
        common = [
            "diagnostic",
            "--plugin-list-file",
            str(file),
            "--cache-root",
            str(self.cache_root),
            "--authoritative-marketplace",
            "authority",
            "--expected-package",
            f"example={self.expected}",
        ]
        for change, exit_code in (("matching", 0), ("stale", 3), ("bytes", 3)):
            args = list(common)
            if change == "stale":
                self.discovery["created_at"] = "2026-10-03T00:00:00Z"
                discovery.write_text(json.dumps(self.discovery))
                args += [
                    "--discovery-file",
                    str(discovery),
                    "--discovery-not-before",
                    self.boundary,
                ]
            if change == "bytes":
                self.cache.joinpath("skills/test-skill/SKILL.md").write_text(
                    "old installed bytes"
                )
            with self.subTest(change=change), patch("sys.argv", args), patch.object(
                DIAGNOSTIC, "candidate_paths", return_value=[]
            ), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(DIAGNOSTIC.main(), exit_code)


if __name__ == "__main__":
    unittest.main()
