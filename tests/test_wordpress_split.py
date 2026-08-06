from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "plugins" / "wordpress-content"
DEVOPS = ROOT / "plugins" / "wordpress-devops"
CENTRAL = ROOT / "plugins" / "amsoft-agentic-workflows"
ROUTER = CENTRAL / "skills" / "amsoft-agentic-workflows" / "SKILL.md"
ONBOARDING = (
    CENTRAL / "skills" / "amsoft-agentic-workflows" / "references" / "onboarding.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class WordPressSplitTests(unittest.TestCase):
    def test_two_standalone_packages_are_cataloged(self) -> None:
        catalog = yaml.safe_load(read(ROOT / "catalog" / "plugins-v1.yaml"))
        packages = {package["name"]: package for package in catalog["packages"]}
        marketplace = json.loads(read(ROOT / ".agents" / "plugins" / "marketplace.json"))

        self.assertEqual(packages["wordpress-content"]["path"], "plugins/wordpress-content")
        self.assertEqual(packages["wordpress-devops"]["path"], "plugins/wordpress-devops")
        self.assertEqual(
            packages["wordpress-content"]["skills"],
            [{"name": "wordpress-content-management", "agent_metadata": "required"}],
        )
        self.assertEqual(
            packages["wordpress-devops"]["skills"],
            [{"name": "wordpress-devops-management", "agent_metadata": "required"}],
        )
        names = [entry["name"] for entry in marketplace["plugins"]]
        self.assertIn("wordpress-content", names)
        self.assertIn("wordpress-devops", names)

    def test_content_contract_is_secret_free_and_content_only(self) -> None:
        manifest = json.loads(read(CONTENT / ".codex-plugin" / "plugin.json"))
        skill = read(CONTENT / "skills" / "wordpress-content-management" / "SKILL.md")
        contract = json.loads(read(CONTENT / "examples" / "content-auth-contract-v1.json"))
        schema = json.loads(
            read(CONTENT / "schemas" / "content-auth-contract-v1.schema.json")
        )

        jsonschema.validate(contract, schema)
        self.assertEqual(manifest["name"], "wordpress-content")
        self.assertEqual(manifest["interface"]["displayName"], "WordPress Content")
        for marker in (
            "pages, posts",
            "design systems and tokens",
            "images, media, videos",
            "Application Password",
            "macOS",
            "Keychain",
            "credential_ref",
            "project-specific contract",
            "Content does not update",
            "do not create a",
            "wordpress-devops-management",
        ):
            self.assertIn(marker, skill)
        self.assertNotIn("application_password_value", json.dumps(contract))

    def test_devops_contract_is_provider_ssh_iac_and_not_content(self) -> None:
        manifest = json.loads(read(DEVOPS / ".codex-plugin" / "plugin.json"))
        skill = read(DEVOPS / "skills" / "wordpress-devops-management" / "SKILL.md")
        contract = json.loads(read(DEVOPS / "examples" / "devops-target-contract-v1.json"))
        schema = json.loads(
            read(DEVOPS / "schemas" / "devops-target-contract-v1.schema.json")
        )

        jsonschema.validate(contract, schema)
        self.assertEqual(manifest["name"], "wordpress-devops")
        self.assertEqual(manifest["interface"]["displayName"], "WordPress DevOps")
        for marker in (
            "Railway",
            "DigitalOcean",
            "SSH",
            "WP-CLI",
            "plugin and theme lifecycle",
            "filesystem",
            "infrastructure-as-code",
            "versioned source",
            "commit",
            "rollback",
            "wordpress-content-management",
        ):
            self.assertIn(marker, skill)
        for forbidden in (
            "edit a page",
            "mutate a page",
            "mutate a post",
            "media object",
        ):
            self.assertNotIn(forbidden, skill)
        self.assertNotIn("private_key", json.dumps(contract))

    def test_central_router_selects_one_or_both(self) -> None:
        router = read(ROUTER)
        onboarding = read(ONBOARDING)
        for text in (router, onboarding):
            self.assertIn("WordPress Content", text)
            self.assertIn("WordPress DevOps", text)
            self.assertIn("amsoft-wordpress-content-management", text)
            self.assertIn("amsoft-wordpress-devops-management", text)
        self.assertIn("use both `amsoft-wordpress-content-management` and", router)
        self.assertIn("26 components", onboarding)
        project = read(CENTRAL / "skills" / "wordpress-project-management" / "SKILL.md")
        seo = read(CENTRAL / "skills" / "amsoft-wordpress-seo-management" / "SKILL.md")
        for text in (project, seo):
            self.assertIn("amsoft-wordpress-content-management", text)
            self.assertIn("amsoft-wordpress-devops-management", text)
            self.assertNotIn("`wordpress-content-management`", text)
            self.assertNotIn("`wordpress-devops-management`", text)

    def test_generated_central_mirrors_preserve_contracts_with_namespace(self) -> None:
        content = CENTRAL / "skills" / "amsoft-wordpress-content-management"
        devops = CENTRAL / "skills" / "amsoft-wordpress-devops-management"
        self.assertEqual(
            {
                path.relative_to(CONTENT / "skills" / "wordpress-content-management")
                for path in (CONTENT / "skills" / "wordpress-content-management").rglob("*")
                if path.is_file()
                and path.name not in {"SKILL.md", "openai.yaml"}
            },
            {
                path.relative_to(content)
                for path in content.rglob("*")
                if path.is_file() and path.name not in {"SKILL.md", "openai.yaml"}
            },
        )
        self.assertEqual(
            {
                path.relative_to(DEVOPS / "skills" / "wordpress-devops-management")
                for path in (DEVOPS / "skills" / "wordpress-devops-management").rglob("*")
                if path.is_file()
                and path.name not in {"SKILL.md", "openai.yaml"}
            },
            {
                path.relative_to(devops)
                for path in devops.rglob("*")
                if path.is_file() and path.name not in {"SKILL.md", "openai.yaml"}
            },
        )
        self.assertIn("name: amsoft-wordpress-content-management", read(content / "SKILL.md"))
        self.assertIn("name: amsoft-wordpress-devops-management", read(devops / "SKILL.md"))
        content_text = "\n".join(read(path) for path in content.rglob("*") if path.is_file())
        devops_text = "\n".join(read(path) for path in devops.rglob("*") if path.is_file())
        self.assertIn("`amsoft-wordpress-content-management`", content_text)
        self.assertIn("`amsoft-wordpress-devops-management`", content_text)
        self.assertNotIn("`wordpress-content-management`", content_text)
        self.assertNotIn("`wordpress-devops-management`", content_text)
        self.assertIn("`amsoft-wordpress-content-management`", devops_text)
        self.assertIn("`amsoft-wordpress-devops-management`", devops_text)
        self.assertNotIn("`wordpress-content-management`", devops_text)
        self.assertNotIn("`wordpress-devops-management`", devops_text)


if __name__ == "__main__":
    unittest.main()
