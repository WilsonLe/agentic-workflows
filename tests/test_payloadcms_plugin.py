from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agentic-workflows"
SKILL = PLUGIN / "skills" / "payloadcms-development"


class PayloadCMSPluginTests(unittest.TestCase):
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
            "${TMPDIR:-/tmp}/payloadcms-compose-test.lock",
            "Never delete a lock solely because it",
            "Build the application image before starting Postgres",
            "no database connection, database credentials, migration command, seed, or",
        ):
            self.assertIn(marker, skill)

        for marker in (
            "All test layers run through Docker Compose with a production-built application image",
            "exactly one Payload Compose test stack may be running at a time",
            "atomic host-wide lock",
            'mkdir "${TMPDIR:-/tmp}/payloadcms-compose-test.lock"',
            "docker compose down --volumes --remove-orphans",
            "do not automatically remove a lock based on age",
            'docker compose --project-name \"$project\" build app',
            "before Postgres starts",
        ):
            self.assertIn(marker, normalized_testing)

    def test_catalog_and_router_expose_payloadcms(self) -> None:
        catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        skill = next(item for item in package["skills"] if item["name"] == "payloadcms-development")
        self.assertEqual(skill["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertIn("`payloadcms-development`", (PLUGIN / "skills/agentic-workflows/SKILL.md").read_text())
        self.assertIn("$payloadcms-development", (SKILL / "agents/openai.yaml").read_text())


if __name__ == "__main__":
    unittest.main()
