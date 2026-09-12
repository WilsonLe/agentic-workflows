from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "wordpress-project-management"
)
CENTRAL_ROUTER = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "amsoft-agentic-workflows"
    / "SKILL.md"
)
CENTRAL_ONBOARDING = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "amsoft-agentic-workflows"
    / "references"
    / "onboarding.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class WordPressProjectManagementTests(unittest.TestCase):
    def test_skill_metadata_and_catalog_discoverability(self) -> None:
        skill = read(SKILL_ROOT / "SKILL.md")
        metadata = yaml.safe_load(read(SKILL_ROOT / "agents" / "openai.yaml"))
        catalog = yaml.safe_load(read(ROOT / "catalog" / "plugins-v1.yaml"))
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        central_names = {entry["name"] for entry in central["skills"]}

        self.assertIn("name: wordpress-project-management", skill)
        self.assertIn("content-as-code", skill)
        self.assertIn("checksum", skill)
        self.assertEqual(metadata["interface"]["default_prompt"].split()[1], "$wordpress-project-management")
        self.assertIn("wordpress-project-management", central_names)
        self.assertEqual(catalog["documentation"]["central_component_count"], 29)

    def test_references_and_examples_are_present(self) -> None:
        expected = {
            "onboarding-and-state.md",
            "lifecycle-and-gates.md",
            "site-management.md",
            "surfaces-and-evidence.md",
            "browser-and-private-pages.md",
            "integrations-and-data-flows.md",
            "drift-rollback-and-incidents.md",
            "content-as-code-and-concurrency.md",
            "issue-and-plan-handoffs.md",
        }
        self.assertEqual(
            {path.name for path in (SKILL_ROOT / "references").glob("*.md")},
            expected,
        )
        self.assertTrue((SKILL_ROOT / "schemas" / "project-state-v1.schema.json").is_file())
        self.assertTrue((SKILL_ROOT / "schemas" / "content-lock-v1.schema.json").is_file())

    def test_secret_free_examples_validate_against_schemas(self) -> None:
        examples = (
            "project-state-v1.json",
            "content-lock-v1.json",
        )
        for name in examples:
            example = json.loads(read(SKILL_ROOT / "examples" / name))
            schema_name = name.replace(".json", ".schema.json")
            schema = json.loads(read(SKILL_ROOT / "schemas" / schema_name))
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.validate(example, schema)
            serialized = json.dumps(example).lower()
            for forbidden in ("password", "token", "cookie", "nonce", "authorization"):
                self.assertNotIn(forbidden, serialized)

    def test_content_contract_requires_fresh_sync_and_atomic_guard(self) -> None:
        text = read(SKILL_ROOT / "references" / "content-as-code-and-concurrency.md")
        for marker in (
            "wp-content-sync pull",
            "--verify-remote",
            "wp-content-sync status",
            "wp-content-sync diff",
            "wp-content-sync apply",
            "--expected-remote-sha256",
            "--expected-remote-revision",
            "--require-atomic-check",
            "fresh remote sync/check immediately before every write",
            "atomic-compare-and-swap",
            "best-effort-preflight",
            "the write is `blocked`",
            "raw REST",
            "direct `wp post update`",
            "Merge is not apply",
        ):
            self.assertIn(marker, text)

    def test_site_and_surface_contracts_cover_real_management_claims(self) -> None:
        site = read(SKILL_ROOT / "references" / "site-management.md")
        surfaces = read(SKILL_ROOT / "references" / "surfaces-and-evidence.md")
        browser = read(SKILL_ROOT / "references" / "browser-and-private-pages.md")
        for marker in (
            "Page, post, CPT",
            "Menu, navigation",
            "Media and source assets",
            "Themes, templates, and blocks",
            "Forms, SEO, privacy, and operations",
            "stable object ID",
            "desktop/mobile",
        ):
            self.assertIn(marker, site)
        for marker in (
            "REST",
            "WP-CLI/SSH/container",
            "Authenticated admin/CDP",
            "Logged-out browser",
            "blocked",
            "API success",
        ):
            self.assertIn(marker, surfaces)
        for marker in ("ERR_BLOCKED_BY_CLIENT", "private", "logged-out", "console/network"):
            self.assertIn(marker, browser)

    def test_router_and_onboarding_route_project_composition(self) -> None:
        router = read(CENTRAL_ROUTER)
        onboarding = read(CENTRAL_ONBOARDING)
        for text in (router, onboarding):
            self.assertIn("wordpress-project-management", text)
        self.assertIn("cross-surface WordPress projects", router)
        self.assertIn("content-as-code synchronization", router)
        self.assertIn("Strict writes use the optional bundled Git Sync helper", onboarding)
        self.assertIn("29 components", onboarding)

    def test_prompt_fixture_matrix_has_required_routes_and_markers(self) -> None:
        cases = json.loads(
            read(ROOT / "tests" / "fixtures" / "wordpress_project_management_cases.json")
        )
        skill_text = read(SKILL_ROOT / "SKILL.md")
        all_references = "\n".join(
            read(path) for path in (SKILL_ROOT / "references").glob("*.md")
        )
        self.assertGreaterEqual(len(cases), 8)
        self.assertEqual({case["name"] for case in cases}, {
            "plan-only-project",
            "content-as-code-page",
            "theme-and-navigation",
            "runtime-and-plugin",
            "stale-remote-conflict",
            "blocked-browser",
            "integration-lifecycle",
            "release-boundary",
        })
        for case in cases:
            self.assertIn("wordpress-project-management", case["required_composition"])
            for marker in case["required_markers"]:
                self.assertIn(marker, skill_text + "\n" + all_references, case["name"])
            for composition in case["required_composition"]:
                if composition != "wordpress-project-management":
                    self.assertIn(composition, skill_text + "\n" + all_references, case["name"])


if __name__ == "__main__":
    unittest.main()
