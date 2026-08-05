from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "amsoft-agentic-workflows"
CLI_SKILL = PLUGIN / "skills" / "wordpress-cli-operations"


class WordPressFilesystemContractTests(unittest.TestCase):
    def test_filesystem_runbook_is_linked_and_provider_aware(self) -> None:
        runbook = (CLI_SKILL / "references" / "filesystem-and-updates.md").read_text(
            encoding="utf-8"
        )
        skill = (CLI_SKILL / "SKILL.md").read_text(encoding="utf-8")
        site = (
            PLUGIN / "skills" / "wordpress-site-management" / "SKILL.md"
        ).read_text(encoding="utf-8")
        router = (
            PLUGIN / "skills" / "amsoft-agentic-workflows" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "get_filesystem_method()",
            "same numeric UID/GID",
            "direct",
            "ftpsockets",
            "Railway volume",
            "Docker Compose VPS",
            "database backup",
            "0777",
            "FTP passwords",
            "production filesystem mutation",
        ):
            self.assertIn(marker, runbook)

        self.assertIn("filesystem-and-updates.md", skill)
        self.assertIn("Could not access filesystem", site)
        self.assertIn("FTP-credential update prompts", router)

    def test_manifest_advertises_the_capability_and_registry_matches(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertIn("filesystem", manifest["keywords"])
        self.assertIn("file-ownership", manifest["keywords"])
        self.assertIn("ftp-credentials", manifest["keywords"])
        version = manifest["version"]
        registry = (
            PLUGIN
            / "skills"
            / "amsoft-agentic-workflows"
            / "references"
            / "plugin-registry.md"
        ).read_text(encoding="utf-8")
        self.assertIn(f"| `amsoft-agentic-workflows` | AMSoft Agentic Workflows | `{version}` |", registry)


if __name__ == "__main__":
    unittest.main()
