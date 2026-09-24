from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENTRAL_SKILL = (
    ROOT
    / "plugins"
    / "agentic-workflows"
    / "skills"
    / "agentic-workflows"
)
REFERENCE = CENTRAL_SKILL / "references" / "plugin-troubleshooting.md"
ROUTER = CENTRAL_SKILL / "SKILL.md"
MANIFEST = (
    ROOT
    / "plugins"
    / "agentic-workflows"
    / ".codex-plugin"
    / "plugin.json"
)


class PluginTroubleshootingTests(unittest.TestCase):
    def test_reference_is_present_and_routed(self) -> None:
        self.assertTrue(REFERENCE.is_file())
        router = ROUTER.read_text(encoding="utf-8")
        self.assertIn(
            "[plugin-troubleshooting.md](references/plugin-troubleshooting.md)",
            router,
        )
        self.assertIn("plugin troubleshooting runbook", router)

    def test_reference_preserves_the_chrome_cache_failure_contract(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for marker in (
            "Browser is not available: chrome",
            "extension-host-config.json",
            "latest",
            "versioned sibling bundle",
            "cache-registration/configuration lifecycle failure",
            "manifest check validates registration fields and origins",
            "Select the requested Chrome browser family",
            "List the user's open tabs",
            "Claim one exact tab",
            "Read its URL, title, or visible DOM state",
            "static diagnostics",
            "live control evidence",
        ):
            self.assertIn(marker, text, marker)

    def test_manual_recovery_is_explicitly_bounded(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for marker in (
            "explicitly authorizes it",
            "exact existing host",
            "preserve the prior manifest/config",
            "never guess a path",
            "profile data",
            "broad caches",
            "tactical workaround",
            "Do not represent the workaround as an upstream installer fix",
        ):
            self.assertIn(marker, text, marker)
        self.assertNotIn("/Users/", text)
        self.assertNotIn("gho_", text)

    def test_plugin_metadata_remains_valid_json(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "agentic-workflows")
        self.assertRegex(manifest["version"], r"^0\.2\.0\+codex\.\d{14}$")


if __name__ == "__main__":
    unittest.main()
