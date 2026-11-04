from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agentic-workflows"
SKILL = PLUGIN / "skills" / "reddit-browsing"


class RedditPluginTests(unittest.TestCase):
    def test_catalog_exposes_the_codex_only_browser_skill(self) -> None:
        catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        skill = next(item for item in package["skills"] if item["name"] == "reddit-browsing")
        self.assertEqual(skill["harnesses"], ["codex"])
        self.assertFalse((SKILL / "scripts").exists())

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
