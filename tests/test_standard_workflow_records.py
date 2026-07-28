from __future__ import annotations

import copy
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins"
    / "amsoft-agentic-workflows"
    / "skills"
    / "standard-development-workflow"
    / "scripts"
    / "standard_workflow_record.py"
)
SPEC = importlib.util.spec_from_file_location("standard_workflow_record", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
workflow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workflow)

REVISION = "a" * 40
DIGEST = "sha256:" + ("0" * 64)


def applicability(
    state: str = "required",
    *,
    reason: str = "Repository evidence requires this capability.",
) -> dict[str, object]:
    return {
        "state": state,
        "reason": reason,
        "evidence_refs": ["instructions"] if state in {"required", "optional"} else [],
    }


def profile() -> dict[str, object]:
    return {
        "schema_version": 1,
        "record_kind": "repository_profile",
        "record_id": "profile-example",
        "repository": {
            "identity": "example/repository",
            "default_branch": "main",
            "revision": REVISION,
        },
        "provenance": {
            "created_at": "2026-07-28T00:00:00Z",
            "sources": [],
        },
        "applicability": {"repository_discovery": applicability()},
        "capabilities": {
            "commands": {"test": "repository-defined"},
            "services": [],
        },
        "environment_keys": ["EXAMPLE_ENDPOINT"],
        "status": "ready",
    }


def passed_step(
    step_id: str,
    *,
    prerequisites: list[str] | None = None,
    cost: str = "focused",
    completion_required: bool = True,
) -> dict[str, object]:
    return {
        "id": step_id,
        "command_or_boundary": "repository-supported check",
        "evidence_ref": "instructions",
        "prerequisites": prerequisites or [],
        "cost": cost,
        "completion_required": completion_required,
        "state": "passed",
        "skip_reason": "",
    }


def task_run() -> dict[str, object]:
    current_profile = profile()
    return {
        "schema_version": 1,
        "record_kind": "task_run",
        "record_id": "task-example",
        "repository": {
            "identity": "example/repository",
            "default_branch": "main",
            "revision": REVISION,
        },
        "provenance": {
            "created_at": "2026-07-28T00:00:00Z",
            "sources": [],
        },
        "applicability": {
            "execution_contract": applicability(),
            "browser": applicability("not_applicable", reason="No browser surface."),
        },
        "profile_ref": {
            "record_id": current_profile["record_id"],
            "digest": workflow.content_digest(current_profile),
        },
        "task": {
            "issue": "https://github.com/example/repository/issues/1",
            "objective": "Deliver the approved behavior.",
            "worktree": "/worktrees/example",
            "base_revision": REVISION,
        },
        "scope": {
            "direct": ["component"],
            "enabling": [],
            "follow_up": [],
            "prohibited": ["unrelated cleanup"],
            "change_envelope": ["component/**"],
            "expansion": {
                "triggered": False,
                "reasons": [],
                "approval_state": "not_triggered",
            },
        },
        "approvals": [
            {
                "id": "plan-approval",
                "kind": "implementation_plan",
                "state": "approved",
                "scope": "Direct work only.",
            }
        ],
        "resources": [],
        "validation": {
            "source_revision": REVISION,
            "steps": [
                passed_step("static", cost="static"),
                passed_step("complete", prerequisites=["static"]),
            ],
        },
        "failures": [],
        "sandboxes": [],
        "artifacts": [],
        "operations": [],
        "verification": {"claims": []},
        "evidence": {
            "status": "final",
            "source_revision": REVISION,
            "tracked_source_clean": True,
            "artifact_refs": [],
            "validation_refs": ["static", "complete"],
            "claim_refs": [],
            "files": [],
            "limitations": [],
            "finalized_at": "2026-07-28T01:00:00Z",
        },
        "status": "completed",
    }


def operation(
    operation_id: str = "build",
    *,
    state: str = "running",
    mutation_key: str = "build-output",
) -> dict[str, object]:
    return {
        "id": operation_id,
        "purpose": "Produce a verified output.",
        "command_or_tool": "repository build",
        "evidence_ref": "instructions",
        "working_directory": "/worktrees/example",
        "source_revision": REVISION,
        "inputs_digest": DIGEST,
        "expected_outputs": ["artifact"],
        "ownership": "task",
        "budgets": {"soft_seconds": 60, "hard_seconds": 120},
        "liveness": "output progress",
        "cancellation": "repository-supported cancellation",
        "resumability": "inspect checkpoint before restart",
        "state": state,
        "checkpoint": {"observed": "2026-07-28T00:00:00Z"}
        if state != "planned"
        else {},
        "mutating": True,
        "mutation_key": mutation_key,
        "retry_count": 0,
        "max_retries": 1,
        "retry_reason": "",
    }


class StandardWorkflowRecordTests(unittest.TestCase):
    def assert_invalid(self, record: dict[str, object], message: str) -> None:
        with self.assertRaisesRegex(workflow.RecordError, message):
            workflow.validate_record(record)

    def test_profile_and_task_share_canonical_identity(self) -> None:
        repository_profile = profile()
        task = task_run()
        workflow.validate_record(repository_profile)
        workflow.validate_record(task, profile=repository_profile, require_final=True)
        self.assertEqual(
            workflow.content_digest(repository_profile),
            task["profile_ref"]["digest"],
        )
        self.assertEqual(
            workflow.canonical_bytes({"b": 2, "a": 1}),
            b'{"a":1,"b":2}\n',
        )

    def test_stale_or_wrong_profile_is_rejected(self) -> None:
        repository_profile = profile()
        task = task_run()
        repository_profile["capabilities"]["commands"]["build"] = "changed"
        with self.assertRaisesRegex(workflow.RecordError, "profile is stale"):
            workflow.validate_record(task, profile=repository_profile)
        repository_profile = profile()
        repository_profile["repository"]["identity"] = "another/repository"
        task["profile_ref"]["digest"] = workflow.content_digest(repository_profile)
        with self.assertRaisesRegex(workflow.RecordError, "repositories differ"):
            workflow.validate_record(task, profile=repository_profile)

    def test_repository_file_drift_is_rejected(self) -> None:
        repository_profile = profile()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "AGENTS.md"
            evidence.write_text("first\n", encoding="utf-8")
            repository_profile["provenance"]["sources"] = [
                {
                    "id": "instructions",
                    "kind": "repository_file",
                    "location": "AGENTS.md",
                    "digest": workflow.file_digest(evidence),
                    "freshness": "revision_bound",
                    "checked_at": "2026-07-28T00:00:00Z",
                }
            ]
            workflow.validate_record(repository_profile, source_root=root)
            evidence.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(workflow.RecordError, "drifted"):
                workflow.validate_record(repository_profile, source_root=root)

    def test_secret_fields_and_values_are_rejected(self) -> None:
        repository_profile = profile()
        repository_profile["capabilities"]["token"] = "not-allowed"
        self.assert_invalid(repository_profile, "secret-bearing field")
        repository_profile = profile()
        repository_profile["capabilities"]["notes"] = (
            "ghp_abcdefghijklmnopqrstuvwxyz123456"
        )
        self.assert_invalid(repository_profile, "secret value")
        repository_profile = profile()
        repository_profile["capabilities"]["repository"] = (
            "https://user:password@example.com/private.git"
        )
        self.assert_invalid(repository_profile, "secret value")

    def test_environment_key_names_are_allowed_but_values_are_not(self) -> None:
        repository_profile = profile()
        repository_profile["environment_keys"] = ["SERVICE_API_TOKEN"]
        workflow.validate_record(repository_profile)
        repository_profile["capabilities"]["value"] = "plaintext"
        self.assert_invalid(repository_profile, "secret-bearing field")

    def test_blocked_capability_cannot_enter_execution(self) -> None:
        task = task_run()
        task["applicability"]["required_channel"] = applicability(
            "blocked", reason="Requested channel is unavailable."
        )
        self.assert_invalid(task, "blocking capabilities")
        task["status"] = "blocked"
        workflow.validate_record(task)

    def test_enabling_work_requires_inseparability_evidence(self) -> None:
        task = task_run()
        task["scope"]["enabling"] = [{"change": "shared helper"}]
        self.assert_invalid(task, "missing required keys")

    def test_material_expansion_requires_revised_approval(self) -> None:
        task = task_run()
        task["scope"]["expansion"] = {
            "triggered": True,
            "reasons": ["new public API"],
            "approval_state": "pending",
        }
        self.assert_invalid(task, "revised approval")
        task["scope"]["expansion"]["approval_state"] = "revised_approved"
        workflow.validate_record(task)

    def test_shared_resource_cleanup_requires_exact_approval(self) -> None:
        task = task_run()
        task["resources"] = [
            {
                "id": "cache",
                "kind": "build_cache",
                "ownership": "host_shared",
                "capacity": "sufficient",
                "cleanup": {
                    "allowed": True,
                    "exact_target": "/shared/cache",
                    "approval_ref": None,
                },
                "recovery": "re-download",
            }
        ]
        self.assert_invalid(task, "explicit approval")
        task["approvals"].append(
            {
                "id": "reclamation-approval",
                "kind": "shared_resource_reclamation",
                "state": "approved",
                "scope": "Only the resolved cache target.",
            }
        )
        task["resources"][0]["cleanup"]["approval_ref"] = "reclamation-approval"
        workflow.validate_record(task)

    def test_pending_plan_and_unknown_capacity_block_execution(self) -> None:
        task = task_run()
        task["approvals"][0]["state"] = "pending"
        self.assert_invalid(task, "approved implementation plan")
        task = task_run()
        task["resources"] = [
            {
                "id": "disk",
                "kind": "disk",
                "ownership": "task",
                "capacity": "unknown",
                "cleanup": {
                    "allowed": False,
                    "exact_target": "",
                    "approval_ref": None,
                },
                "recovery": "No cleanup authorized.",
            }
        ]
        self.assert_invalid(task, "capacity blocks")

    def test_failed_prerequisite_blocks_expensive_step(self) -> None:
        task = task_run()
        task["evidence"]["status"] = "rehearsal"
        task["validation"]["steps"][0]["state"] = "failed"
        self.assert_invalid(task, "ran after failed prerequisite")

    def test_validation_cycle_and_unknown_prerequisite_are_rejected(self) -> None:
        task = task_run()
        task["validation"]["steps"][0]["prerequisites"] = ["complete"]
        self.assert_invalid(task, "cycle")
        task = task_run()
        task["validation"]["steps"][1]["prerequisites"] = ["missing"]
        self.assert_invalid(task, "unknown prerequisite")

    def test_validation_ladder_must_be_cheap_first(self) -> None:
        task = task_run()
        task["validation"]["steps"][0]["cost"] = "build"
        task["validation"]["steps"][1]["cost"] = "static"
        self.assert_invalid(task, "cheap-first")

    def test_unknown_required_failure_blocks_review(self) -> None:
        task = task_run()
        task["evidence"]["status"] = "rehearsal"
        task["validation"]["steps"][0]["state"] = "failed"
        task["validation"]["steps"][1]["state"] = "blocked"
        task["failures"] = [
            {
                "id": "failure-1",
                "step_ref": "static",
                "first_evidence": "original stderr retained",
                "reproduction": "focused clean rerun",
                "classification": "unknown",
                "classification_evidence": "not resolved",
                "remedy": "none",
                "rerun_steps": [],
                "accepted": False,
            }
        ]
        self.assert_invalid(task, "unknown required failure")
        task["failures"][0]["accepted"] = True
        workflow.validate_record(task)

    def test_each_failure_class_is_representable(self) -> None:
        for classification in workflow.FAILURE_CLASSES:
            with self.subTest(classification=classification):
                task = task_run()
                task["evidence"]["status"] = "rehearsal"
                task["validation"]["steps"][0]["completion_required"] = False
                task["validation"]["steps"][0]["state"] = "failed"
                task["validation"]["steps"][1]["state"] = "blocked"
                task["failures"] = [
                    {
                        "id": "failure",
                        "step_ref": "static",
                        "first_evidence": "retained",
                        "reproduction": "focused",
                        "classification": classification,
                        "classification_evidence": "evidence",
                        "remedy": "bounded remedy",
                        "rerun_steps": [],
                        "accepted": classification == "unknown",
                    }
                ]
                workflow.validate_record(task)

    def test_suite_state_contamination_requires_safe_sharing(self) -> None:
        task = task_run()
        task["sandboxes"] = [
            {
                "id": "integration",
                "suite": "integration",
                "mutable_resources": ["database"],
                "readiness": ["migrated"],
                "cleanup_targets": ["database-integration"],
                "safe_sharing_evidence": "",
            },
            {
                "id": "browser",
                "suite": "browser",
                "mutable_resources": ["database"],
                "readiness": ["seeded"],
                "cleanup_targets": ["database-browser"],
                "safe_sharing_evidence": "",
            },
        ]
        self.assert_invalid(task, "share mutable state")
        for sandbox in task["sandboxes"]:
            sandbox["safe_sharing_evidence"] = "Repository fixtures reset every test."
        workflow.validate_record(task)

    def test_artifact_requires_immutable_matching_identity(self) -> None:
        task = task_run()
        task["artifacts"] = [
            {
                "id": "package",
                "digest": DIGEST,
                "source_revision": REVISION,
                "build_inputs_digest": DIGEST,
                "command_ref": "build",
                "platform": "darwin-arm64",
                "immutable": True,
                "verified": True,
            }
        ]
        task["evidence"]["artifact_refs"] = ["package"]
        workflow.validate_record(task)
        task["artifacts"][0]["source_revision"] = "b" * 40
        self.assert_invalid(task, "stale source")
        task["artifacts"][0]["source_revision"] = REVISION
        task["artifacts"][0]["immutable"] = False
        self.assert_invalid(task, "mutable")
        task["artifacts"][0]["immutable"] = True
        task["artifacts"][0]["verified"] = False
        self.assert_invalid(task, "not verified")

    def test_long_operation_requires_checkpoint_and_matching_source(self) -> None:
        task = task_run()
        task["operations"] = [operation()]
        workflow.validate_record(task)
        task["operations"][0]["checkpoint"] = {}
        self.assert_invalid(task, "durable checkpoint")
        task["operations"][0] = operation()
        task["operations"][0]["source_revision"] = "b" * 40
        self.assert_invalid(task, "checkpoint is stale")

    def test_duplicate_mutating_operation_is_rejected(self) -> None:
        task = task_run()
        task["operations"] = [
            operation("migration-1", mutation_key="database-migration"),
            operation("migration-2", mutation_key="database-migration"),
        ]
        self.assert_invalid(task, "duplicate mutating operation")

    def test_retry_and_time_budgets_are_bounded(self) -> None:
        task = task_run()
        task["operations"] = [operation()]
        task["operations"][0]["retry_count"] = 2
        task["operations"][0]["retry_reason"] = "One bounded transient retry."
        self.assert_invalid(task, "retry budget")
        task["operations"][0] = operation()
        task["operations"][0]["budgets"] = {
            "soft_seconds": 120,
            "hard_seconds": 60,
        }
        self.assert_invalid(task, "time budgets")

    def test_retry_requires_a_diagnosed_reason(self) -> None:
        task = task_run()
        task["operations"] = [operation()]
        task["operations"][0]["retry_count"] = 1
        self.assert_invalid(task, "retry_reason")
        task["operations"][0]["retry_reason"] = "Registry connection reset."
        workflow.validate_record(task)

    def test_partial_or_diagnostic_channel_cannot_satisfy_claim(self) -> None:
        for decision in ("partial", "diagnostic"):
            with self.subTest(decision=decision):
                task = task_run()
                task["verification"]["claims"] = [
                    {
                        "id": "rendered-ui",
                        "claim": "Rendered UI is correct.",
                        "primary_channel": "requested browser",
                        "availability": "available",
                        "selected_channel": "API",
                        "decision": decision,
                        "equivalence_justification": "",
                        "approval_owner": "",
                        "approval_ref": None,
                        "satisfied": True,
                        "artifact_refs": [],
                    }
                ]
                self.assert_invalid(task, "weaker channel")

    def test_equivalent_fallback_requires_justification(self) -> None:
        task = task_run()
        task["verification"]["claims"] = [
            {
                "id": "claim",
                "claim": "Same observable boundary.",
                "primary_channel": "primary",
                "availability": "unavailable",
                "selected_channel": "fallback",
                "decision": "equivalent",
                "equivalence_justification": "",
                "approval_owner": "user",
                "approval_ref": "fallback-approval",
                "satisfied": True,
                "artifact_refs": [],
            }
        ]
        self.assert_invalid(task, "equivalence_justification")
        task["approvals"].append(
            {
                "id": "fallback-approval",
                "kind": "verification_fallback",
                "state": "approved",
                "scope": "Claim-specific equivalent channel.",
            }
        )
        task["verification"]["claims"][0][
            "equivalence_justification"
        ] = "The fallback exercises the same independently observable boundary."
        task["evidence"]["claim_refs"] = ["claim"]
        workflow.validate_record(task)

    def test_unavailable_primary_cannot_claim_success(self) -> None:
        task = task_run()
        task["verification"]["claims"] = [
            {
                "id": "claim",
                "claim": "Required channel.",
                "primary_channel": "device",
                "availability": "unavailable",
                "selected_channel": "device",
                "decision": "primary",
                "equivalence_justification": "",
                "approval_owner": "",
                "approval_ref": None,
                "satisfied": True,
                "artifact_refs": [],
            }
        ]
        self.assert_invalid(task, "unavailable primary")

    def test_rehearsal_and_drifted_evidence_fail_final_gate(self) -> None:
        task = task_run()
        task["evidence"]["status"] = "rehearsal"
        with self.assertRaisesRegex(workflow.RecordError, "Rehearsal|rehearsal"):
            workflow.validate_record(task, require_final=True)
        task = task_run()
        task["evidence"]["source_revision"] = "b" * 40
        self.assert_invalid(task, "stale source")

    def test_final_evidence_requires_all_completion_steps(self) -> None:
        task = task_run()
        task["evidence"]["validation_refs"] = ["static"]
        self.assert_invalid(task, "omits")

    def test_five_archetypes_support_progressive_disclosure(self) -> None:
        archetypes = {
            "library": {"browser": "not_applicable", "stateful": "not_applicable"},
            "cli": {"artifact": "required", "stateful": "not_applicable"},
            "service": {"stateful": "required", "browser": "not_applicable"},
            "browser": {"stateful": "required", "browser": "required"},
            "staged": {"stateful": "required", "external": "required"},
        }
        for name, decisions in archetypes.items():
            with self.subTest(archetype=name):
                task = task_run()
                for capability_name, state in decisions.items():
                    task["applicability"][capability_name] = applicability(
                        state,
                        reason=f"{name} applicability decision.",
                    )
                workflow.validate_record(task)

    def test_state_directory_is_scoped_and_overrideable(self) -> None:
        previous = os.environ.get("AMSOFT_WORKFLOW_STATE_DIR")
        try:
            os.environ["AMSOFT_WORKFLOW_STATE_DIR"] = "/tmp/amsoft-workflow-tests"
            self.assertEqual(
                workflow.state_directory(),
                Path("/tmp/amsoft-workflow-tests"),
            )
        finally:
            if previous is None:
                os.environ.pop("AMSOFT_WORKFLOW_STATE_DIR", None)
            else:
                os.environ["AMSOFT_WORKFLOW_STATE_DIR"] = previous

    def test_state_directory_resolves_windows_xdg_and_fallbacks(self) -> None:
        self.assertEqual(
            workflow.state_directory(
                platform_name="nt",
                environment={"LOCALAPPDATA": "/windows-local"},
                home=Path("/home"),
            ),
            Path("/windows-local/AMSoft/standard-development-workflow"),
        )
        self.assertEqual(
            workflow.state_directory(
                platform_name="posix",
                environment={"XDG_STATE_HOME": "/xdg-state"},
                home=Path("/home"),
            ),
            Path("/xdg-state/amsoft/standard-development-workflow"),
        )
        self.assertEqual(
            workflow.state_directory(
                platform_name="posix",
                environment={},
                home=Path("/home"),
            ),
            Path("/home/.local/state/amsoft/standard-development-workflow"),
        )
        with self.assertRaisesRegex(workflow.RecordError, "absolute path"):
            workflow.state_directory(
                platform_name="posix",
                environment={"AMSOFT_WORKFLOW_STATE_DIR": "relative-state"},
                home=Path("/home"),
            )

    def test_summary_is_compact_and_outcome_focused(self) -> None:
        output = workflow.summarize(task_run())
        self.assertIn("Task Run", output)
        self.assertIn("Deliver the approved behavior.", output)
        self.assertIn("Evidence: `final`", output)
        self.assertNotIn("command_or_boundary", output)

    def test_future_schema_requires_explicit_migration(self) -> None:
        repository_profile = copy.deepcopy(profile())
        repository_profile["schema_version"] = 2
        self.assert_invalid(repository_profile, "migrate incompatible records")


if __name__ == "__main__":
    unittest.main()
