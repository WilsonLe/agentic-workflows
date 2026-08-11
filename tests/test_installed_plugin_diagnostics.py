from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "scripts"
    / "diagnose_installed_plugins.py"
)
SPEC = importlib.util.spec_from_file_location("diagnose_installed_plugins", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
DIAGNOSTIC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTIC)


class InstalledPluginDiagnosticTests(unittest.TestCase):
    def test_duplicate_enabled_names_and_cache_state_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cache_root = Path(temporary)
            expected_cache = cache_root / "amsoft" / "example" / "2.0.0"
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
                        "pluginId": "example@amsoft",
                        "name": "example",
                        "marketplaceName": "amsoft",
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
            ["example@personal", "example@amsoft"],
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
                    "pluginId": "example@amsoft",
                    "name": "example",
                    "marketplaceName": "amsoft",
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
            cache = cache_root / "amsoft" / "example" / "2.0.0"
            for package in (expected, source, cache):
                (package / ".codex-plugin").mkdir(parents=True)
                (package / ".codex-plugin" / "plugin.json").write_text(
                    json.dumps({"name": "example", "version": "2.0.0"})
                )
                (package / "content.txt").write_text("same")
            payload = {
                "installed": [
                    {
                        "pluginId": "example@amsoft",
                        "name": "example",
                        "marketplaceName": "amsoft",
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
                "amsoft",
                {"example": expected},
            )
        selected = report["authoritative_providers"]["example"]
        self.assertTrue(selected["version_matches"])
        self.assertTrue(selected["source_parity"]["matches"])
        self.assertTrue(selected["cache_parity"]["matches"])

    def test_malformed_plugin_list_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "installed array"):
            DIAGNOSTIC.analyze_plugin_list({}, Path("/missing-cache"))


if __name__ == "__main__":
    unittest.main()
