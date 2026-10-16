"""Behavioral regression cases for scoped UI decisions and merge activation."""
from __future__ import annotations
import copy
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_workflow_efficiencies import workflow
from tests.test_standard_workflow_records import SCRIPT, passed_step, task_run


def merge_readiness():
    return {
        "state": "ready",
        "trigger": "deploys",
        "revision": "a" * 40,
        "trigger_evidence_ref": "provider-branch-readback",
        "environment": "production",
        "configuration_ref": "deployment-config-sha",
        "observed_at": "2026-09-29T00:00:00Z",
        "authority_ref": "user-approved-merge",
        "inventory_ref": "changed-dependencies",
        "activation": "active",
        "prerequisites": [
            {
                "id": "schema",
                "state": "ready",
                "revision": "a" * 40,
                "environment": "production",
                "configuration_ref": "deployment-config-sha",
                "evidence_ref": "target-schema-readback",
                "evidence_surface": "target",
                "observed_at": "2026-09-29T00:00:00Z",
            }
        ],
    }


class MergeActivationTests(unittest.TestCase):
    def validate(self, value):
        workflow.validate_merge_readiness(value, source_revision="a" * 40)

    def test_local_pass_cannot_substitute_for_target_migration_or_key(self):
        for prerequisite in ("migration", "encryption-key"):
            value = merge_readiness()
            value["prerequisites"][0].update(id=prerequisite, state="unknown")
            with self.assertRaisesRegex(workflow.RecordError, "unverified target"):
                self.validate(value)
            value["prerequisites"][0].update(state="ready", evidence_surface="local")
            with self.assertRaisesRegex(workflow.RecordError, "local fixtures"):
                self.validate(value)

    def test_identity_drift_invalidates_readiness(self):
        for field in ("revision", "environment", "configuration_ref"):
            value = merge_readiness()
            value["prerequisites"][0][field] = "changed"
            with self.assertRaisesRegex(workflow.RecordError, "stale"):
                self.validate(value)
        value = merge_readiness()
        value["revision"] = "b" * 40
        with self.assertRaisesRegex(workflow.RecordError, "stale candidate"):
            self.validate(value)

    def test_unknown_trigger_and_incomplete_staging_block(self):
        value = merge_readiness()
        value["trigger"] = "unknown"
        with self.assertRaisesRegex(workflow.RecordError, "unknown deployment"):
            self.validate(value)
        value = merge_readiness()
        value["activation"] = "safely_inactive"
        value["prerequisites"][0]["state"] = "deferred"
        with self.assertRaises(workflow.RecordError):
            self.validate(value)
        value.update(
            inactivity_evidence_ref="all-routes-disabled",
            compatibility_evidence_ref="old-reader-and-schema-proof",
            activation_followup="issue-activation",
        )
        self.validate(value)

    def test_non_deploying_merge_needs_no_production_checks(self):
        self.validate(
            {
                "state": "ready",
                "trigger": "does_not_deploy",
                "revision": "a" * 40,
                "trigger_evidence_ref": "branch-not-deployed",
                "prerequisites": [],
            }
        )
        value = merge_readiness()
        value["state"] = "blocked"
        value["prerequisites"][0]["state"] = "unknown"
        self.validate(value)

    def test_integrated_record_rejects_missing_prerequisite(self):
        record = task_run()
        record["merge_readiness"] = merge_readiness()
        record["merge_readiness"]["prerequisites"][0]["state"] = "blocked"
        with self.assertRaisesRegex(workflow.RecordError, "unverified target"):
            workflow.validate_record(record)


class UIConventionTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "repository": "project-a",
            "changed_surfaces": ["new-screen"],
            "rules": [
                {
                    "id": "concise-copy",
                    "source_ref": "approved-project-guide",
                    "surface": "new-screen",
                    "state": "current",
                    "applicable": True,
                    "review": "passed",
                    "evidence_ref": "render",
                }
            ],
        }

    def test_second_project_cannot_inherit_rules(self):
        with self.assertRaisesRegex(workflow.RecordError, "repository mismatch"):
            workflow.validate_ui_conventions(self.record, repository="project-b")

    def test_conflicting_copy_or_control_blocks_delivery(self):
        for rule_id in ("concise-copy", "shared-select"):
            value = copy.deepcopy(self.record)
            value["rules"][0].update(id=rule_id, review="failed")
            with self.assertRaisesRegex(workflow.RecordError, "delivery review"):
                workflow.validate_ui_conventions(
                    value, repository="project-a", require_final=True
                )
        workflow.validate_ui_conventions(
            self.record, repository="project-a", require_final=True
        )

    def test_supersession_and_local_scope_are_explicit(self):
        rule = self.record["rules"][0]
        rule.update(state="superseded", superseded_by="new-decision")
        with self.assertRaisesRegex(workflow.RecordError, "superseded"):
            workflow.validate_ui_conventions(self.record, repository="project-a")
        rule.update(applicable=False, review="not_applicable")
        workflow.validate_ui_conventions(
            self.record, repository="project-a", require_final=True
        )
        rule.update(state="screen_local", applicable=True, review="exception")
        with self.assertRaises(workflow.RecordError):
            workflow.validate_ui_conventions(
                self.record, repository="project-a", require_final=True
            )
        rule.update(exception_reason="Keep a necessary accessible error label")
        workflow.validate_ui_conventions(
            self.record, repository="project-a", require_final=True
        )


class ScreenLocalTests(unittest.TestCase):
    def test_local_correction_does_not_apply_to_other_screen(self):
        record = {
            "repository": "a",
            "changed_surfaces": ["settings"],
            "rules": [
                {
                    "id": "short-heading",
                    "source_ref": "user-correction",
                    "surface": "login",
                    "state": "screen_local",
                    "applicable": True,
                    "review": "passed",
                    "evidence_ref": "render",
                }
            ],
        }
        with self.assertRaisesRegex(workflow.RecordError, "another surface"):
            workflow.validate_ui_conventions(record, repository="a", require_final=True)


class ReflectionHandoffScenarios(unittest.TestCase):
    """Synthetic later-task handoffs, exercised through the operator's CLI.

    Observations below are fixtures, not captured agent/browser/provider runs.
    They test whether declared evidence can satisfy delivery, not its truth.
    """

    def check_handoff(self, record, *, error=None, final=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handoff.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            command = [sys.executable, str(SCRIPT), "validate", str(path)]
            if final:
                command.append("--require-final")
            result = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
        if error is None:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Valid task_run record:", result.stdout)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(error, result.stderr)
            self.assertNotIn("Valid task_run record:", result.stdout)

    def consumer_task(self):
        record = task_run()
        record["task"][
            "objective"
        ] = "Index the supplied video and retain all labels after reload."
        record["applicability"]["browser"].update(
            state="required",
            reason="Actual saved labels need browser readback.",
            evidence_refs=["fixture-user-request-for-visible-browser"],
        )
        record["verification"]["claims"] = [
            {
                "id": "saved-labels",
                "claim": "All 47 scene labels and summary survive reload.",
                "primary_channel": "built-in browser with connected model",
                "selected_channel": "built-in browser with connected model",
                "availability": "available",
                "decision": "primary",
                "equivalence_justification": "",
                "approval_owner": "",
                "approval_ref": None,
                "satisfied": True,
                "artifact_refs": [],
                "outcome_check": {
                    "input_ref": "fixture-video-47-scenes",
                    "expected_result": "47 labels plus summary persist across reload, including a long style label.",
                    "observed_result": "47 labels plus summary read back after reload; long label retained within the limit.",
                    "evidence_ref": "fixture-connected-model-and-reload-observation",
                    "evidence_kind": "actual",
                    "state": "passed",
                    "limitation": "",
                },
            }
        ]
        record["evidence"]["claim_refs"] = ["saved-labels"]
        return record

    def test_controlled_indexing_then_failed_live_retry_cannot_close_delivery(self):
        record = self.consumer_task()
        claim = record["verification"]["claims"][0]
        outcome = claim["outcome_check"]
        outcome.update(
            evidence_kind="controlled",
            observed_result="47 canned provider replies were accepted.",
        )
        self.check_handoff(record, error="lacks a passed actual outcome")
        # Removing the claim from final evidence must not hide a required failed run.
        claim["satisfied"] = False
        outcome.update(
            evidence_kind="actual",
            state="failed",
            observed_result="12/47 labels saved; scene 13 rejected an oversized style.",
            limitation="Connected-model indexing has not completed.",
        )
        record["evidence"]["claim_refs"] = []
        self.check_handoff(
            record, error="final actual outcome saved-labels remains unsatisfied"
        )
        self.check_handoff(self.consumer_task())

    def test_requested_browser_cannot_be_silently_replaced_by_headless_checks(self):
        record = self.consumer_task()
        claim = record["verification"]["claims"][0]
        claim["selected_channel"] = "headless browser with stubbed model"
        self.check_handoff(record, error="primary decision selects a different channel")
        claim.update(decision="diagnostic", satisfied=False)
        claim["outcome_check"].update(
            state="unavailable",
            observed_result="",
            evidence_ref="",
            limitation="Requested visible browser is unavailable.",
        )
        record["evidence"].update(status="rehearsal", claim_refs=[])
        record["status"] = "blocked"
        self.check_handoff(record, final=False)
        self.check_handoff(record, error="final actual outcome")

    def test_equivalent_channel_still_requires_explicit_approval(self):
        record = self.consumer_task()
        claim = record["verification"]["claims"][0]
        claim.update(
            selected_channel="visible native browser with connected model",
            decision="equivalent",
            equivalence_justification="Same video, live provider, saved labels and reload boundary.",
            approval_owner="user",
            approval_ref="visible-browser-substitution",
        )
        self.check_handoff(record, error="lacks approved fallback authority")
        record["approvals"].append(
            {
                "id": "visible-browser-substitution",
                "kind": "verification_fallback",
                "state": "approved",
                "scope": "Use the visible native browser for saved-labels.",
            }
        )
        self.check_handoff(record)

    def test_future_live_outcome_stays_explicit_and_becomes_required_at_its_milestone(
        self
    ):
        record = self.consumer_task()
        claim = record["verification"]["claims"][0]
        claim.update(satisfied=False, availability="unavailable")
        claim["outcome_check"].update(
            completion_required=False,
            state="unavailable",
            observed_result="",
            evidence_ref="",
            limitation="Live provider run explicitly deferred to the authorized release milestone.",
        )
        record["evidence"]["claim_refs"] = []
        self.check_handoff(record)
        record["evidence"]["claim_refs"] = ["saved-labels"]
        self.check_handoff(record, error="unsatisfied verification claim")
        record["evidence"]["claim_refs"] = []
        claim["outcome_check"]["completion_required"] = True
        self.check_handoff(record, error="final actual outcome")

    def later_ui_task(self):
        record = task_run()
        record["task"][
            "objective"
        ] = "Add a speech feedback screen using the project's established UI decisions."
        record["ui_conventions"] = {
            "repository": record["repository"]["identity"],
            "changed_surfaces": ["speech-feedback"],
            "rules": [
                {
                    "id": "progressive-disclosure",
                    "source_ref": "project-guide-approved-in-earlier-task",
                    "surface": "speech-feedback",
                    "state": "current",
                    "applicable": True,
                    "review": "passed",
                    "evidence_ref": "fixture-current-screen-details-on-demand",
                },
                {
                    "id": "essential-recovery",
                    "source_ref": "project-guide-approved-in-earlier-task",
                    "surface": "speech-feedback",
                    "state": "current",
                    "applicable": True,
                    "review": "exception",
                    "exception_reason": "Keep labelled Retry and missing-recording guidance visible for recovery and accessibility.",
                    "evidence_ref": "fixture-current-screen-retry-focus-and-label",
                },
            ],
        }
        return record

    def test_later_ui_task_requires_current_review_and_preserves_essential_recovery(
        self
    ):
        record = self.later_ui_task()
        self.check_handoff(record)
        for review in ("pending", "failed", "not_applicable"):
            with self.subTest(review=review):
                incorrect = copy.deepcopy(record)
                incorrect["ui_conventions"]["rules"][0]["review"] = review
                self.check_handoff(incorrect, error="has not passed delivery review")
        record["ui_conventions"]["rules"][0]["evidence_ref"] = ""
        self.check_handoff(record, error="evidence_ref")
        record = self.later_ui_task()
        record["ui_conventions"]["rules"][1]["exception_reason"] = ""
        self.check_handoff(record, error="exception_reason")

    def test_later_ui_task_rejects_other_project_stale_capture_and_superseded_rule(
        self
    ):
        record = self.later_ui_task()
        record["ui_conventions"]["repository"] = "another/project"
        self.check_handoff(record, error="repository mismatch")
        record = self.later_ui_task()
        record["evidence"]["source_revision"] = "b" * 40
        self.check_handoff(record, error="stale source identity")
        record = self.later_ui_task()
        old_rule = record["ui_conventions"]["rules"][0]
        old_rule.update(state="superseded", superseded_by="new-approved-layout")
        self.check_handoff(record, error="superseded UI convention cannot apply")
        old_rule.update(applicable=False, review="not_applicable")
        record["ui_conventions"]["rules"].append(
            {
                **old_rule,
                "id": "new-approved-layout",
                "state": "current",
                "applicable": True,
                "review": "passed",
                "source_ref": "new-user-decision",
            }
        )
        self.check_handoff(record)

    def broad_feedback_task(self):
        record = self.consumer_task()
        record["task"][
            "objective"
        ] = "Apply friendly feedback across all practice and mock question types and response states."
        record["verification"]["claims"] = []
        record["evidence"]["claim_refs"] = []
        record["validation"]["steps"].insert(
            1, passed_step("feedback-consumer-map", cost="static")
        )
        record["evidence"]["validation_refs"].append("feedback-consumer-map")
        surfaces = []
        for question, state in itertools.product(
            ("reorder", "speech", "choice"), ("answered", "missing-response")
        ):
            claim = copy.deepcopy(self.consumer_task()["verification"]["claims"][0])
            claim.update(
                id=f"{question}-{state}",
                claim=f"Shared {question} feedback renders the {state} state.",
            )
            claim.update(
                primary_channel="built-in browser", selected_channel="built-in browser"
            )
            claim["outcome_check"].update(
                input_ref=f"fixture-{question}-{state}",
                expected_result="Inline answer comparison and on-demand explanation."
                if state == "answered"
                else "Clear missing-response recovery without empty comparison panels.",
                observed_result="Comparison and explanation trigger rendered."
                if state == "answered"
                else "Recovery action rendered; empty panels absent.",
                evidence_ref=f"fixture-render-{question}-{state}",
            )
            record["verification"]["claims"].append(claim)
            record["evidence"]["claim_refs"].append(claim["id"])
            for route in ("practice", "mock"):
                surfaces.append(
                    {
                        "id": f"{route}/{question}/{state}",
                        "kind": "feedback-state",
                        "decision": "included",
                        "reason": "Requested feedback uses the same renderer in both routes; structural mapping covers route wiring.",
                        "shared_point": f"{question}-feedback",
                        "verification_refs": ["feedback-consumer-map", claim["id"]],
                    }
                )
        # The discovered matrix is independent of the candidate's surface rows.
        discovered = [
            "/".join(cell)
            for cell in itertools.product(
                ("practice", "mock"),
                ("reorder", "speech", "choice"),
                ("answered", "missing-response"),
            )
        ]
        record["impact_inventory"] = {
            "pattern_wide": True,
            "discovery_evidence_refs": ["fixture-route-question-state-discovery"],
            "discovered_surface_ids": discovered + ["settings"],
            "surfaces": surfaces
            + [
                {
                    "id": "settings",
                    "kind": "route",
                    "decision": "excluded",
                    "reason": "Settings has no question feedback consumer.",
                    "shared_point": "",
                    "verification_refs": [],
                }
            ],
        }
        return record

    def test_all_feedback_cells_accept_shared_structural_and_representative_runtime_proof(
        self
    ):
        record = self.broad_feedback_task()
        self.assertEqual(len(record["impact_inventory"]["discovered_surface_ids"]), 13)
        self.assertEqual(len(record["verification"]["claims"]), 6)
        self.check_handoff(record)

    def test_all_feedback_cells_reject_missing_cell_unknown_or_missing_proof(self):
        for defect in ("missing-cell", "missing-proof", "unknown-proof"):
            with self.subTest(defect=defect):
                record = self.broad_feedback_task()
                inventory = record["impact_inventory"]
                target = next(
                    surface
                    for surface in inventory["surfaces"]
                    if surface["id"] == "mock/speech/missing-response"
                )
                if defect == "missing-cell":
                    inventory["surfaces"].remove(target)
                    error = "omits or duplicates a discovered surface"
                else:
                    target["verification_refs"] = (
                        [] if defect == "missing-proof" else ["prior-task-render"]
                    )
                    error = (
                        "lacks final verification"
                        if defect == "missing-proof"
                        else "unknown verification"
                    )
                self.check_handoff(record, error=error)

    def test_all_feedback_cells_cannot_hide_unresolved_runtime_outcome_behind_static_pass(
        self
    ):
        record = self.broad_feedback_task()
        claim = next(
            item
            for item in record["verification"]["claims"]
            if item["id"] == "speech-missing-response"
        )
        claim["satisfied"] = False
        claim["outcome_check"].update(
            state="unavailable",
            observed_result="",
            evidence_ref="",
            limitation="Missing-recording feedback is unreachable in the requested browser.",
        )
        record["evidence"]["claim_refs"].remove(claim["id"])
        for surface in record["impact_inventory"]["surfaces"]:
            if claim["id"] in surface["verification_refs"]:
                surface["verification_refs"] = ["feedback-consumer-map"]
        self.check_handoff(
            record,
            error="final actual outcome speech-missing-response remains unsatisfied",
        )
