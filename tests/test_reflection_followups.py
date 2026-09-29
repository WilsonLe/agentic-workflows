"""Behavioral regression cases for scoped UI decisions and merge activation."""
from __future__ import annotations
import copy
import unittest
from tests.test_workflow_efficiencies import workflow
from tests.test_standard_workflow_records import task_run


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
