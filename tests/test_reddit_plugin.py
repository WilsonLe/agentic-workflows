from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "reddit"
SKILL = PLUGIN / "skills" / "reddit-browsing"
CENTRAL = ROOT / "plugins" / "agentic-workflows"


class RedditPluginTests(unittest.TestCase):
    def test_manifest_and_catalog_expose_the_read_only_browser_plugin(self) -> None:
        manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
        catalog = yaml.safe_load((ROOT / "catalog" / "plugins-v2.yaml").read_text())
        package = next(package for package in catalog["packages"] if package["name"] == "reddit")
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "agentic-workflows"
        )

        self.assertEqual(manifest["name"], "reddit")
        self.assertEqual(manifest["interface"]["displayName"], "Reddit")
        self.assertEqual([skill["name"] for skill in package["skills"]], ["reddit-browsing"])
        self.assertEqual(package["executables"], [])
        self.assertEqual(
            package["runtime_dependencies"],
            [
                "Host browser controls (prefer the Codex in-app browser)",
            ],
        )
        self.assertIn(
            "reddit-browsing",
            {skill["name"] for skill in central["skills"]},
        )

    def test_skill_has_bounded_cdp_and_privacy_contracts(self) -> None:
        skill = (SKILL / "SKILL.md").read_text()
        onboarding = (SKILL / "references" / "onboarding.md").read_text()
        operation = (SKILL / "references" / "operation-contract.md").read_text()
        evidence = (SKILL / "references" / "evidence-and-reporting.md").read_text()

        for marker in (
            "Chrome",
            "CDP",
            "read-only",
            "Reddit API",
            "raw CDP socket",
            "infinite scroll",
            "cookies",
            "passwords",
            "CAPTCHA",
            "subreddit",
            "visible comments",
            "task-owned",
            "tab_cleanup_failed",
        ):
            self.assertIn(marker, skill)
        for marker in (
            "Needs sign-in",
            "Needs configuration",
            "reddit_rate_limited",
            "task-owned",
            "tab_cleanup_failed",
        ):
            self.assertIn(marker, onboarding + operation)
        for marker in (
            "captured_at",
            "observed_items",
            "in this sample",
            "not a complete dataset",
            "task-created tabs were closed",
        ):
            self.assertIn(marker, evidence + skill)

    def test_skill_is_instruction_only(self) -> None:
        self.assertFalse((SKILL / "scripts").exists())
        self.assertFalse((SKILL / "schemas").exists())
        self.assertFalse((SKILL / "examples").exists())
        self.assertFalse(any(path.suffix in {".py", ".js", ".mjs"} for path in SKILL.rglob("*")))


if __name__ == "__main__":
    unittest.main()
