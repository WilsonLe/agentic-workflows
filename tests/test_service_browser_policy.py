"""Guard service routing against mandatory token setup and command-first regressions."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SERVICE_SKILLS = {
    "railway-account-operations",
    "vercel-account-operations",
    "cloudflare-account-operations",
    "digitalocean-account-operations",
    "excalidraw-api-operations",
    "excalidraw-scene-operations",
    "erpnext-operations",
    "erpnext-accounting-finance",
    "erpnext-buying-stock",
    "erpnext-content-analytics",
    "erpnext-manufacturing-assets",
    "erpnext-organization-administration",
    "erpnext-people-projects-support",
    "erpnext-sales-crm",
}


class ServiceBrowserPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        cls.contract = (
            ROOT
            / "plugins/agentic-workflows/skills/agentic-workflows/references"
            / "service-browser-operations.md"
        ).read_text()

    def test_every_service_consumer_can_start_without_provider_credentials(self) -> None:
        found = set()
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                found.add(skill["name"])
                with self.subTest(package=package["name"], skill=skill["name"]):
                    required = [p for p in skill["prerequisites"] if p["required"]]
                    self.assertTrue(any(p["name"] == "Authenticated browser" for p in required))
                    self.assertFalse(any(
                        re.search(r"install|configure.*(?:token|key|API|CLI)", p["setup"], re.I)
                        for p in required
                    ))
                    diagnostics = [p for p in skill["prerequisites"] if p["name"] == "Read-only CLI diagnostics"]
                    self.assertEqual(len(diagnostics), 1)
                    self.assertFalse(diagnostics[0]["required"])
                    self.assertIn("independently matching", diagnostics[0]["setup"])
        self.assertEqual(found, SERVICE_SKILLS)

    def test_service_entrypoints_route_management_to_browser(self) -> None:
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                path = ROOT / package["path"] / "skills" / skill["name"] / "SKILL.md"
                with self.subTest(path=path.relative_to(ROOT)):
                    text = path.read_text()
                    self.assertIn("browser", text.lower())
                    if skill["name"].startswith("erpnext-") and skill["name"] != "erpnext-operations":
                        self.assertIn("`erpnext-operations`", text)
                        self.assertIn("browser management", text)
                    else:
                        self.assertIn("references/browser-selection.md", text)
                    self.assertNotRegex(text, r"Use (?:`railway`|`doctl`|command-line tools) as the execution layer")
                    metadata = yaml.safe_load((path.parent / "agents/openai.yaml").read_text())
                    self.assertIn("browser", metadata["interface"]["default_prompt"].lower())

    def test_management_and_log_scenarios_have_distinct_authority(self) -> None:
        # A request to edit DNS must use UI; asking for service logs must not confer
        # deployment authority; a CLI signed into another account cannot supply proof.
        text = " ".join(self.contract.split())
        for guard in (
            "use the built-in Codex browser",
            "Never choose the first account",
            "Recheck the visible account and exact target immediately before a mutation",
            "Use visible browser controls for account management, creation, updates, deletion",
            "Read-only CLI permission does not authorize CLI writes",
            "On mismatch or unknown scope, stop that diagnostic",
            "does not require an API token, CLI installation, MCP connection",
            "private password entry, MFA, CAPTCHA",
            "reopen or refresh the same resource",
            "If the outcome is unknown, read back before retrying",
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, text)

    def test_provider_runbooks_share_the_service_contract(self) -> None:
        covered = set()
        for package in self.catalog["packages"]:
            for skill in package["skills"]:
                if skill["name"] not in SERVICE_SKILLS:
                    continue
                if skill["name"].startswith("erpnext-") and skill["name"] != "erpnext-operations":
                    continue
                path = ROOT / package["path"] / "skills" / skill["name"] / "references/browser-selection.md"
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertEqual(path.read_text(), self.contract)
                    covered.add(skill["name"])
        self.assertEqual(covered, {n for n in SERVICE_SKILLS if not n.startswith("erpnext-")} | {"erpnext-operations"})


if __name__ == "__main__":
    unittest.main()
