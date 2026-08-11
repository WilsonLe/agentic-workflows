from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "payloadcms"
SKILL = PLUGIN / "skills" / "payloadcms-development"
CENTRAL_SKILL = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "amsoft-payloadcms-development"
)


class PayloadCMSPluginTests(unittest.TestCase):
    def test_manifest_exposes_the_payloadcms_workflow(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "payloadcms")
        self.assertEqual(manifest["license"], "LicenseRef-AMSoft-Proprietary")
        self.assertEqual(manifest["interface"]["category"], "Developer")
        self.assertEqual(
            manifest["interface"]["capabilities"],
            ["Interactive", "Read", "Write", "Research"],
        )
        self.assertIn("migrations", manifest["keywords"])
        self.assertIn("playwright", manifest["keywords"])

    def test_skill_requires_prompt_safe_reversible_migrations(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "short initial tool wait",
            "same process/session alive",
            "--skip-empty",
            "never start concurrent generators",
            "migrate:down",
            "second up must work",
            "disposable database",
        ):
            self.assertIn(marker, text)

        migrations = (SKILL / "references" / "postgres-migrations.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "generated `up` and `down`",
            "migrate:status",
            "Do not retry while another",
            "generator is live",
            "never point this sequence at production",
        ):
            self.assertIn(marker, migrations)

    def test_configuration_components_and_access_are_documented(self) -> None:
        config = (SKILL / "references" / "configuration-and-components.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "CollectionConfig",
            "GlobalConfig",
            "buildConfig",
            "React Server Components",
            "'use client'",
            "Payload plugin",
        ):
            self.assertIn(marker, config)

        access = (SKILL / "references" / "access-control.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "default-deny",
            "query constraint",
            "Field access",
            "overrideAccess",
            "directly",
        ):
            self.assertIn(marker, access)

    def test_three_layer_testing_contract_is_explicit(self) -> None:
        text = (SKILL / "references" / "testing.md").read_text(encoding="utf-8")
        for marker in (
            "## Unit tests",
            "## Integration tests",
            "## Playwright E2E tests",
            "web-first assertions",
            "up/down/up database round trip",
            "role, label, text",
        ):
            self.assertIn(marker, text)

    def test_worktree_compose_contract_serializes_production_test_stacks(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        testing = (SKILL / "references" / "testing.md").read_text(encoding="utf-8")
        normalized_testing = " ".join(testing.split())
        for marker in (
            "Every Payload test run must use Docker Compose and a production application build",
            "Each worktree owns a separate Compose project",
            "Only one local Payload Compose test stack may run on a host at a time",
            "${TMPDIR:-/tmp}/amsoft-payloadcms-compose-test.lock",
            "Never delete a lock solely because it",
            "Build the application image before starting Postgres",
            "no database connection, database credentials, migration command, seed, or",
        ):
            self.assertIn(marker, skill)

        for marker in (
            "All test layers run through Docker Compose with a production-built application image",
            "exactly one Payload Compose test stack may be running at a time",
            "atomic host-wide lock",
            'mkdir "${TMPDIR:-/tmp}/amsoft-payloadcms-compose-test.lock"',
            "docker compose down --volumes --remove-orphans",
            "do not automatically remove a lock based on age",
            'docker compose --project-name \"$project\" build app',
            "before Postgres starts",
        ):
            self.assertIn(marker, normalized_testing)

    def test_catalog_registry_and_central_mirror_are_declared(self) -> None:
        catalog = yaml.safe_load(
            (ROOT / "catalog" / "plugins-v1.yaml").read_text(encoding="utf-8")
        )
        package = next(
            package for package in catalog["packages"] if package["name"] == "payloadcms"
        )
        self.assertEqual(
            [skill["name"] for skill in package["skills"]],
            ["payloadcms-development"],
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        self.assertIn(
            "amsoft-payloadcms-development",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn(
            "payloadcms-skill", {mirror["name"] for mirror in catalog["mirrors"]}
        )
        self.assertIn(
            "`amsoft-payloadcms-development`",
            (
                ROOT
                / "plugins"
                / "amsoft-agentic-workflows"
                / "skills"
                / "amsoft-agentic-workflows"
                / "SKILL.md"
            ).read_text(encoding="utf-8"),
        )

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


if __name__ == "__main__":
    unittest.main()
