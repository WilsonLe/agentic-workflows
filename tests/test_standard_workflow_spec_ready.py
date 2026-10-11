from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "plugins/agentic-workflows/skills/standard-development-workflow"
SPEC_READY = (
    ROOT
    / "plugins"
    / "agentic-workflows"
    / "skills"
    / "standard-development-workflow"
    / "references"
    / "spec-ready.md"
)


class StandardWorkflowSpecReadyTests(unittest.TestCase):
    def test_preimplementation_stages_have_distinct_ordered_contracts(self) -> None:
        stages = (SKILL_ROOT / "references/stage-contracts.md").read_text()
        headers = [line for line in stages.splitlines() if line.startswith("## Stage ")]
        self.assertEqual(headers, [
            "## Stage 1 — Isolated worktree ready",
            "## Stage 2 — Grill Me and spec-ready issue",
            "## Stage 3 — Planning",
            "## Stage 4 — Design specification",
            "## Stage 5 — Authorized implementation and local verification",
            "## Stage 6 — Draft pull request review",
            "## Stage 7 — Approval, squash merge, synchronization, and cleanup",
            "## Stage 8 — Declared-target deployment",
        ])
        grilling, planning, design, implementation = [
            " ".join(stages.split(header)[1].split("## Stage ")[0].split())
            for header in headers[1:5]
        ]
        self.assertIn("../../grill-me/SKILL.md", grilling)
        self.assertIn("technical choices still requiring investigation", grilling)
        self.assertIn("map acceptance criteria to checks", planning)
        self.assertIn("planning owns sequencing and evidence", planning)
        self.assertIn("spec-ready.md#design-specification", design)
        self.assertIn("Reconcile final design choices with plan sequencing", design)
        self.assertIn("read back the decision summary, plan, and design specification", implementation)
        self.assertIn("full-suite coverage deferred to Stage 7", implementation)

    def test_design_specification_reuses_plan_and_defines_implementation_readiness(self) -> None:
        spec = " ".join(SPEC_READY.read_text().split())
        for marker in (
            "Stage 4 design output, distinct from Stage 3",
            "existing issue/execution note, canonical plan comment",
            "dependency direction, state/data ownership and lifetime",
            "inputs/outputs or data schemas, validation, invariants, errors",
            "failure handling, and verification without guessing",
            "material technical questions are resolved",
            "Block dependent implementation on missing evidence or decisions",
            "every Stage 3 planning requirement",
            "add the Stage 4 design specification to this same comment",
        ):
            self.assertIn(marker, spec)
        self.assertNotIn("Stage 2 plan requirement", spec)

    def test_grilling_and_stage_artifacts_preserve_authority_and_resume(self) -> None:
        grill = " ".join((SKILL_ROOT.parent / "grill-me/SKILL.md").read_text().split())
        for marker in (
            "Inspect the repository or other authorized sources",
            "prerequisites are settled",
            "Give a recommended answer",
            "Wait for the answer before making a dependent decision",
            "silence, elapsed time, or a preselected option",
            "already settles the tree",
            "interview-only request",
            "coding on a plan-only request, merging, deploying",
            "On resume, inspect the summary and current evidence",
        ):
            self.assertIn(marker, grill)
        stages = " ".join((SKILL_ROOT / "references/stage-contracts.md").read_text().split())
        self.assertIn("plan-only request stops", stages)
        self.assertIn("Honor a design-only or stop-before-coding request", stages)
        self.assertIn("do not add a routine approval wait", stages)
        self.assertIn("revisit only decisions invalidated by new evidence", stages)
        loop = " ".join((ROOT / "plugins/agent-orchestration/skills/sdlc-loop/SKILL.md").read_text().split())
        self.assertIn("select -> grill -> plan -> design specification -> implement", loop)
        self.assertIn("standalone loop does not require another plugin", loop)
        self.assertIn("These steps do not activate autopilot", loop)

    def test_ui_requests_require_a_complete_github_visual_package(self) -> None:
        text = SPEC_READY.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for marker in (
            "UI change requests: mandatory visual package",
            "every image supplied by the user",
            "preserve the request order",
            "upload each image to GitHub so it is embedded in the issue body",
            "Request images: none",
            "exported PNG sketches",
            "Tool-neutral issue text",
            "No silent omission",
            "one or more inspectable exported PNG sketches",
        ):
            self.assertIn(marker, normalized)
        self.assertNotIn("excalidraw", text.lower())


if __name__ == "__main__":
    unittest.main()
