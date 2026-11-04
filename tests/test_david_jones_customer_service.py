from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/agentic-workflows"
SKILL = PLUGIN / "skills/david-jones-till-sales"


class DavidJonesCustomerServiceTests(unittest.TestCase):
    def test_catalog_registers_the_portable_till_skill(self) -> None:
        catalog = yaml.safe_load((ROOT / "catalog/plugins-v2.yaml").read_text())
        package, = catalog["packages"]
        skill = next(item for item in package["skills"] if item["name"] == "david-jones-till-sales")
        self.assertEqual(skill["harnesses"], ["codex", "claude-code", "opencode"])
        self.assertEqual(catalog["marketplace"]["plugin_order"], ["agentic-workflows"])
        self.assertIn("$david-jones-till-sales", (SKILL / "agents/openai.yaml").read_text())

    def test_till_sale_preserves_ordered_customer_service_contract(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
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



if __name__ == "__main__":
    unittest.main()
