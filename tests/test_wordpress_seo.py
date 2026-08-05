from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "wordpress-seo"
SKILL = PLUGIN / "skills" / "wordpress-seo-management"
CENTRAL_SKILL = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "amsoft-wordpress-seo-management"
)


class WordPressSeoTests(unittest.TestCase):
    def test_manifest_describes_research_and_controlled_writes(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "wordpress-seo")
        self.assertEqual(manifest["license"], "LicenseRef-AMSoft-Proprietary")
        self.assertEqual(
            manifest["interface"]["capabilities"],
            ["Interactive", "Read", "Write", "Research"],
        )

    def test_skill_preserves_people_first_and_publication_boundaries(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "people-first content",
            "Do not copy competitor prose",
            "Do not invent search volume",
            "authorizes a proposed draft, not publication",
            "Refetch immediately before writing",
            "claim ranking improvement before comparable post-change data exists",
        ):
            self.assertIn(marker, text)

    def test_content_gap_workflow_rejects_topic_copying(self) -> None:
        text = (
            SKILL / "references" / "content-discovery-and-gap-analysis.md"
        ).read_text(encoding="utf-8")
        self.assertIn("A competitor topic alone is not a content gap", text)
        self.assertIn("Do not invent search volume or traffic forecasts", text)
        self.assertIn("Check for cannibalization", text)
        self.assertIn("query-to-page mismatch", text.lower())
        self.assertIn("supported", text)

    def test_free_source_registry_distinguishes_access_and_evidence(self) -> None:
        sources = (SKILL / "references" / "free-seo-data-sources.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "Google Search Console",
            "Google Trends API",
            "Alpha/restricted",
            "Bing Keyword Research",
            "Microsoft Clarity",
            "Ahrefs Free",
            "Common Crawl",
            "open_source: yes/no/unknown",
        ):
            self.assertIn(marker, sources)
        self.assertIn("free with account and billing setup", sources.lower())

    def test_browser_and_api_runbook_is_bounded_and_secret_safe(self) -> None:
        runbook = (
            SKILL / "references" / "browser-and-api-research-runbook.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Prefer the API",
            "Prefer Chrome",
            "Do not reverse-engineer private dashboard calls",
            "Do not extract credentials from Chrome",
            "do not scrape",
            "Evidence matrix",
            "not a synthetic universal",
            "task-owned",
            "tab_cleanup_failed",
        ):
            self.assertIn(marker, runbook)
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for marker in ("task-created tab", "pre-existing user tabs", "tab_cleanup_failed"):
            self.assertIn(marker, skill_text)

    def test_source_and_central_portable_files_match(self) -> None:
        source_files = {
            path.relative_to(SKILL): path.read_bytes()
            for path in SKILL.rglob("*")
            if path.is_file()
            and path.name != "SKILL.md"
            and path.relative_to(SKILL) != Path("agents/openai.yaml")
        }
        central_files = {
            path.relative_to(CENTRAL_SKILL): path.read_bytes()
            for path in CENTRAL_SKILL.rglob("*")
            if path.is_file()
            and path.name != "SKILL.md"
            and path.relative_to(CENTRAL_SKILL) != Path("agents/openai.yaml")
        }
        self.assertEqual(source_files, central_files)

        central_skill_text = (CENTRAL_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: amsoft-wordpress-seo-management", central_skill_text)
        self.assertNotIn("name: wordpress-seo-management\n", central_skill_text)


if __name__ == "__main__":
    unittest.main()
