"""Guard authenticated CLI defaults and browser authentication/fallback boundaries."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "plugins/agentic-workflows/skills/agentic-workflows/references/service-browser-operations.md"
SERVICE_SKILLS = {
    "supabase-cli",
    "railway-account-operations",
    "cloudflare-account-operations",
    "digitalocean-account-operations",
}


class ServiceChannelPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        cls.contract = GUIDE.read_text()
        cls.normalized = " ".join(cls.contract.split())

    def test_every_service_requires_authenticated_client_for_remote_operations(self) -> None:
        found = set()
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                found.add(skill["name"])
                with self.subTest(package=package["name"], skill=skill["name"]):
                    clients = [p for p in skill["prerequisites"] if p["name"] == "Authenticated service CLI"]
                    self.assertEqual(len(clients), 1)
                    self.assertTrue(clients[0]["required"])
                    self.assertIn("verify authentication", clients[0]["setup"])
                    self.assertIn("account/target", clients[0]["setup"])
                    browsers = [p for p in skill["prerequisites"] if p["name"] == "Browser authentication assistance"]
                    self.assertEqual(len(browsers), 1)
                    self.assertFalse(browsers[0]["required"])
                    self.assertIn("return to CLI verification", browsers[0]["setup"])
                    self.assertIn("authenticated CLI capability gap", browsers[0]["setup"])
        self.assertEqual(found, SERVICE_SKILLS)

    def test_entrypoints_and_prompts_select_authenticated_cli(self) -> None:
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                path = ROOT / package["path"] / "skills" / skill["name"] / "SKILL.md"
                with self.subTest(path=path.relative_to(ROOT)):
                    text = path.read_text()
                    self.assertIn("references/service-browser-operations.md", text)
                    self.assertIn("Default to a supported authenticated CLI", text)
                    self.assertNotIn("Browser operation is the base", text)
                    metadata = yaml.safe_load((path.parent / "agents/openai.yaml").read_text())
                    prompt = metadata["interface"]["default_prompt"].lower()
                    self.assertIn("authenticated cli", prompt)
                    self.assertIn("browser", prompt)

    def test_missing_authentication_returns_to_cli_instead_of_browser_management(self) -> None:
        for guard in (
            "Check existing CLI authentication read-only",
            "Reuse valid credentials only when authenticated identity and exact target match",
            "If authentication is missing, expired, or for the wrong account",
            "then return to the CLI and verify again",
            "Do not use browser management merely because the CLI is unauthenticated",
            "Login success or key creation alone is insufficient",
            "On mismatch or unknown identity/scope, stop dependent operations",
            "validated concealed transfer",
            "private password entry, MFA, CAPTCHA",
            "Never extract cookies, passwords, browser storage, or sessions",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, self.normalized)

    def test_browser_fallback_requires_supported_cli_capability_failure(self) -> None:
        for guard in (
            "Use browser service operations only when the authenticated CLI cannot perform",
            "Do not execute a mutation just to test support",
            "Permission denials cannot be bypassed",
            "Record the unsupported operation",
            "same verified account, project, and resource",
            "Existing operation authority covers the fallback",
            "Return to the CLI for later supported actions",
            "If an outcome is unknown, read back before retrying",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, self.normalized)

    def test_vercel_uses_connected_app_and_excludes_local_credentials(self) -> None:
        skill = next(s for s in self.catalog["packages"][0]["skills"] if s["name"] == "vercel-account-operations")
        self.assertEqual([p["name"] for p in skill["prerequisites"]], ["Connected Vercel app"])
        root = ROOT / "plugins/agentic-workflows/skills"
        vercel = root / "vercel-account-operations"
        entry = (vercel / "SKILL.md").read_text()
        self.assertIn("Always use the Vercel plugin/connected app through Codex", entry)
        self.assertIn("Missing connection", self.contract)
        prompt = yaml.safe_load((vercel / "agents/openai.yaml").read_text())["interface"]["default_prompt"]
        self.assertIn("plugin/connected app in Codex", prompt)
        for path in vercel.rglob("*.md"):
            text = path.read_text()
            self.assertNotIn("VERCEL_TOKEN_STORAGE", text)
            self.assertNotIn("--global-config", text)
            self.assertNotIn("vercel whoami", text)
        for path in root.rglob("task-authority-and-secrets.md"):
            self.assertNotIn("| Vercel |", path.read_text())
        bootstrap = (root / "standard-development-workflow/references/worktree-bootstrap.md").read_text()
        self.assertIn("exclude Vercel authentication files", bootstrap)

    def test_all_provider_runbooks_share_the_channel_contract(self) -> None:
        covered = set()
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                path = ROOT / package["path"] / "skills" / skill["name"] / "SKILL.md"
                with self.subTest(path=path.relative_to(ROOT)):
                    target = re.search(r"\]\(([^)]+service-browser-operations\.md)\)", path.read_text())
                    self.assertIsNotNone(target)
                    self.assertEqual((path.parent / target[1]).resolve(), GUIDE.resolve())
                    self.assertFalse((path.parent / "references/browser-selection.md").exists())
                    covered.add(skill["name"])
        self.assertEqual(covered, SERVICE_SKILLS)


if __name__ == "__main__":
    unittest.main()
