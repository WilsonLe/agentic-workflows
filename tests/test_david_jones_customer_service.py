from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins" / "david-jones-customer-service"
CENTRAL = ROOT / "plugins" / "amsoft-agentic-workflows"
SOURCE_SKILL = SOURCE / "skills" / "david-jones-till-sales" / "SKILL.md"
CENTRAL_SKILL = (
    CENTRAL / "skills" / "amsoft-david-jones-till-sales" / "SKILL.md"
)


class DavidJonesCustomerServiceTests(unittest.TestCase):
    def test_manifest_and_catalog_register_the_source_plugin(self) -> None:
        manifest = json.loads(
            (SOURCE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        catalog = yaml.safe_load(
            (ROOT / "catalog" / "plugins-v1.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["name"], "david-jones-customer-service")
        self.assertEqual(manifest["license"], "LicenseRef-AMSoft-Proprietary")
        package = next(
            package
            for package in catalog["packages"]
            if package["name"] == "david-jones-customer-service"
        )
        self.assertEqual(package["path"], "plugins/david-jones-customer-service")
        self.assertEqual(
            [skill["name"] for skill in package["skills"]],
            ["david-jones-till-sales"],
        )
        self.assertIn(
            "david-jones-customer-service",
            catalog["marketplace"]["plugin_order"],
        )

    def test_till_sale_preserves_ordered_customer_service_contract(self) -> None:
        text = SOURCE_SKILL.read_text(encoding="utf-8")
        required_markers = (
            "Sign in to the authorized till",
            "Do you have your David Jones Rewards card with you?",
            "try the phone number",
            "Scan each item one by one",
            "detagging machine's confirmation beep",
            "Press **Total**",
            "**Card / EFTPOS — No Cash**",
            "**Continue** button",
            "Would you like a bag?",
            "Fold the receipt in half",
            "Have a good day.",
        )
        positions = [text.index(marker) for marker in required_markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("never ask for, repeat, record, or store either credential", text)
        self.assertIn("retain a phone number in notes", text)
        self.assertIn("uncertain result", text)
        self.assertIn("does not cover cash, refunds, returns, exchanges", text)

    def test_central_skill_is_namespaced_and_mirror_is_cataloged(self) -> None:
        central_text = CENTRAL_SKILL.read_text(encoding="utf-8")
        central_metadata = (
            CENTRAL
            / "skills"
            / "amsoft-david-jones-till-sales"
            / "agents"
            / "openai.yaml"
        ).read_text(encoding="utf-8")
        catalog = yaml.safe_load(
            (ROOT / "catalog" / "plugins-v1.yaml").read_text(encoding="utf-8")
        )
        central = next(
            package
            for package in catalog["packages"]
            if package["name"] == "amsoft-agentic-workflows"
        )
        mirror_names = {mirror["name"] for mirror in catalog["mirrors"]}

        self.assertIn("amsoft-david-jones-till-sales", central_text)
        self.assertNotIn("$david-jones-till-sales", central_text)
        self.assertIn("$amsoft-david-jones-till-sales", central_metadata)
        self.assertIn(
            "amsoft-david-jones-till-sales",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn("david-jones-customer-service-skill", mirror_names)


if __name__ == "__main__":
    unittest.main()
