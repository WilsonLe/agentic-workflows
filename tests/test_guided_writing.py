from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "guided-writing"
SKILL = PLUGIN / "skills" / "guided-writing-coach"
CENTRAL = ROOT / "plugins" / "agentic-workflows"
CENTRAL_SKILL = CENTRAL / "skills" / "guided-writing-coach"


class GuidedWritingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = yaml.safe_load(
            (ROOT / "catalog" / "plugins-v2.yaml").read_text(encoding="utf-8")
        )
        self.scenarios = json.loads(
            (SKILL / "examples" / "conversation-scenarios.json").read_text(
                encoding="utf-8"
            )
        )["scenarios"]

    def test_manifest_catalog_and_marketplace_order_register_package(self) -> None:
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        package = next(
            package
            for package in self.catalog["packages"]
            if package["name"] == "guided-writing"
        )
        order = self.catalog["marketplace"]["plugin_order"]

        self.assertEqual(manifest["name"], "guided-writing")
        self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(manifest["interface"]["displayName"], "Guided Writing Coach")
        self.assertEqual(package["path"], "plugins/guided-writing")
        self.assertEqual(package["runtime_dependencies"], [])
        self.assertEqual(package["executables"], [])
        self.assertEqual(
            package["skills"],
            [{"name": "guided-writing-coach", "agent_metadata": "required", "harnesses": ["codex", "claude-code"], "prerequisites": []}],
        )
        self.assertEqual(
            order.index("guided-writing"),
            order.index("literature-review") + 1,
        )

    def test_instruction_contract_preserves_user_authorship_and_fit_gate(self) -> None:
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        loop = (SKILL / "references" / "coaching-loop.md").read_text(
            encoding="utf-8"
        )
        fit = (SKILL / "references" / "fit-and-feedback.md").read_text(
            encoding="utf-8"
        )
        integrity = (
            SKILL / "references" / "authorship-and-integrity.md"
        ).read_text(encoding="utf-8")
        combined = "\n".join((skill, loop, fit, integrity))

        for marker in (
            "outline",
            "detailed reference",
            "one paragraph at a time",
            "only wording the user contributed",
            "Append a new contribution verbatim",
            "Apply it only after explicit approval",
            "Fits original idea: yes",
            "Paragraph role",
            "Semantic coverage",
            "Factual and citation accuracy",
            "No contradiction",
            "Audience coherence",
            "ask exactly one question",
            "explicit acceptance",
            "Humanizer",
            "Academic Writing",
            "detector-evasion",
            "cannot prove who authored",
        ):
            self.assertIn(marker, combined)

    def test_conversation_fixtures_compile_only_exact_user_contributions(self) -> None:
        for scenario in self.scenarios:
            turns = {turn["id"]: turn for turn in scenario["user_turns"]}
            turn_positions = {
                turn["id"]: position
                for position, turn in enumerate(scenario["user_turns"])
            }
            for check in scenario["coach_checks"]:
                source_ids = check["source_user_turn_ids"]
                expected = " ".join(turns[turn_id]["text"] for turn_id in source_ids)
                self.assertEqual(
                    check["working_paragraph"],
                    expected,
                    msg=f"{scenario['id']} contains non-user wording",
                )
                self.assertTrue(
                    all(
                        turns[turn_id]["kind"]
                        in {"contribution", "complete_replacement"}
                        for turn_id in source_ids
                    )
                )

                chronological = sorted(source_ids, key=turn_positions.__getitem__)
                if source_ids != chronological:
                    after_position = turn_positions[check["after"]]
                    approvals = [
                        turn
                        for turn in scenario["user_turns"][: after_position + 1]
                        if turn["kind"] == "edit_approval"
                        and turn.get("approved_order") == source_ids
                    ]
                    self.assertTrue(
                        approvals,
                        msg=f"{scenario['id']} reorders prose without approval",
                    )

    def test_fit_yes_requires_complete_idea_and_exact_term_coverage(self) -> None:
        for scenario in self.scenarios:
            turns = {turn["id"]: turn for turn in scenario["user_turns"]}
            required_ideas = set(scenario["required_ideas"])
            for check in scenario["coach_checks"]:
                covered = {
                    idea
                    for turn_id in check["source_user_turn_ids"]
                    for idea in turns[turn_id]["covers"]
                }
                terms_present = all(
                    term in check["working_paragraph"]
                    for term in scenario["required_exact_terms"]
                )
                complete = required_ideas <= covered and terms_present
                self.assertEqual(
                    check["fits_original_idea"] == "yes",
                    complete,
                    msg=f"{scenario['id']} has an invalid fit decision",
                )
                self.assertEqual(check["missing"] == [], complete)

    def test_replacement_and_boundary_scenarios_are_explicit(self) -> None:
        by_id = {scenario["id"]: scenario for scenario in self.scenarios}
        replacement = by_id["complete_user_replacement"]
        final_check = replacement["coach_checks"][-1]

        self.assertEqual(final_check["source_user_turn_ids"], ["u2"])
        self.assertNotIn(
            replacement["user_turns"][0]["text"], final_check["working_paragraph"]
        )
        self.assertEqual(by_id["missing_outline"]["expected_action"], "request_outline")
        self.assertEqual(
            by_id["missing_detailed_reference"]["expected_action"],
            "request_detailed_reference",
        )
        self.assertEqual(
            by_id["academic_policy_unknown"]["expected_action"],
            "ask_for_policy_and_limit_to_permitted_support",
        )
        self.assertEqual(
            by_id["detector_evasion_request"]["expected_action"],
            "refuse_detector_evasion_and_offer_integrity_preserving_coaching",
        )

    def test_central_mirror_is_namespaced_and_instruction_only(self) -> None:
        central = next(
            package
            for package in self.catalog["packages"]
            if package["name"] == "agentic-workflows"
        )
        mirrors = {mirror["name"] for mirror in self.catalog["mirrors"]}
        source_metadata = (SKILL / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        central_metadata = (CENTRAL_SKILL / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        router = (
            CENTRAL / "skills" / "agentic-workflows" / "SKILL.md"
        ).read_text(encoding="utf-8")
        onboarding = (
            CENTRAL
            / "skills"
            / "agentic-workflows"
            / "references"
            / "onboarding.md"
        ).read_text(encoding="utf-8")
        registry = (
            CENTRAL
            / "skills"
            / "agentic-workflows"
            / "references"
            / "plugin-registry.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "guided-writing-coach",
            {skill["name"] for skill in central["skills"]},
        )
        self.assertIn("guided-writing-skill", mirrors)
        self.assertIn("$guided-writing-coach", source_metadata)
        self.assertIn("$guided-writing-coach", central_metadata)
        self.assertIn("`guided-writing-coach`", router)
        self.assertIn("Prerequisites", onboarding)
        self.assertIn("| `guided-writing` | Guided Writing Coach |", registry)
        self.assertEqual(
            (CENTRAL_SKILL / "references" / "coaching-loop.md").read_bytes(),
            (SKILL / "references" / "coaching-loop.md").read_bytes(),
        )
        self.assertEqual(
            (CENTRAL_SKILL / "examples" / "conversation-scenarios.json").read_bytes(),
            (SKILL / "examples" / "conversation-scenarios.json").read_bytes(),
        )

        for root in (PLUGIN, CENTRAL_SKILL):
            self.assertFalse((root / "scripts").exists())
            self.assertFalse((root / "schemas").exists())
            self.assertFalse(
                any(path.suffix in {".py", ".js", ".mjs", ".ts"} for path in root.rglob("*"))
            )


if __name__ == "__main__":
    unittest.main()
