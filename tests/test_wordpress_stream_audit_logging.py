from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "amsoft-agentic-workflows"
SKILL = PLUGIN / "skills" / "wordpress-stream-audit-logging"
ROUTER = PLUGIN / "skills" / "amsoft-agentic-workflows" / "SKILL.md"
ONBOARDING = (
    PLUGIN
    / "skills"
    / "amsoft-agentic-workflows"
    / "references"
    / "onboarding.md"
)


class WordPressStreamAuditLoggingTests(unittest.TestCase):
    def test_skill_is_cataloged_and_discoverable(self) -> None:
        catalog = yaml.safe_load(
            (ROOT / "catalog" / "plugins-v1.yaml").read_text(encoding="utf-8")
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        declared = {entry["name"]: entry for entry in central["skills"]}
        self.assertEqual(
            declared["wordpress-stream-audit-logging"]["agent_metadata"],
            "required",
        )

        metadata = yaml.safe_load(
            (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )
        self.assertIn(
            "$wordpress-stream-audit-logging",
            metadata["interface"]["default_prompt"],
        )

    def test_skill_has_no_executable_or_bundled_stream_payload(self) -> None:
        self.assertFalse((SKILL / "scripts").exists())
        self.assertFalse((SKILL / "assets").exists())
        self.assertFalse(any(path.suffix in {".php", ".zip"} for path in SKILL.rglob("*")))

        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertIn("stream", manifest["keywords"])
        self.assertIn("audit-logging", manifest["keywords"])

    def test_policy_and_safety_contracts_are_explicit(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        policy = (SKILL / "references" / "policy-and-data-handling.md").read_text(
            encoding="utf-8"
        )
        verification = (
            SKILL
            / "references"
            / "installation-configuration-verification.md"
        ).read_text(encoding="utf-8")
        rollback = (
            SKILL / "references" / "release-rollback-and-incidents.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "optional application layer",
            "90-day live retention",
            "administrator-only access",
            "no outbound integrations",
            "no AI/MCP access",
            "Never trust raw `HTTP_*` forwarded headers",
        ):
            self.assertIn(marker, skill)

        for marker in (
            "Audit-log retention and backup retention are different",
            "Abilities API",
            "MCP Adapter",
            "potentially sensitive",
        ):
            self.assertIn(marker, policy)

        for marker in (
            "Plugin activation is insufficient",
            "guaranteed cleanup",
            "structural/read-only",
            "Stop on an unexpected option shape",
        ):
            self.assertIn(marker, verification)

        for marker in (
            "Do not use uninstall",
            "Do not delete records",
            "destructive data-removal proposal",
            "explicit authorization.",
        ):
            self.assertIn(marker, rollback)

    def test_router_and_onboarding_expose_the_optional_layer(self) -> None:
        router = ROUTER.read_text(encoding="utf-8")
        onboarding = ONBOARDING.read_text(encoding="utf-8")
        for text in (router, onboarding):
            self.assertIn("WordPress Stream Audit Logging", text)
            self.assertIn("wordpress-stream-audit-logging", text)
        self.assertIn("Load only the layers the request needs", router)
        self.assertIn("Explain the 24 components", onboarding)


if __name__ == "__main__":
    unittest.main()
