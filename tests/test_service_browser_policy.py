"""Guard connected-provider routing and the boundary with local/runtime configuration."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/agentic-workflows/skills"
GUIDE = SKILLS / "agentic-workflows/references/service-browser-operations.md"
SERVICES = {
    "supabase-cli": "Supabase",
    "railway-account-operations": "Railway",
    "cloudflare-account-operations": "Cloudflare",
    "digitalocean-account-operations": "DigitalOcean",
    "vercel-account-operations": "Vercel",
}
RETIRED_HELPERS = {
    "copy_openrouter_key.py", "cloudflare_api.py", "cloudflare_configure_credentials.py",
    "digitalocean_cli.py", "digitalocean_configure_credentials.py", "railway_cli.py",
    "railway_configure_credentials.py",
}


class ServiceChannelPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        cls.package = cls.catalog["packages"][0]
        cls.contract = " ".join(GUIDE.read_text().split())

    def test_provider_prerequisites_require_connections_without_cli_auth_setup(self) -> None:
        for name, provider in SERVICES.items():
            skill = next(s for s in self.package["skills"] if s["name"] == name)
            with self.subTest(skill=name):
                required = [p for p in skill["prerequisites"] if p["required"]]
                connection = next(p for p in skill["prerequisites"] if p["name"] == f"Connected {provider} app")
                if name == "supabase-cli":
                    self.assertEqual(required, [])
                    self.assertIn("Required for remote operations only", connection["setup"])
                else:
                    self.assertEqual(required, [connection])
                self.assertIn("Codex", connection["setup"])
                self.assertNotIn("Authenticated service CLI", str(skill["prerequisites"]))

    def test_skill_entrypoints_and_prompts_reuse_codex_connections(self) -> None:
        for name in SERVICES:
            with self.subTest(skill=name):
                text = (SKILLS / name / "SKILL.md").read_text()
                self.assertIn("plugin/connected app", text)
                self.assertIn("Codex", text)
                prompt = yaml.safe_load((SKILLS / name / "agents/openai.yaml").read_text())["interface"]["default_prompt"]
                self.assertIn("plugin/connected app", prompt)
                self.assertIn("Codex", prompt)

    def test_connection_recovery_and_permission_gaps_do_not_provision_tokens(self) -> None:
        for phrase in (
            "Codex owns connector authentication",
            "before provider skill or tool discovery",
            "never infer that a connection or operation exists",
            "Verify connected identity/scope and the exact target",
            "Recover a missing, expired, or mismatched connection through Codex",
            "report that exact blocker and continue independent work",
            "Do not provision local CLI tokens, extract connector credentials",
            "or switch to dashboard management as an automatic fallback",
            "Permission denial cannot be bypassed",
            "On unknown write outcome, read back before retrying",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.contract)
        for provider in (*SERVICES.values(), "PostHog", "Polar"):
            self.assertIn(provider, self.contract)

    def test_local_development_and_runtime_secrets_do_not_replace_connector_auth(self) -> None:
        self.assertIn("Local-only tools", self.contract)
        self.assertIn("must not become authenticated account-management fallbacks", self.contract)
        self.assertIn("Application SDKs, database connections, event capture, webhooks", self.contract)
        supabase = (SKILLS / "supabase-cli/SKILL.md").read_text()
        self.assertIn("## Local development", supabase)
        self.assertIn("Remote login\nis not a prerequisite for local-only work", supabase)
        bootstrap = " ".join((SKILLS / "standard-development-workflow/references/worktree-bootstrap.md").read_text().split())
        self.assertIn("Exclude agent authentication stores before inventory or copy", bootstrap)
        self.assertIn("required application env/config files", bootstrap)
        self.assertIn("does not create a separate remote target", bootstrap)

    def test_retired_token_helpers_are_not_shipped_or_referenced(self) -> None:
        for name in RETIRED_HELPERS:
            with self.subTest(helper=name):
                self.assertFalse((ROOT / "plugins/agentic-workflows/scripts" / name).exists())
                self.assertNotIn("scripts/" + name, self.package["executables"])
        for base in (SKILLS, ROOT / "plugins/agentic-workflows/scripts"):
            for path in base.rglob("*"):
                if path.suffix not in {".md", ".py", ".yaml"}:
                    continue
                text = path.read_text()
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn(".cli/", text)
                    self.assertNotIn("project-local-cli-credentials", text)
                    for name in RETIRED_HELPERS:
                        self.assertNotIn(name, text)

    def test_provider_runbooks_link_the_single_channel_owner(self) -> None:
        for name in SERVICES:
            for path in (SKILLS / name).rglob("*.md"):
                for link in re.findall(r"\]\(([^)#]+service-browser-operations\.md)(?:#[^)]+)?\)", path.read_text()):
                    with self.subTest(path=path.relative_to(ROOT)):
                        self.assertEqual((path.parent / link).resolve(), GUIDE.resolve())


if __name__ == "__main__":
    unittest.main()
