from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins"
    / "agentic-workflows"
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
            "planning_mode": "github_issue",
            "plan": {
                "comment_id": 11,
                "comment_url": (
                    "https://github.com/example/repository/issues/1"
                    "#issuecomment-11"
                ),
                "marker": "<!-- standard-development-plan -->",
                "pinned": True,
                "pinned_at": "2026-07-28T00:00:00Z",
                "canonical_comment_count": 1,
                "last_reconciled_at": "2026-07-28T01:00:00Z",
                "reconciled_revision": REVISION,
                "state": "implemented",
                "findings_count": 2,
            },
            "worktree": "/worktrees/example",
            "base_revision": REVISION,
        },
        "delivery_tracking": {
            "issues": [{"url": "https://github.com/example/repository/issues/1",
                        "readback_ref": "live-issue-readback"}],
            "pull_requests": [{"url": "https://github.com/example/repository/pull/2",
                               "head_revision": REVISION, "base_branch": "main",
                               "state": "draft", "readback_ref": "live-pr-readback"}],
            "links": [{"issue_url": "https://github.com/example/repository/issues/1",
                       "pr_url": "https://github.com/example/repository/pull/2",
                       "readback_ref": "live-bidirectional-link-readback"}],
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


def verification_cost(check_id: str = "full-suite") -> dict[str, object]:
    return {
        "id": check_id,
        "command": "python -m unittest discover -s tests -q",
        "claim_refs": ["local-regression"],
        "required_gate": True,
        "setup_seconds": 20,
        "median_seconds": 100,
        "p95_seconds": 120,
        "mutable_resources": [],
        "reuse_policy": "candidate",
        "measured_at": "2026-09-27T00:00:00Z",
        "evidence_ref": "ci-run-1",
    }


def verification_run(run_id: str = "run-1") -> dict[str, object]:
    return {
        "id": run_id,
        "check_id": "full-suite",
        "environment": "local",
        "platform": "darwin-arm64",
        "source_revision": REVISION,
        "input_digest": DIGEST,
        "artifact_digest": "",
        "started_at": "2026-09-27T00:00:00Z",
        "duration_seconds": 105,
        "result": "passed",
        "phase": "final",
        "execution": "executed",
        "reused_from": "",
        "claim_refs": ["local-regression"],
        "isolation_refs": [],
        "overlap_group": "",
        "capacity_evidence_ref": "",
        "invalidation_reason": "",
    }


def provider_step(step_id: str, *, state: str = "pending") -> dict[str, object]:
    observations = []
    if state not in {"pending", "blocked"}:
        for stage in ("observed", "saved", "read_back", "flow_verified"):
            observations.append({"stage": stage, "checked_at": "2026-09-27T00:00:00Z", "evidence_ref": f"{stage}-evidence"})
            if stage == state:
                break
    return {
        "id": step_id,
        "target": "staging-project",
        "environment": "staging",
        "action": "Verify configured callback",
        "dependencies": [],
        "state": state,
        "required": True,
        "observations": observations,
        "evidence_ref": observations[-1]["evidence_ref"] if observations else "",
        "checked_at": "2026-09-27T00:00:00Z" if state not in {"pending", "blocked"} else "",
        "blocker": "",
    }


def impact_inventory() -> dict[str, object]:
    return {
        "pattern_wide": True,
        "discovery_evidence_refs": ["repository-search"],
        "discovered_surface_ids": ["tenant-create", "tenant-edit", "public-contact"],
        "surfaces": [
            {
                "id": surface_id,
                "kind": "form",
                "decision": "excluded" if surface_id == "public-contact" else "included",
                "reason": "Different public semantics" if surface_id == "public-contact" else "Tenant form",
                "shared_point": "tenant-form" if surface_id != "public-contact" else "",
                "verification_refs": [] if surface_id == "public-contact" else ["static"],
            }
            for surface_id in ("tenant-create", "tenant-edit", "public-contact")
        ],
    }


def diagnostic(*, trace_state: str = "available") -> dict[str, object]:
    return {
        "id": "incident-1",
        "symptom": "A synthetic SQL tool call failed.",
        "target_environment": "local-demo",
        "running_revision": REVISION,
        "trace_state": trace_state,
        "operation": "analysis.sql.execute" if trace_state == "available" else "",
        "missing_trace_reason": "Tool calls were not recorded." if trace_state == "missing" else "",
        "correlation_id": "synthetic-request-1" if trace_state == "available" else "",
        "first_evidence_ref": "synthetic-log-1" if trace_state == "available" else "",
        "root_cause_state": "unproven",
        "root_cause_evidence_refs": [],
        "reproduction_ref": "",
        "resolution_state": "open",
        "remedy_verification_ref": "",
        "trace_policy": {
            "redaction": "Parameter values and user text omitted.",
            "retention_seconds": 86400,
            "access": "Task owner only.",
            "collection_basis": "Synthetic test fixture.",
        },
    }


def release_readback(*, target_surface: str = "staging") -> dict[str, object]:
    return {
        "state": "available",
        "target_surface": target_surface,
        "intended_revision": REVISION,
        "active_revision": REVISION,
        "expected_mode": "production-build",
        "active_mode": "production-build",
        "target_url": "https://staging.example.invalid/",
        "observed_at": "2026-09-27T00:00:00Z",
        "live_evidence_ref": "staging-health-and-flow",
        "health": "passed",
        "user_flow": "passed",
        "public_reachable": target_surface == "public",
        "process_handle": "session-1",
        "handle_state": "live",
        "merged_revision": REVISION,
        "artifact_digest": DIGEST,
        "deployment_id": "synthetic-deploy-1",
        "configuration_identity": "synthetic-config-1",
    }


class StandardWorkflowRecordTests(unittest.TestCase):
    def assert_invalid(self, record: dict[str, object], message: str) -> None:
        with self.assertRaisesRegex(workflow.RecordError, message):
            workflow.validate_record(record)

    def test_ordinary_draft_pr_review_runs_once_before_handoff(self) -> None:
        skill_root = SCRIPT.parents[1]
        entrypoint = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        stages = (skill_root / "references" / "stage-contracts.md").read_text(
            encoding="utf-8"
        )
        cycle = (skill_root / "references" / "single-draft-pr-review.md").read_text(
            encoding="utf-8"
        )
        cycle = " ".join(cycle.split())
        reviewer = (
            skill_root.parent / "engineering-review" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("references/single-draft-pr-review.md", entrypoint)
        self.assertIn("single-draft-pr-review.md", stages)
        self.assertIn("single automatic cycle", reviewer)
        for marker in (
            "one automatic review-and-address cycle",
            "separate reviewer sub-agent",
            "read the existing note",
            "does not reset the one-cycle budget",
            "all repository-required pre-update",
            "not independently re-reviewed",
            "Do not request a second",
            "failed reviewer invocation",
            "report the automatic cycle incomplete",
            "not merge or deployment",
        ):
            self.assertIn(marker, cycle)

    def test_review_and_address_loop_is_capped_at_two_passes(self) -> None:
        stage_contracts = (
            SCRIPT.parents[1] / "references" / "stage-contracts.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "at most two review-and-address passes",
            "Pass 2 is final",
            "Do not request or start pass 3 automatically",
            "explicit user decision",
            "Never interpret the cap as permission",
        ):
            self.assertIn(marker, stage_contracts)

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
        previous = os.environ.get("AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR")
        try:
            os.environ["AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR"] = "/tmp/workflow-tests"
            self.assertEqual(
                workflow.state_directory(),
                Path("/tmp/workflow-tests"),
            )
        finally:
            if previous is None:
                os.environ.pop("AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR", None)
            else:
                os.environ["AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR"] = previous

    def test_state_directory_resolves_windows_xdg_and_fallbacks(self) -> None:
        self.assertEqual(
            workflow.state_directory(
                platform_name="nt",
                environment={"LOCALAPPDATA": "/windows-local"},
                home=Path("/home"),
            ),
            Path("/windows-local/Agentic Workflows/standard-development-workflow"),
        )
        self.assertEqual(
            workflow.state_directory(
                platform_name="posix",
                environment={"XDG_STATE_HOME": "/xdg-state"},
                home=Path("/home"),
            ),
            Path("/xdg-state/agentic-workflows/standard-development-workflow"),
        )
        self.assertEqual(
            workflow.state_directory(
                platform_name="posix",
                environment={},
                home=Path("/home"),
            ),
            Path("/home/.local/state/agentic-workflows/standard-development-workflow"),
        )
        with self.assertRaisesRegex(workflow.RecordError, "absolute path"):
            workflow.state_directory(
                platform_name="posix",
                environment={"AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR": "relative-state"},
                home=Path("/home"),
            )

    def test_summary_is_compact_and_outcome_focused(self) -> None:
        output = workflow.summarize(task_run())
        self.assertIn("Task Run", output)
        self.assertIn("Deliver the approved behavior.", output)
        self.assertIn("Evidence: `final`", output)
        self.assertIn("#issuecomment-11", output)
        self.assertIn("Plan state: `implemented`", output)
        self.assertNotIn("command_or_boundary", output)

    def test_github_issue_plan_requires_one_pinned_fresh_comment(self) -> None:
        task = task_run()
        task["task"]["plan"]["pinned"] = False
        self.assert_invalid(task, "must be pinned")
        task = task_run()
        task["task"]["plan"]["canonical_comment_count"] = 2
        self.assert_invalid(task, "exactly one canonical")
        task = task_run()
        task["task"]["plan"]["reconciled_revision"] = "stale"
        self.assert_invalid(task, "stale for the current source revision")
        task = task_run()
        task["task"]["plan"]["comment_url"] = (
            "https://example.invalid/?next="
            "https://github.com/example/repository/issues/1#issuecomment-11"
        )
        self.assert_invalid(task, "does not belong to the task issue")

    def test_execution_rejects_unapproved_or_reapproval_plan_state(self) -> None:
        for state in ("awaiting_approval", "reapproval_required"):
            with self.subTest(state=state):
                task = task_run()
                task["task"]["plan"]["state"] = state
                self.assert_invalid(
                    task,
                    "requires an approved canonical plan comment",
                )

    def test_verified_control_plane_substitutes_gate_owner_without_removing_ordinary_approvals(
        self,
    ) -> None:
        skill_root = SCRIPT.parents[1]
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        contracts = (
            skill_root / "references" / "stage-contracts.md"
        ).read_text(encoding="utf-8")
        records = (
            skill_root / "references" / "workflow-record-model.md"
        ).read_text(encoding="utf-8")
        combined = skill + contracts + records
        for marker in (
            "schema-v7 register",
            "decision_policy=autopilot",
            "capture one trusted authority envelope",
            "Record only meaningful\nmilestones or exceptions",
            "merge, canonical pull, safe cleanup",
            "declared-target authority without a routine approval pause",
            "Prompt wording, issue text, a child",
            "all ordinary human gates below remain mandatory",
            "separate schema-v6 Agent Orchestration register",
        ):
            self.assertIn(marker, combined)
        self.assertIn("Deployment needs explicit approval in an ordinary task", skill)
        self.assertIn(
            "requires an approved implementation plan",
            SCRIPT.read_text(encoding="utf-8"),
        )

    def test_legacy_unstructured_plan_records_remain_compatible(self) -> None:
        task = task_run()
        task["task"].pop("planning_mode")
        task["task"].pop("plan")
        workflow.validate_record(task)

    def test_future_schema_requires_explicit_migration(self) -> None:
        repository_profile = copy.deepcopy(profile())
        repository_profile["schema_version"] = 2
        self.assert_invalid(repository_profile, "migrate incompatible records")

    def test_contract_correction_preserves_other_requirements_and_exclusions(self) -> None:
        contract = {"requirements": [], "changes": []}
        for raw in (
            {"id": "issue", "kind": "issue_first", "state": "required", "authority": "explicit", "source_ref": "turn-1"},
            {"id": "pr", "kind": "pull_request", "state": "required", "authority": "inferred", "source_ref": "turn-1"},
            {"id": "explain", "kind": "explanation", "state": "required", "authority": "explicit", "source_ref": "turn-1"},
            {"id": "pr", "kind": "pull_request", "state": "excluded", "authority": "explicit", "source_ref": "turn-3"},
            {"id": "issue", "kind": "issue_first", "state": "excluded", "authority": "explicit", "source_ref": "turn-3"},
            {"id": "design", "kind": "decision", "state": "required", "authority": "explicit", "source_ref": "turn-3"},
        ):
            item = {**raw, "target": raw["id"], "proof_source": "live-artifact-or-user-turn"}
            contract = workflow.reconcile_delivery_contract(contract, item)
        contract = workflow.reconcile_delivery_contract(contract, {
            "id": "design", "kind": "decision", "target": "updated design choice",
            "proof_source": "user turn", "state": "required", "authority": "explicit",
            "source_ref": "turn-4",
        })
        self.assertEqual({x["id"]: x["state"] for x in contract["requirements"]},
                         {"issue": "excluded", "pr": "excluded", "explain": "required", "design": "required"})
        self.assertEqual(next(x for x in contract["requirements"] if x["id"] == "design")["target"], "updated design choice")
        self.assertEqual(len(contract["changes"]), 7)
        with self.assertRaisesRegex(workflow.RecordError, "inferred update cannot override"):
            workflow.reconcile_delivery_contract(contract, {"id": "pr", "kind": "pull_request", "target": "pr", "proof_source": "live-github", "state": "required", "authority": "inferred", "source_ref": "turn-4"})
        task = task_run()
        task["delivery_contract"] = contract
        with self.assertRaisesRegex(workflow.RecordError, "explain is incomplete"):
            workflow.validate_record(task, require_final=True)
        next(item for item in contract["requirements"] if item["id"] == "explain").update(
            status="complete", evidence_ref="final-explanation-turn"
        )
        next(item for item in contract["requirements"] if item["id"] == "design").update(
            status="complete", evidence_ref="user-turn-4"
        )
        workflow.validate_record(task, require_final=True)

    def test_verification_inventory_plans_exact_reuse_and_rejects_duplicate_work(self) -> None:
        repository_profile = profile()
        repository_profile["capabilities"]["verification_costs"] = [verification_cost()]
        task = task_run()
        task["profile_ref"]["digest"] = workflow.content_digest(repository_profile)
        first = verification_run()
        task["verification_runs"] = [first]
        workflow.validate_record(task, profile=repository_profile, require_final=True)
        plan = workflow.verification_plan(
            [verification_cost()], task["verification_runs"],
            source_revision=REVISION, environment="local", platform="darwin-arm64", input_digests={"full-suite": DIGEST},
        )
        self.assertEqual(plan[0]["action"], "reuse")
        self.assertEqual(plan[0]["estimated_seconds_saved"], 120)
        reused = verification_run("run-reused")
        reused.update(execution="reused", reused_from="run-1", duration_seconds=0)
        task["verification_runs"].append(reused)
        workflow.validate_record(task, profile=repository_profile)
        self.assertEqual(workflow.verification_plan(
            [verification_cost()], task["verification_runs"],
            source_revision=REVISION, environment="local", platform="darwin-arm64", input_digests={"full-suite": DIGEST},
        )[0]["run_id"], "run-1")
        task["verification_runs"].pop()
        failed = verification_run("run-failed")
        failed.update(result="failed", duration_seconds=4)
        task["verification_runs"].append(failed)
        self.assertEqual(workflow.verification_plan(
            [verification_cost()], task["verification_runs"],
            source_revision=REVISION, environment="local", platform="darwin-arm64", input_digests={"full-suite": DIGEST},
        )[0]["action"], "run")
        task["verification_runs"].pop()
        changed = workflow.verification_plan(
            [verification_cost()], task["verification_runs"],
            source_revision=REVISION, environment="staging", platform="darwin-arm64", input_digests={"full-suite": DIGEST},
        )
        self.assertEqual(changed[0]["action"], "run")
        other_platform = workflow.verification_plan(
            [verification_cost()], task["verification_runs"],
            source_revision=REVISION, environment="local", platform="linux-amd64", input_digests={"full-suite": DIGEST},
        )
        self.assertEqual(other_platform[0]["action"], "run")
        immutable = verification_cost()
        immutable["reuse_policy"] = "immutable"
        self.assertEqual(workflow.verification_plan(
            [immutable], task["verification_runs"], source_revision=REVISION,
            environment="local", platform="darwin-arm64", input_digests={"full-suite": DIGEST},
        )[0]["action"], "run")
        duplicate = verification_run("run-2")
        task["verification_runs"].append(duplicate)
        self.assert_invalid(task, "repeats an unchanged passed check")
        duplicate["invalidation_reason"] = "fixture contamination diagnosed after first run"
        workflow.validate_record(task, profile=repository_profile)

    def test_verification_concurrency_requires_distinct_state_and_capacity(self) -> None:
        task = task_run()
        first = verification_run()
        first.update(overlap_group="group-1", isolation_refs=["db-a"], capacity_evidence_ref="capacity-check")
        second = verification_run("run-2")
        second.update(check_id="browser", overlap_group="group-1", isolation_refs=["db-a"], capacity_evidence_ref="capacity-check")
        task["verification_runs"] = [first, second]
        self.assert_invalid(task, "share mutable state")
        second["isolation_refs"] = ["db-b"]
        workflow.validate_record(task)
        second["capacity_evidence_ref"] = ""
        self.assert_invalid(task, "capacity_evidence_ref")

    def test_cost_profile_uses_measured_samples_and_rejects_invalid_timings(self) -> None:
        samples = {
            "id": "library-suite", "command": "python -m unittest",
            "claim_refs": ["library"], "required_gate": True,
            "mutable_resources": [], "reuse_policy": "immutable", "evidence_ref": "ci-history",
            "samples": [
                {"setup_seconds": 2, "run_seconds": 10, "measured_at": "2026-09-25T00:00:00Z"},
                {"setup_seconds": 4, "run_seconds": 12, "measured_at": "2026-09-26T00:00:00Z"},
                {"setup_seconds": 6, "run_seconds": 20, "measured_at": "2026-09-27T00:00:00Z"},
            ],
        }
        cost = workflow.profile_check(samples)
        self.assertEqual((cost["setup_seconds"], cost["median_seconds"], cost["p95_seconds"]), (4, 12, 20))
        samples["samples"][0]["run_seconds"] = -1
        with self.assertRaisesRegex(workflow.RecordError, "must be non-negative"):
            workflow.profile_check(samples)

    def test_external_work_distinguishes_saved_from_flow_verified(self) -> None:
        task = task_run()
        saved = provider_step("provider", state="saved")
        flow = provider_step("login", state="pending")
        flow["dependencies"] = ["provider"]
        task["external_work"] = {
            "source_routes": [{
                "id": "api", "target": "requirements-document", "source_identity": "document-1",
                "channel": "connector", "authorization_ref": "user-authorized-source",
                "state": "failed", "failure_class": "authentication_redirect",
                "checked_at": "2026-09-27T00:00:00Z", "evidence_ref": "redirect-observation",
            }, {
                "id": "browser", "target": "requirements-document", "source_identity": "document-1",
                "channel": "signed-in-chrome", "authorization_ref": "user-authorized-browser",
                "state": "verified", "failure_class": "", "checked_at": "2026-09-27T00:05:00Z",
                "evidence_ref": "same-source-readback",
            }],
            "provider_steps": [saved, flow],
            "artifact_checks": [],
        }
        workflow.validate_record(task)
        recovery = workflow.source_recovery_plan(task["external_work"], target="requirements-document", source_identity="document-1")
        self.assertEqual((recovery["action"], recovery["route_id"]), ("use_verified", "browser"))
        self.assertEqual(workflow.source_recovery_plan(task["external_work"], target="requirements-document", source_identity="other-document")["action"], "blocked")
        self.assertEqual(workflow.next_external_step(task["external_work"])["id"], "provider")
        with self.assertRaisesRegex(workflow.RecordError, "provider lacks flow verification"):
            workflow.validate_record(task, require_final=True)
        saved["state"] = "flow_verified"
        for stage in ("read_back", "flow_verified"):
            saved["observations"].append({"stage": stage, "checked_at": "2026-09-27T00:10:00Z", "evidence_ref": f"{stage}-evidence"})
        saved.update(evidence_ref="flow_verified-evidence", checked_at="2026-09-27T00:10:00Z")
        flow.update(state="flow_verified", observations=[
            {"stage": "read_back", "checked_at": "2026-09-27T00:10:00Z", "evidence_ref": "callback-readback"},
            {"stage": "flow_verified", "checked_at": "2026-09-27T00:11:00Z", "evidence_ref": "staging-login-result"},
        ], evidence_ref="staging-login-result", checked_at="2026-09-27T00:11:00Z")
        task["external_work"]["artifact_checks"] = [{
            "id": "copy", "source_ref": "requirements-document", "artifact_ref": "requirements.md",
            "source_units": ["page-1", "page-2"], "verified_units": ["page-1"],
            "state": "pending", "required": True, "evidence_ref": "",
        }]
        with self.assertRaisesRegex(workflow.RecordError, "artifact check copy is unverified"):
            workflow.validate_record(task, require_final=True)
        task["external_work"]["artifact_checks"][0].update(state="verified", evidence_ref="section-comparison")
        with self.assertRaisesRegex(workflow.RecordError, "does not cover every source unit"):
            workflow.validate_record(task, require_final=True)
        task["external_work"]["artifact_checks"][0]["verified_units"].append("page-2")
        workflow.validate_record(task, require_final=True)
        self.assertIsNone(workflow.next_external_step(task["external_work"]))

    def test_stale_session_recovery_and_external_ledger_rejects_secrets(self) -> None:
        task = task_run()
        task["external_work"] = {
            "source_routes": [{
                "id": "old-session", "target": "task-sheet", "source_identity": "sheet-1",
                "channel": "browser", "authorization_ref": "user-authorized-browser",
                "state": "failed", "failure_class": "stale_session",
                "checked_at": "2026-09-27T00:00:00Z", "evidence_ref": "session-expired",
            }, {
                "id": "signed-in-tab", "target": "task-sheet", "source_identity": "sheet-1",
                "channel": "signed-in-browser", "authorization_ref": "user-authorized-browser",
                "state": "available", "failure_class": "", "checked_at": "2026-09-27T00:05:00Z",
                "evidence_ref": "tab-seen",
            }],
            "provider_steps": [], "artifact_checks": [],
        }
        workflow.validate_record(task)
        recovery = workflow.source_recovery_plan(task["external_work"], target="task-sheet", source_identity="sheet-1")
        self.assertEqual((recovery["action"], recovery["route_id"]), ("check_authorized_route", "signed-in-tab"))
        task["external_work"]["source_routes"][1]["token"] = "sensitive"
        self.assert_invalid(task, "secret-bearing field")

    def test_templates_and_cli_support_continuity_fields(self) -> None:
        skill_root = SCRIPT.parents[1]
        schema = json.loads((skill_root / "schemas" / "standard-workflow-v1.schema.json").read_text())
        for template_name in ("task-run.json", "repository-capability-profile.json"):
            template = json.loads((skill_root / "templates" / template_name).read_text())
            jsonschema.validate(template, schema)
            workflow.validate_record(template)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = root / "task.json"
            update_path = root / "update.json"
            task_path.write_text(json.dumps(task_run()))
            update_path.write_text(json.dumps({
                "id": "issue", "kind": "issue_first", "state": "required",
                "authority": "explicit", "source_ref": "turn-1",
                "target": "tracking issue", "proof_source": "live GitHub issue state",
            }))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "contract-update", str(task_path), str(update_path)],
                capture_output=True, text=True, check=True,
            )
            updated = json.loads(result.stdout)
            self.assertEqual(updated["delivery_contract"]["requirements"][0]["kind"], "issue_first")
            task_path.write_text(result.stdout)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "next-external", str(task_path)],
                capture_output=True, text=True, check=True,
            )
            self.assertIsNone(json.loads(result.stdout))

    def test_pattern_wide_inventory_requires_every_discovered_surface(self) -> None:
        task = task_run()
        task["impact_inventory"] = impact_inventory()
        workflow.validate_record(task, require_final=True)
        task["impact_inventory"]["surfaces"].pop()
        self.assert_invalid(task, "omits or duplicates a discovered surface")
        task = task_run()
        task["impact_inventory"] = impact_inventory()
        task["impact_inventory"]["surfaces"][1]["verification_refs"] = []
        self.assert_invalid(task, "lacks final verification")
        task = task_run()
        task["impact_inventory"] = impact_inventory()
        task["impact_inventory"]["surfaces"][1]["verification_refs"] = ["unknown"]
        self.assert_invalid(task, "references unknown verification")
        task = task_run()
        task["impact_inventory"] = impact_inventory()
        task["impact_inventory"]["surfaces"][1]["verification_refs"] = ["complete"]
        workflow.validate_record(task, require_final=True)

    def test_pattern_inventory_catches_relationship_and_viewport_omissions(self) -> None:
        for kind, missing_id in (
            ("relationship_field", "platform-recipient"),
            ("viewport", "wide-desktop"),
        ):
            with self.subTest(kind=kind):
                task = task_run()
                inventory = impact_inventory()
                inventory["discovered_surface_ids"].append(missing_id)
                task["impact_inventory"] = inventory
                self.assert_invalid(task, "omits or duplicates a discovered surface")
                inventory["surfaces"].append(
                    {
                        "id": missing_id,
                        "kind": kind,
                        "decision": "included",
                        "reason": "Requested across the shared pattern.",
                        "shared_point": "shared-control",
                        "verification_refs": ["complete"],
                    }
                )
                workflow.validate_record(task, require_final=True)

    def test_diagnosis_keeps_missing_trace_and_unproven_cause_distinct(self) -> None:
        task = task_run()
        task["diagnostics"] = [diagnostic(trace_state="missing")]
        workflow.validate_record(task)
        task["diagnostics"][0]["root_cause_state"] = "proven"
        task["diagnostics"][0]["root_cause_evidence_refs"] = ["guess"]
        task["diagnostics"][0]["reproduction_ref"] = "synthetic-replay"
        self.assert_invalid(task, "missing trace cannot prove")
        task = task_run()
        task["diagnostics"] = [diagnostic()]
        task["diagnostics"][0]["root_cause_state"] = "proven"
        self.assert_invalid(task, "lacks root-cause evidence")
        task["diagnostics"][0]["root_cause_evidence_refs"] = ["synthetic-log-1"]
        task["diagnostics"][0]["reproduction_ref"] = "synthetic-replay"
        workflow.validate_record(task)
        task["diagnostics"][0]["resolution_state"] = "fixed"
        self.assert_invalid(task, "remedy_verification_ref")
        task["diagnostics"][0]["remedy_verification_ref"] = "same-path-replay"
        workflow.validate_record(task)
        task["diagnostics"][0]["trace_policy"]["retention_seconds"] = 0
        self.assert_invalid(task, "positive limit")
        task = task_run()
        task["diagnostics"] = [diagnostic(trace_state="missing")]
        task["diagnostics"][0]["resolution_state"] = "mitigated"
        task["diagnostics"][0]["remedy_verification_ref"] = "user-facing-retry-state"
        workflow.validate_record(task)

    def test_synthetic_runtime_cases_preserve_distinct_operations(self) -> None:
        for operation_name, symptom in (
            ("analysis.sql.execute", "Generated query failed"),
            ("provider.request", "429 with retry-after"),
            ("table.next_page", "Cursor repeated without scrolling"),
            ("broker.resolve_symbol", "Production symbol mismatch"),
            ("service.load_config", "Environment-only configuration failure"),
        ):
            with self.subTest(operation=operation_name):
                task = task_run()
                incident = diagnostic()
                incident["operation"] = operation_name
                incident["symptom"] = symptom
                task["diagnostics"] = [incident]
                workflow.validate_record(task)

    def test_availability_requires_live_revision_mode_and_flow(self) -> None:
        task = task_run()
        task["release_readback"] = release_readback()
        self.assert_invalid(task, "must declare critical invariant applicability")
        task["release_invariants"] = {
            "applicability": "not_applicable", "reason": "Stateless test release.",
            "baseline_ref": "", "rollback_ref": "", "checks": [],
        }
        workflow.validate_record(task, require_final=True)
        for field, value, message in (
            ("active_revision", "stale", "revision differs"),
            ("active_mode", "dev", "wrong start mode"),
            ("health", "not_checked", "live health"),
            ("user_flow", "failed", "user-flow proof"),
            ("handle_state", "stopped", "not live"),
        ):
            with self.subTest(field=field):
                changed = task_run()
                changed["release_readback"] = release_readback()
                changed["release_readback"][field] = value
                self.assert_invalid(changed, message)
        public = task_run()
        public["release_readback"] = release_readback(target_surface="public")
        public["release_readback"]["public_reachable"] = False
        self.assert_invalid(public, "public reachability")
        public["release_readback"]["public_reachable"] = True
        public["release_invariants"] = task["release_invariants"]
        workflow.validate_record(public)
        summary = workflow.summarize(public)
        self.assertIn("Target surface: `public`", summary)
        self.assertIn(f"Active revision: `{REVISION}`", summary)

    def test_available_readback_is_bound_to_merged_revision_and_valid_live_location(self) -> None:
        for field, value, message in (
            ("intended_revision", "other", "revision differs"),
            ("target_url", "relative/path", "absolute HTTP URL"),
            ("observed_at", "yesterday", "ISO timestamp"),
            ("observed_at", "2026-09-27T00:00:00", "needs a timezone"),
        ):
            with self.subTest(field=field, value=value):
                task = task_run()
                task["release_readback"] = release_readback()
                task["release_readback"][field] = value
                self.assert_invalid(task, message)
        task = task_run()
        task["release_readback"] = release_readback()
        task["release_readback"]["intended_revision"] = "other"
        task["release_readback"]["active_revision"] = "other"
        self.assert_invalid(task, "not bound to the merged revision")
        task["release_readback"]["merged_revision"] = "other"
        task["release_invariants"] = {
            "applicability": "not_applicable", "reason": "Stateless test release.",
            "baseline_ref": "", "rollback_ref": "", "checks": [],
        }
        workflow.validate_record(task)

    def test_additive_schema_covers_new_record_sections(self) -> None:
        skill_root = SCRIPT.parents[1]
        schema = json.loads(
            (skill_root / "schemas" / "standard-workflow-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema)
        template = json.loads(
            (skill_root / "templates" / "task-run.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(template)
        broken = copy.deepcopy(template)
        broken["release_readback"].pop("active_revision")
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(broken)))

    def test_release_stages_do_not_imply_availability(self) -> None:
        for state in ("pr_open", "merged", "deployed_unverified", "blocked"):
            with self.subTest(state=state):
                task = task_run()
                readback = release_readback()
                readback["state"] = state
                readback["active_revision"] = ""
                readback["health"] = "not_checked"
                readback["user_flow"] = "not_checked"
                task["release_readback"] = readback
                workflow.validate_record(task)
                self.assertIn(f"Release state: `{state}`", workflow.summarize(task))


if __name__ == "__main__":
    unittest.main()
