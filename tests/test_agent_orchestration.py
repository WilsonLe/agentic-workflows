from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import io
import importlib.util
import json
import os
import stat
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agent-orchestration"
SCRIPT = PLUGIN / "scripts" / "orchestration_state.py"
SPEC = importlib.util.spec_from_file_location("orchestration_state", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
orchestration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orchestration)

TIMESTAMP = "2026-07-30T08:00:00Z"
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
DIGEST_C = "c" * 64
GOAL_CONTRACT = {
    "objective": "Deliver issue #91 through its defined terminal outcome.",
    "project_boundary": "project-example issue #91 only.",
    "completion_conditions": "Required code, checks, and issue reconciliation complete.",
    "constraints": "Remain within the trusted issue authority and preserve safety gates.",
}


def task(
    thread_id: str,
    *,
    project_id: str = "project-example",
    status: str = "active",
    title: str | None = None,
) -> dict[str, object]:
    return orchestration.default_task(
        thread_id=thread_id,
        project_id=project_id,
        status=status,
        observed_at=TIMESTAMP,
        host_id="local",
        title=title or f"Task {thread_id} | working",
    )


def issue_session(
    thread_id: str,
    *,
    status: str = "active",
    issue_number: int = 88,
    pr_number: int | None = None,
) -> dict[str, object]:
    return orchestration.default_task(
        thread_id=thread_id,
        project_id="project-example",
        status=status,
        observed_at=TIMESTAMP,
        host_id="local",
        title=f"Issue #{issue_number} | working",
        issue_number=issue_number,
        pr_number=pr_number,
        run_mode="issue_session",
        worktree_path=f"/workspace/example.worktrees/issue-{issue_number}",
        branch_name=f"codex/issue-{issue_number}",
        base_revision="0123456789abcdef0123456789abcdef01234567",
    )


def launch(
    *,
    issue_number: int = 91,
    goal_contract: dict[str, str] | None = None,
) -> dict[str, object]:
    return orchestration.default_launch(
        issue_number=issue_number,
        goal_contract=goal_contract or GOAL_CONTRACT,
        observed_at=TIMESTAMP,
    )


def review_session(
    thread_id: str,
    *,
    status: str = "active",
    outcome: str = "pending",
    issue_number: int = 88,
    pr_number: int | None = None,
    target_revision: str = "89abcdef0123456789abcdef0123456789abcdef",
) -> dict[str, object]:
    return orchestration.default_task(
        thread_id=thread_id,
        project_id="project-example",
        status=status,
        observed_at=TIMESTAMP,
        host_id="local",
        title=f"Issue #{issue_number} | review",
        issue_number=issue_number,
        pr_number=pr_number,
        run_mode="review_session",
        worktree_path=f"/workspace/example.worktrees/issue-{issue_number}",
        base_revision="0123456789abcdef0123456789abcdef01234567",
        subject_thread_id=f"thread-{issue_number}",
        target_revision=target_revision,
        review_outcome=outcome,
        effective_model=orchestration.LUNA_MODEL,
        effective_reasoning_effort=orchestration.MAX_REASONING_EFFORT,
        settings_verification_state="verified",
    )


def verification_session(
    thread_id: str,
    *,
    status: str = "active",
    outcome: str = "pending",
    issue_number: int = 88,
    target_revision: str = "89abcdef0123456789abcdef0123456789abcdef",
) -> dict[str, object]:
    return orchestration.default_task(
        thread_id=thread_id,
        project_id="project-example",
        status=status,
        observed_at=TIMESTAMP,
        host_id="local",
        title=f"Issue #{issue_number} | testing",
        issue_number=issue_number,
        run_mode="verification_session",
        worktree_path=f"/workspace/example.worktrees/issue-{issue_number}",
        base_revision="0123456789abcdef0123456789abcdef01234567",
        subject_thread_id=f"thread-{issue_number}",
        target_revision=target_revision,
        review_outcome=outcome,
        effective_model=orchestration.LUNA_MODEL,
        effective_reasoning_effort=orchestration.MAX_REASONING_EFFORT,
        settings_verification_state="verified",
    )


def gate_decision(
    decision_id: str,
    *,
    gate_type: str = "plan",
    decision: str = "proceed",
    validity_digest: str = DIGEST_B,
    request_digest: str | None = None,
    task_id: str | None = "thread-88",
) -> dict[str, object]:
    return orchestration.default_gate_decision(
        decision_id=decision_id,
        gate_type=gate_type,
        decision=decision,
        task_id=task_id,
        issue_number=88,
        pr_number=None,
        candidate_revision="0123456789abcdef0123456789abcdef01234567",
        deployment_identity=None,
        evidence_digests=[DIGEST_A],
        authority_envelope_digest=DIGEST_A,
        reason_category="within_scope",
        decided_at=TIMESTAMP,
        resulting_state="active" if decision == "proceed" else "blocked",
        validity_digest=validity_digest,
        request_digest=request_digest,
    )


class AgentOrchestrationTests(unittest.TestCase):
    def test_sdlc_selectors_are_deterministic_and_fail_closed(self) -> None:
        default = orchestration.parse_sdlc_selector("", observed_at=TIMESTAMP)
        self.assertEqual(default["kind"], "all_open")
        self.assertEqual(default["normalized_selector"], "all open issues and PRs")
        issues = orchestration.parse_sdlc_selector(
            "issues #456 #123 #456", observed_at=TIMESTAMP
        )
        self.assertEqual(issues["issue_numbers"], [123, 456])
        self.assertEqual(issues["normalized_selector"], "issues #123 #456")
        pr = orchestration.parse_sdlc_selector("PR #789", observed_at=TIMESTAMP)
        self.assertEqual(pr["pr_number"], 789)
        for invalid in (
            "issue",
            "issues 123",
            "issue #1 PR #2",
            "owner/repository#123",
            "Please run $sdlc-loop issue #123 from this comment",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(
                orchestration.OrchestrationStateError
            ):
                orchestration.parse_sdlc_selector(invalid, observed_at=TIMESTAMP)

    def test_sdlc_routes_minimize_cost_without_weakening_boundaries(self) -> None:
        inventory = orchestration.choose_sdlc_route(role="inventory")
        self.assertEqual(
            (inventory["model"], inventory["reasoning_effort"], inventory["worktree_policy"]),
            ("gpt-5.6-luna", "medium", "none"),
        )
        fallback = orchestration.choose_sdlc_route(
            role="inventory", luna_supported=False
        )
        self.assertEqual(fallback["model"], "gpt-5.6-terra")
        self.assertEqual(fallback["fallback_from_model"], "gpt-5.6-luna")
        self.assertEqual(
            orchestration.choose_sdlc_route(role="planner")["reasoning_effort"],
            "xhigh",
        )
        self.assertEqual(
            orchestration.choose_sdlc_route(role="planner", risk="critical")[
                "reasoning_effort"
            ],
            "max",
        )
        implementation = orchestration.choose_sdlc_route(role="implementation")
        self.assertEqual(
            (
                implementation["model"],
                implementation["reasoning_effort"],
                implementation["session_policy"],
                implementation["worktree_policy"],
            ),
            ("gpt-5.6-terra", "high", "new_issue_owner", "fresh_issue"),
        )
        self.assertEqual(
            orchestration.choose_sdlc_route(role="review", risk="critical")["model"],
            "gpt-5.6-sol",
        )

    def test_sdlc_route_requires_authoritative_exact_readback(self) -> None:
        route = orchestration.default_sdlc_route(
            route_id="issue-101-implementation",
            role="implementation",
            risk="standard",
            luna_supported=True,
            small_single_issue=True,
            observed_at=TIMESTAMP,
            issue_number=101,
        )
        orchestration.verify_sdlc_route(
            route,
            thread_id="thread-101",
            host_id="local",
            effective_model="gpt-5.6-terra",
            effective_reasoning_effort="high",
            effective_worktree_policy="none",
            observed_at="2026-07-30T08:01:00Z",
        )
        self.assertEqual(route["verification_state"], "blocked")
        self.assertEqual(route["blocker_category"], "worktree_mismatch")

    def test_issue_specific_sdlc_routes_require_candidate_binding(self) -> None:
        for role in ("planner", "implementation", "remediation"):
            with self.subTest(role=role), self.assertRaisesRegex(
                orchestration.OrchestrationStateError, "requires issue_number"
            ):
                orchestration.default_sdlc_route(
                    route_id=f"unbound-{role}",
                    role=role,
                    risk="standard",
                    luna_supported=True,
                    small_single_issue=False,
                    observed_at=TIMESTAMP,
                )
        for role in ("review", "verification", "delivery"):
            with self.subTest(role=role), self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "requires issue_number or pr_number",
            ):
                orchestration.default_sdlc_route(
                    route_id=f"unbound-{role}",
                    role=role,
                    risk="standard",
                    luna_supported=True,
                    small_single_issue=False,
                    observed_at=TIMESTAMP,
                )

    def test_sdlc_skill_is_direct_delivery_focused_and_repository_agnostic(self) -> None:
        skill = (
            PLUGIN / "skills" / "sdlc-loop" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Explicit `$sdlc-loop` invocation immediately designates",
            "This is a delivery command, not a portfolio-reporting command.",
            "maximum two passes",
            "pull -> deploy target -> verify target",
            "The workflow is repository-agnostic.",
            "`gpt-5.6-luna` / `medium`",
            "`gpt-5.6-sol` / `xhigh`",
            "`gpt-5.6-terra` / `high`",
            "New detached exact-head worktree",
            "continue without routine human approval",
        ):
            self.assertIn(marker, skill)

        standard = (
            PLUGIN.parent
            / "agentic-workflows"
            / "skills"
            / "standard-development-workflow"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("generic Standard\nDevelopment Workflow autopilot delivery profile", standard)
        self.assertIn("schema-v7 register", standard)

    def test_example_register_and_schema_metadata_are_valid(self) -> None:
        example = json.loads(
            (PLUGIN / "examples" / "register.json").read_text(encoding="utf-8")
        )
        orchestration.validate_register(example)
        schema_v3 = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v3.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema_v3["properties"]["schema_version"]["const"], 3)
        self.assertIn("task", schema_v3["$defs"])
        Draft202012Validator.check_schema(schema_v3)
        schema = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v4.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 4)
        self.assertIn("launch", schema["$defs"])
        self.assertIn("task", schema["$defs"])
        Draft202012Validator.check_schema(schema)
        schema_v5 = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v5.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema_v5["properties"]["schema_version"]["const"], 5)
        self.assertIn("state_revision", schema_v5["properties"])
        self.assertIn("remediationTurn", schema_v5["$defs"])
        Draft202012Validator.check_schema(schema_v5)
        schema_v6 = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v6.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema_v6["properties"]["schema_version"]["const"], 6)
        self.assertIn("sdlc_scope", schema_v6["properties"])
        self.assertIn("routing_decisions", schema_v6["properties"])
        Draft202012Validator.check_schema(schema_v6)
        schema_v7 = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v7.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema_v7["properties"]["schema_version"]["const"], 7)
        self.assertIn("delegatedGoal", schema_v7["$defs"])
        Draft202012Validator.check_schema(schema_v7)
        validator = Draft202012Validator(schema_v7)
        validator.validate(example)
        claim_schema = json.loads(
            (
                PLUGIN
                / "schemas"
                / "worktree-claim-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        claim_example = json.loads(
            (
                PLUGIN
                / "examples"
                / "worktree-claim.json"
            ).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(claim_schema)
        Draft202012Validator(claim_schema).validate(claim_example)
        invalid = copy.deepcopy(example)
        invalid["tasks"][2]["branch_name"] = "review-must-be-detached"
        with self.assertRaises(ValidationError):
            validator.validate(invalid)
        invalid_remediation = copy.deepcopy(example)
        invalid_remediation["tasks"][0]["remediation_turn"] = {
            "turn_id": "failed-readback",
            "requested_model": "gpt-5.6-luna",
            "effective_model": "gpt-5.6-luna",
            "requested_reasoning_effort": "max",
            "effective_reasoning_effort": "high",
            "verification_state": "blocked",
            "blocker_category": "reasoning_mismatch",
        }
        with self.assertRaises(ValidationError):
            validator.validate(invalid_remediation)
        for run_mode in ("review_session", "verification_session"):
            invalid_non_issue = copy.deepcopy(example)
            non_issue_index = next(
                index
                for index, item in enumerate(invalid_non_issue["tasks"])
                if item["run_mode"] == run_mode
            )
            invalid_non_issue["tasks"][non_issue_index]["remediation_turn"] = {}
            with self.subTest(run_mode=run_mode):
                with self.assertRaises(ValidationError):
                    validator.validate(invalid_non_issue)
                with self.assertRaises(orchestration.OrchestrationStateError):
                    orchestration.validate_register(invalid_non_issue)

    def test_schema_v6_acceptance_and_v5_migration_preserve_runtime_fields(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        register["sdlc_scope"] = orchestration.parse_sdlc_selector(
            "issues #99 #100",
            observed_at=TIMESTAMP,
        )
        register["routing_decisions"] = [
            orchestration.default_sdlc_route(
                route_id="issue-99-implementation",
                role="implementation",
                risk="standard",
                luna_supported=True,
                small_single_issue=False,
                observed_at=TIMESTAMP,
                issue_number=99,
            )
        ]
        legacy_v6 = copy.deepcopy(register)
        legacy_v6["schema_version"] = 6
        legacy_v6.pop("state_revision")
        legacy_task = task("thread-v6")
        for field in orchestration.TASK_EXTENSION_KEYS:
            legacy_task.pop(field)
        legacy_v6["tasks"] = [legacy_task]
        migrated_v6 = orchestration.migrate_register(legacy_v6)
        self.assertEqual(migrated_v6["schema_version"], 7)
        self.assertEqual(migrated_v6["state_revision"], 0)
        self.assertEqual(
            migrated_v6["sdlc_scope"]["normalized_selector"],
            "issues #99 #100",
        )
        self.assertEqual(
            migrated_v6["routing_decisions"][0]["route_id"],
            "issue-99-implementation",
        )
        self.assertEqual(
            set(migrated_v6["tasks"][0]),
            orchestration.TASK_KEYS,
        )

        legacy_v5 = copy.deepcopy(register)
        legacy_v5["schema_version"] = 5
        legacy_v5.pop("sdlc_scope")
        legacy_v5.pop("routing_decisions")
        legacy_v5["state_revision"] = 7
        migrated_v5 = orchestration.migrate_register(legacy_v5)
        self.assertEqual(migrated_v5["schema_version"], 7)
        self.assertEqual(migrated_v5["state_revision"], 7)
        self.assertIsNone(migrated_v5["sdlc_scope"])
        self.assertEqual(migrated_v5["routing_decisions"], [])

    def test_schema_valid_v7_gate_identifier_ids_load_through_runtime(self) -> None:
        schema = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v7.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 7)
        self.assertEqual(schema["properties"]["decision_policy"]["const"], "autopilot")
        self.assertIn("gateDecision", schema["$defs"])
        self.assertIn("launch", schema["$defs"])
        self.assertIn("task", schema["$defs"])
        example = json.loads((PLUGIN / "examples" / "register.json").read_text())
        Draft202012Validator(schema).validate(example)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        decision_ids = ("9:gate", "a" * 199 + ":", "9" + "a" * 199)

        with tempfile.TemporaryDirectory() as directory:
            for index, decision_id in enumerate(decision_ids):
                with self.subTest(decision_id=decision_id):
                    register = orchestration.new_register(
                        "project-example",
                        "orchestrator",
                        timestamp=TIMESTAMP,
                    )
                    register["state_revision"] = 7
                    register["gate_decisions"] = [
                        {
                            "decision_id": decision_id,
                            "gate_type": "implementation",
                            "decision": "proceed",
                            "task_id": None,
                            "issue_number": None,
                            "pr_number": None,
                            "candidate_revision": None,
                            "deployment_identity": None,
                            "evidence_digests": ["a" * 64],
                            "authority_envelope_digest": "b" * 64,
                            "reason_category": "operator",
                            "decided_at": TIMESTAMP,
                            "resulting_state": "active",
                            "validity_digest": "c" * 64,
                            "request_digest": None,
                            "invalidated_at": None,
                        }
                    ]
                    validator.validate(register)
                    path = Path(directory) / f"register-{index}.json"
                    path.write_text(json.dumps(register), encoding="utf-8")
                    path.chmod(stat.S_IRUSR | stat.S_IWUSR)

                    loaded = orchestration.load_register(path)

                    self.assertEqual(loaded["state_revision"], 7)
                    self.assertEqual(
                        loaded["gate_decisions"][0]["decision_id"],
                        decision_id,
                    )

    def test_sdlc_cli_commands_parse_and_persist_routing(self) -> None:
        def invoke(arguments: list[str]) -> dict[str, object]:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = orchestration.main(arguments)
            self.assertEqual(result, 0, stderr.getvalue())
            return json.loads(stdout.getvalue())

        selector = invoke(
            [
                "parse-selector",
                "--selector",
                "issues #100 #99",
                "--observed-at",
                TIMESTAMP,
            ]
        )
        self.assertEqual(selector["normalized_selector"], "issues #99 #100")
        profile = invoke(["route-profile", "--role", "verification"])
        self.assertEqual(profile["model"], "gpt-5.6-luna")
        self.assertEqual(profile["worktree_policy"], "detached_exact_head")

        with tempfile.TemporaryDirectory() as directory:
            common = [
                "--project-id",
                "project-example",
                "--orchestrator-id",
                "orchestrator",
                "--state-root",
                str(Path(directory) / "state"),
            ]
            invoke(["init", *common])
            route = invoke(
                [
                    "route-request",
                    *common,
                    "--route-id",
                    "issue-99-verification",
                    "--role",
                    "verification",
                    "--issue-number",
                    "99",
                    "--observed-at",
                    TIMESTAMP,
                ]
            )
            self.assertEqual(route["verification_state"], "requested")
            verified = invoke(
                [
                    "route-verify",
                    *common,
                    "--route-id",
                    "issue-99-verification",
                    "--thread-id",
                    "thread-verification-99",
                    "--host-id",
                    "host-local",
                    "--effective-model",
                    "gpt-5.6-luna",
                    "--effective-reasoning-effort",
                    "high",
                    "--effective-worktree-policy",
                    "detached_exact_head",
                    "--observed-at",
                    TIMESTAMP,
                ]
            )
            self.assertEqual(verified["verification_state"], "verified")

    def test_goal_mode_contract_requires_clarity_and_announcement(self) -> None:
        activation = (
            PLUGIN
            / "skills"
            / "orchestration"
            / "references"
            / "activation-and-goal-mode.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Inspect current goal state",
            "stop before goal creation",
            "Control-plane mode always runs in autopilot",
            "sanitized\n`goal_scope` decision",
            "Goal is clear. I have no further questions.",
            "Omit `token_budget`",
            "after context compaction",
            "Mark it blocked only after the same blocking condition",
            "Goal Mode increases persistence, not authority",
            "ordinary delivery authority envelope",
            "Production must be directly named",
        ):
            self.assertIn(marker, activation)

    def test_activation_description_distinguishes_explicit_and_ambiguous_use(self) -> None:
        skill = (
            PLUGIN / "skills" / "orchestration" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("explicit operator designation", skill)
        self.assertIn("main branch", skill)
        self.assertIn("Never create subagents", skill)
        self.assertIn("project worktree", skill)
        self.assertIn("never performs code review itself", skill)
        self.assertIn("exact implementation worktree", skill)
        self.assertIn("gpt-5.6-luna", skill)
        self.assertIn("test-and-verification task", skill)
        self.assertIn("Never share a writable worktree concurrently", skill)
        self.assertIn("does not claim independent code review", skill)
        self.assertIn("ordinary delivery actions", skill)

    def test_control_plane_preserves_parent_main_merge_approval(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        self.assertEqual(register["decision_policy"], "autopilot")
        for invalid_policy in (None, "manual", "disabled", "unknown"):
            invalid = copy.deepcopy(register)
            invalid["decision_policy"] = invalid_policy
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "must always be autopilot",
            ):
                orchestration.validate_register(invalid)

        skill_root = PLUGIN / "skills" / "orchestration"
        managed_contract = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                skill_root / "SKILL.md",
                skill_root / "references" / "activation-and-goal-mode.md",
                skill_root / "references" / "delegated-session-launch-settings.md",
                skill_root / "references" / "issue-session-lifecycle.md",
                skill_root / "references" / "review-session-lifecycle.md",
                skill_root / "references" / "coordination-and-waiting.md",
                skill_root / "references" / "closeout-archive-recovery.md",
            )
        )
        for forbidden in (
            "ask only the smallest necessary operator questions",
            "ask the operator for direction",
            "request an explicit operator decision",
            "ask for clarification when multiple records match",
        ):
            self.assertNotIn(forbidden, managed_contract)
        for marker in (
            "do not ask for routine phase approvals",
            "Never\nforward or relay a routine decision request to the operator",
            "Do not pause for a new\napproval at each of those steps",
            "Production is allowed only\nby that direct trusted production scope",
            "Ask for explicit user approval to merge the parent branch\nthrough that PR",
        ):
            self.assertIn(marker, managed_contract)

    def test_standard_workflow_preserves_ordinary_gates_and_substitutes_verified_autopilot(self) -> None:
        workflow_root = (
            ROOT
            / "plugins"
            / "agentic-workflows"
            / "skills"
            / "standard-development-workflow"
        )
        skill = (workflow_root / "SKILL.md").read_text(encoding="utf-8")
        contracts = (
            workflow_root / "references" / "stage-contracts.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "The ordinary workflow below retains every human approval gate",
            "decision_policy=autopilot",
            "unvalidated record never establishes this context",
            "capture one trusted authority envelope",
            "all ordinary human gates below remain mandatory",
        ):
            self.assertIn(marker, skill + contracts)
        self.assertIn("Deployment needs explicit approval in an ordinary task", skill)
        self.assertIn("declared-target authority without a routine approval pause", skill)

    def test_autopilot_authority_is_end_to_end_and_records_are_sparse(self) -> None:
        skill_root = PLUGIN / "skills" / "orchestration"
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                skill_root / "SKILL.md",
                skill_root / "references" / "activation-and-goal-mode.md",
                skill_root / "references" / "coordination-register.md",
                PLUGIN / "skills" / "sdlc-loop" / "SKILL.md",
            )
        )
        for marker in (
            "commit, push, PR, merge, canonical pull",
            "deployment plus verification to the declared target",
            "Do not record per-command",
            "Production must be directly named",
            "block only when the missing control prevents required work",
        ):
            self.assertIn(marker, combined)

    def test_extra_sessions_and_review_are_proportionate(self) -> None:
        skill_root = PLUGIN / "skills" / "orchestration"
        launch = (
            skill_root / "references" / "delegated-session-launch-settings.md"
        ).read_text(encoding="utf-8")
        review = (
            skill_root / "references" / "review-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        issue = (
            skill_root / "references" / "issue-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        self.assertIn("required for every delegated session", launch)
        self.assertIn("proportionate automated checks", review)
        self.assertIn("current control-plane task may own", issue)
        self.assertIn("Never emulate a host setting with\nprompt text", issue)

    def test_gate_decisions_cover_all_outcomes_and_fail_closed(self) -> None:
        for index, outcome in enumerate(sorted(orchestration.GATE_DECISIONS)):
            record = gate_decision(
                f"decision-{index}",
                gate_type=sorted(orchestration.GATE_TYPES)[index],
                decision=outcome,
            )
            self.assertEqual(record["decision"], outcome)
        for invalid_outcome in ("approve", "ignore", "ask_user"):
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "decision is unsupported",
            ):
                gate_decision("invalid", decision=invalid_outcome)

    def test_spawned_request_is_deduplicated_and_never_redecided(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        first = gate_decision(
            "request-1",
            gate_type="spawned_request",
            decision="blocked",
            request_digest=DIGEST_C,
        )
        recorded = orchestration.record_gate_decision(register, first)
        duplicate = copy.deepcopy(first)
        duplicate["decision_id"] = "request-duplicate"
        self.assertEqual(
            orchestration.record_gate_decision(register, duplicate),
            recorded,
        )
        self.assertEqual(len(register["gate_decisions"]), 1)
        conflicting = copy.deepcopy(duplicate)
        conflicting["decision"] = "proceed"
        conflicting["resulting_state"] = "active"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "different bounded decision",
        ):
            orchestration.record_gate_decision(register, conflicting)

    def test_gate_evidence_drift_invalidates_prior_decision(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        orchestration.record_gate_decision(register, gate_decision("plan-v1"))
        changed = gate_decision(
            "plan-v2",
            decision="revise",
            validity_digest=DIGEST_C,
        )
        orchestration.record_gate_decision(register, changed)
        by_id = {item["decision_id"]: item for item in register["gate_decisions"]}
        self.assertEqual(by_id["plan-v1"]["invalidated_at"], TIMESTAMP)
        self.assertIsNone(by_id["plan-v2"]["invalidated_at"])

    def test_autopilot_decision_matrix_fails_closed_at_material_boundaries(self) -> None:
        baseline = {
            "in_goal": True,
            "authority_available": True,
            "credentials_available": True,
            "required_evidence": "passed",
            "safe_path_available": True,
        }
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="merge",
                **baseline,
            ),
            "proceed",
        )
        for gate_type in ("staging", "production", "provider_mutation"):
            self.assertEqual(
                orchestration.choose_autopilot_decision(
                    gate_type=gate_type,
                    **{**baseline, "in_goal": False},
                ),
                "skip",
            )
            self.assertEqual(
                orchestration.choose_autopilot_decision(
                    gate_type=gate_type,
                    **baseline,
                ),
                "proceed",
            )
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="staging",
                **{**baseline, "credentials_available": False},
            ),
            "blocked",
        )
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="pr_readiness",
                **{
                    **baseline,
                    "required_evidence": "failed",
                    "remediation_available": True,
                },
            ),
            "retry",
        )
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="pr_readiness",
                **{**baseline, "required_evidence": "unavailable"},
            ),
            "blocked",
        )
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="final_review",
                review_passes=2,
                review_outcome="findings",
                **baseline,
            ),
            "stop",
        )
        self.assertEqual(
            orchestration.choose_autopilot_decision(
                gate_type="cleanup",
                **{**baseline, "safe_path_available": False},
            ),
            "blocked",
        )

    def test_review_and_address_loop_is_capped_at_two_passes(self) -> None:
        lifecycle = (
            PLUGIN
            / "skills"
            / "orchestration"
            / "references"
            / "review-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "Two-pass review-and-address cap",
            "A pass starts when its exact-head review task is created",
            "Pass 2",
            "never create pass 3 automatically",
            "explicit operator decision",
            "The cap never authorizes",
        ):
            self.assertIn(marker, lifecycle)

        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        for pass_number in (1, 2):
            review = review_session(
                f"review-88-pass-{pass_number}",
                status="completed",
                outcome="findings",
            )
            review["target_revision"] = str(pass_number) * 40
            for field in ("terminal_verified", "final_read", "reconciled"):
                review[field] = True
            review["closeout_result"] = "reconciled"
            orchestration.upsert_task(register, review)
            orchestration.set_archive_state(
                register,
                thread_id=review["thread_id"],
                archive_state="archive_intent",
            )
            orchestration.set_archive_state(
                register,
                thread_id=review["thread_id"],
                archive_state="archived",
            )

        third_review = review_session("review-88-pass-3")
        third_review["target_revision"] = "3" * 40
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "two-pass review cap reached",
        ):
            orchestration.upsert_task(register, third_review)

    def test_issue_session_contract_uses_codex_tasks_not_subagents(self) -> None:
        skill_root = PLUGIN / "skills" / "orchestration"
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                skill_root / "SKILL.md",
                skill_root / "references" / "portfolio-triage.md",
                skill_root / "references" / "delegated-session-launch-settings.md",
                skill_root / "references" / "issue-session-lifecycle.md",
            ]
        )
        for marker in (
            "Never create subagents",
            "host's Codex task creation capability",
            "worktree starting from the verified `main` branch",
            "one issue-specific branch",
            "bounded task reads, follow-up messages, and cursor-aware waits",
            "identify safe local equivalents",
            "full-suite coverage deferred",
            "then rerun affected checks and the full suite",
            "patiently waits, observes, and steers only",
            "Goal: <concrete terminal outcome>",
            "archive the exact Codex task",
            "Never delete unmerged work",
        ):
            self.assertIn(marker, combined)
        self.assertNotIn("spawn_agent", combined)
        self.assertNotIn("fork_thread", combined)

    def test_execution_mode_requires_an_explicit_goal_contract(self) -> None:
        self.assertEqual(
            orchestration.choose_execution_mode(goal_contract=GOAL_CONTRACT),
            ("goal", "explicit_goal"),
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "goal_contract",
        ):
            orchestration.choose_execution_mode()

    def test_launch_preflight_fails_closed_without_every_host_capability(self) -> None:
        requested = launch()
        blocked = orchestration.preflight_launch(
            requested,
            permission_selection_supported=False,
            permission_readback_supported=True,
            mode_selection_supported=True,
            mode_readback_supported=True,
            observed_at="2026-07-30T08:01:00Z",
        )
        self.assertEqual(blocked["verification_state"], "blocked")
        self.assertEqual(blocked["blocker_category"], "host_capability")
        self.assertIsNone(blocked["thread_id"])
        self.assertFalse(orchestration.launch_allows_activation(blocked))
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "verified launch preflight",
        ):
            orchestration.bind_launch_task(
                blocked,
                thread_id="thread-91",
                host_id="local",
            )

    def test_verified_full_access_goal_launch_activates_exact_issue_session(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        requested = launch()
        orchestration.preflight_launch(
            requested,
            permission_selection_supported=True,
            permission_readback_supported=True,
            mode_selection_supported=True,
            mode_readback_supported=True,
            observed_at="2026-07-30T08:01:00Z",
        )
        orchestration.bind_launch_task(
            requested,
            thread_id="thread-91",
            host_id="local",
            observed_at="2026-07-30T08:02:00Z",
        )
        verified = orchestration.verify_launch_readback(
            requested,
            effective_permission_profile="full_access",
            effective_execution_mode="goal",
            observed_at="2026-07-30T08:03:00Z",
        )
        self.assertTrue(orchestration.launch_allows_activation(verified))
        orchestration.upsert_launch(register, verified)
        worker = issue_session("thread-91", issue_number=91)
        orchestration.activate_issue_session(register, worker)
        self.assertEqual(register["tasks"][0]["thread_id"], "thread-91")

    def test_permission_mode_and_readback_failures_block_activation(self) -> None:
        cases = (
            ("workspace_write", "goal", "permission_mismatch"),
            ("full_access", "plan", "mode_mismatch"),
            (None, "goal", "readback_unavailable"),
            ("full_access", None, "readback_unavailable"),
        )
        for effective_permission, effective_mode, blocker in cases:
            with self.subTest(blocker=blocker, mode=effective_mode):
                candidate = launch()
                orchestration.preflight_launch(
                    candidate,
                    permission_selection_supported=True,
                    permission_readback_supported=True,
                    mode_selection_supported=True,
                    mode_readback_supported=True,
                    observed_at="2026-07-30T08:01:00Z",
                )
                orchestration.bind_launch_task(
                    candidate,
                    thread_id="thread-91",
                    host_id="local",
                    observed_at="2026-07-30T08:02:00Z",
                )
                orchestration.verify_launch_readback(
                    candidate,
                    effective_permission_profile=effective_permission,
                    effective_execution_mode=effective_mode,
                    observed_at="2026-07-30T08:03:00Z",
                )
                self.assertEqual(candidate["verification_state"], "blocked")
                self.assertEqual(candidate["blocker_category"], blocker)
                self.assertFalse(orchestration.launch_allows_activation(candidate))

    def test_non_goal_or_incomplete_goal_launches_are_rejected(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        non_goal = launch()
        non_goal["requested_execution_mode"] = "plan"
        with self.assertRaisesRegex(orchestration.OrchestrationStateError, "must be goal"):
            orchestration.upsert_launch(register, non_goal)
        incomplete = dict(GOAL_CONTRACT)
        incomplete["objective"] = ""
        with self.assertRaisesRegex(orchestration.OrchestrationStateError, "objective"):
            launch(goal_contract=incomplete)

    def test_cli_launch_flow_requires_verified_settings_before_issue_upsert(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            common = [
                "--project-id",
                "project-example",
                "--orchestrator-id",
                "orchestrator",
                "--state-root",
                str(Path(directory) / "state"),
            ]

            def run(*arguments: str) -> dict[str, object]:
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    result = orchestration.main([arguments[0], *common, *arguments[1:]])
                self.assertEqual(result, 0, stderr.getvalue())
                return json.loads(stdout.getvalue())

            run("init")
            requested = run(
                "launch-request",
                "--issue-number",
                "91",
                "--goal-objective",
                GOAL_CONTRACT["objective"],
                "--project-boundary",
                GOAL_CONTRACT["project_boundary"],
                "--completion-conditions",
                GOAL_CONTRACT["completion_conditions"],
                "--constraints",
                GOAL_CONTRACT["constraints"],
                "--observed-at",
                TIMESTAMP,
            )
            self.assertEqual(requested["verification_state"], "requested")
            preflight = run(
                "launch-preflight",
                "--issue-number",
                "91",
                "--permission-selection-supported",
                "--permission-readback-supported",
                "--mode-selection-supported",
                "--mode-readback-supported",
                "--observed-at",
                "2026-07-30T08:01:00Z",
            )
            self.assertEqual(preflight["verification_state"], "preflight_verified")
            run(
                "launch-bind",
                "--issue-number",
                "91",
                "--thread-id",
                "thread-91",
                "--host-id",
                "local",
                "--observed-at",
                "2026-07-30T08:02:00Z",
            )
            verified = run(
                "launch-verify",
                "--issue-number",
                "91",
                "--effective-permission-profile",
                "full_access",
                "--effective-execution-mode",
                "goal",
                "--observed-at",
                "2026-07-30T08:03:00Z",
            )
            self.assertEqual(verified["verification_state"], "verified")
            activated = run(
                "upsert",
                "--thread-id",
                "thread-91",
                "--host-id",
                "local",
                "--title",
                "Issue #91 | active",
                "--status",
                "active",
                "--issue-number",
                "91",
                "--run-mode",
                "issue_session",
                "--worktree-path",
                "/workspace/example.worktrees/issue-91",
                "--branch-name",
                "codex/issue-91",
                "--base-revision",
                "0123456789abcdef0123456789abcdef01234567",
                "--observed-at",
                "2026-07-30T08:04:00Z",
            )
            self.assertEqual(activated["thread_id"], "thread-91")

    def test_review_contract_is_independent_asynchronous_and_exact_head(self) -> None:
        review = (
            PLUGIN
            / "skills"
            / "orchestration"
            / "references"
            / "review-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "never labels that inspection independent review",
            "must not review\nits own work",
            "Start asynchronously at a stable review point",
            "exact implementation worktree",
            "gpt-5.6-luna",
            "The review task is read-only",
            "Any base or head change makes every earlier review",
            "terminal `clear` result reconciled",
            "Capacity exhaustion is a recorded deferral when independence",
        ):
            self.assertIn(marker, review)

    def test_verification_contract_requires_new_luna_max_same_worktree_task(self) -> None:
        verification = (
            PLUGIN
            / "skills"
            / "orchestration"
            / "references"
            / "verification-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "new user-owned Codex task",
            "`gpt-5.6-luna`",
            "reasoning effort `max`",
            "exact implementation worktree",
            "Never create a separate verifier worktree",
            "`passed`, `failed`, or",
            "must not edit tracked source",
        ):
            self.assertIn(marker, verification)

        register = orchestration.new_register(
            "project-example", "orchestrator", timestamp=TIMESTAMP
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        verifier = verification_session(
            "verify-88", status="completed", outcome="passed"
        )
        verifier["terminal_verified"] = True
        verifier["final_read"] = True
        verifier["reconciled"] = True
        orchestration.upsert_task(register, verifier)
        self.assertEqual(verifier["worktree_path"], subject["worktree_path"])
        self.assertTrue(orchestration.archive_eligible(verifier))

        wrong_worktree = verification_session("verify-wrong")
        wrong_worktree["worktree_path"] = "/workspace/example.worktrees/verify-88"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "must reuse its subject implementation worktree",
        ):
            orchestration.upsert_task(register, wrong_worktree)

    def test_luna_max_readback_and_remediation_turns_fail_closed(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        pending = orchestration.default_task(
            thread_id="review-settings",
            project_id="project-example",
            status="active",
            observed_at=TIMESTAMP,
            host_id="local",
            title="Issue #88 | review",
            issue_number=88,
            run_mode="review_session",
            worktree_path=subject["worktree_path"],
            base_revision=subject["base_revision"],
            subject_thread_id=subject["thread_id"],
            target_revision="89abcdef0123456789abcdef0123456789abcdef",
            review_outcome="pending",
        )
        self.assertEqual(pending["settings_verification_state"], "requested")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "requires verified Luna/max readback",
        ):
            orchestration.upsert_task(register, pending)
        blocked = orchestration.verify_task_settings_readback(
            pending,
            effective_model="gpt-5.6-luna",
            effective_reasoning_effort="high",
        )
        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["settings_blocker_category"], "reasoning_mismatch")
        orchestration.upsert_task(register, blocked)

        implementation = issue_session("thread-remediation")
        turn = orchestration.record_remediation_turn(
            implementation,
            turn_id="remediation-turn-1",
            effective_model=orchestration.LUNA_MODEL,
            effective_reasoning_effort=orchestration.MAX_REASONING_EFFORT,
        )
        self.assertTrue(orchestration.remediation_turn_allows_work(turn))
        self.assertEqual(turn["remediation_turn"]["requested_model"], orchestration.LUNA_MODEL)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "identity and readback are immutable",
        ):
            orchestration.record_remediation_turn(
                turn,
                turn_id="remediation-turn-2",
                effective_model=orchestration.LUNA_MODEL,
                effective_reasoning_effort=orchestration.MAX_REASONING_EFFORT,
            )

    def test_failed_remediation_readback_blocks_source_work_in_cli_transition(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_root = Path(directory) / "state"
            register_path = orchestration.register_path(
                "project-example",
                "orchestrator",
                root=state_root,
            )
            register = orchestration.new_register(
                "project-example",
                "orchestrator",
                timestamp=TIMESTAMP,
            )
            implementation = issue_session("thread-remediation")
            orchestration.upsert_task(register, implementation)
            orchestration.write_register(register_path, register, state_root=state_root)

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = orchestration.main(
                    [
                        "remediation",
                        "--project-id",
                        "project-example",
                        "--orchestrator-id",
                        "orchestrator",
                        "--state-root",
                        str(state_root),
                        "--thread-id",
                        "thread-remediation",
                        "--turn-id",
                        "failed-readback",
                        "--effective-model",
                        orchestration.LUNA_MODEL,
                        "--effective-reasoning-effort",
                        "high",
                    ]
                )
            self.assertEqual(result, 0, stderr.getvalue())
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["status"], "blocked")
            self.assertEqual(output["blocker_category"], "tooling")
            self.assertFalse(orchestration.remediation_turn_allows_work(output))
            persisted = orchestration.load_register(register_path)
            persisted_task = orchestration.resolve_task(
                persisted,
                "thread-remediation",
            )
            self.assertEqual(persisted_task["status"], "blocked")
            self.assertFalse(orchestration.remediation_turn_allows_work(persisted_task))

    def test_terminal_verification_outcomes_are_immutable(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        verifier = verification_session(
            "verify-88",
            status="completed",
            outcome="passed",
        )
        for field in ("terminal_verified", "final_read", "reconciled"):
            verifier[field] = True
        verifier["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, verifier)
        changed = copy.deepcopy(verifier)
        changed["review_outcome"] = "failed"
        changed["last_observed_at"] = "2026-07-30T09:00:00Z"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "terminal verification outcome is immutable",
        ):
            orchestration.upsert_task(register, changed)

        pending = verification_session("verify-stale")
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archived",
        )
        orchestration.upsert_task(register, pending)
        stale = orchestration.set_verification_outcome(
            register,
            thread_id="verify-stale",
            verification_outcome="stale",
        )
        self.assertEqual(stale["review_outcome"], "stale")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "terminal verification outcome is immutable",
        ):
            orchestration.set_verification_outcome(
                register,
                thread_id="verify-stale",
                verification_outcome="stale",
            )

    def test_title_formatter_orders_verified_references(self) -> None:
        self.assertEqual(
            orchestration.format_title(
                issue_number=49,
                pr_number=50,
                status="testing",
            ),
            "Issue #49 | PR #50 | testing",
        )
        self.assertEqual(
            orchestration.format_title(
                pr_number=50,
                status="review",
            ),
            "PR #50 | review",
        )
        self.assertEqual(
            orchestration.format_title(
                fallback_kind="Project",
                fallback_text="checkout",
                status="coordinating",
            ),
            "Project checkout | coordinating",
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "short operational",
        ):
            orchestration.format_title(
                issue_number=49,
                status="this status is much too long and verbose",
            )

    def test_state_directory_resolves_windows_xdg_and_fallbacks(self) -> None:
        self.assertEqual(
            orchestration.state_directory(
                platform_name="nt",
                environment={"LOCALAPPDATA": "/windows-local"},
                home=Path("/home"),
            ),
            Path("/windows-local/Agentic Workflows/agent-orchestration"),
        )
        self.assertEqual(
            orchestration.state_directory(
                platform_name="posix",
                environment={"XDG_STATE_HOME": "/xdg"},
                home=Path("/home"),
            ),
            Path("/xdg/agentic-workflows/agent-orchestration"),
        )
        self.assertEqual(
            orchestration.state_directory(
                platform_name="posix",
                environment={},
                home=Path("/home"),
            ),
            Path("/home/.local/state/agentic-workflows/agent-orchestration"),
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "absolute",
        ):
            orchestration.state_directory(
                environment={"AGENTIC_WORKFLOWS_ORCHESTRATION_STATE_DIR": "relative"},
                home=Path("/home"),
            )

    def test_register_path_uses_identity_digests_and_rejects_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "state"
            path = orchestration.register_path(
                "../project",
                "../../orchestrator",
                root=root,
            )
            self.assertEqual(path.name, "register.json")
            self.assertNotIn("project", str(path.relative_to(root)))
            target = Path(directory) / "target"
            target.mkdir()
            root.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "symlink",
            ):
                orchestration.register_path("project", "task", root=root)

    def test_atomic_owner_only_write_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = orchestration.register_path(
                "project",
                "orchestrator",
                root=Path(directory) / "state",
            )
            register = orchestration.new_register(
                "project",
                "orchestrator",
                timestamp=TIMESTAMP,
            )
            orchestration.write_register(path, register)
            self.assertEqual(orchestration.load_register(path), register)
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)

    def test_register_compare_and_swap_rejects_stale_controller_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "state"
            path = orchestration.register_path("project", "controller", root=root)
            first = orchestration.new_register(
                "project",
                "controller",
                timestamp=TIMESTAMP,
            )
            orchestration.write_register(path, first)
            stale = orchestration.load_register(path)
            current = orchestration.load_register(path)
            current["goal"] = {"state": "active", "last_checked_at": TIMESTAMP}
            current["updated_at"] = TIMESTAMP
            orchestration.write_register(path, current)
            stale["inventory"]["complete"] = True
            stale["updated_at"] = TIMESTAMP
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "stale register write",
            ):
                orchestration.write_register(path, stale)

    def test_same_worktree_claims_are_cross_controller_serialized_and_cas_protected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "state"

            def claim(controller_number: int) -> tuple[bool, str]:
                controller = f"controller-{controller_number}"
                try:
                    orchestration.claim_worktree_ownership(
                        "/workspace/shared",
                        state_root=root,
                        controller_id=controller,
                        task_id=f"task-{controller_number}",
                    )
                    return True, controller
                except orchestration.OrchestrationStateError as error:
                    return False, str(error)

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(claim, (1, 2)))
            self.assertEqual(sum(success for success, _ in results), 1)
            self.assertTrue(
                any("owned by another controller" in value for success, value in results if not success)
            )
            claim_path = (
                root
                / "worktree-claims"
                / f"{orchestration.identity_digest('path:/workspace/shared')}.json"
            )
            persisted = json.loads(claim_path.read_text(encoding="utf-8"))
            winner = persisted["controller_id"]
            task_id = persisted["task_id"]
            revision = persisted["revision"]
            released = orchestration.release_worktree_ownership(
                "/workspace/shared",
                state_root=root,
                controller_id=winner,
                task_id=task_id,
                expected_revision=revision,
            )
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "stale worktree claim revision",
            ):
                orchestration.claim_worktree_ownership(
                    "/workspace/shared",
                    state_root=root,
                    controller_id="controller-2" if winner == "controller-1" else "controller-1",
                    task_id="stale-task",
                    expected_revision=revision,
                )
            reacquired = orchestration.claim_worktree_ownership(
                "/workspace/shared",
                state_root=root,
                controller_id="controller-new",
                task_id="task-new",
                expected_revision=released["revision"],
            )
            self.assertEqual(reacquired["state"], "claimed")

    def test_worktree_claim_identity_survives_creation_and_realpath_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            actual_parent = root / "actual"
            actual_parent.mkdir()
            alias_parent = root / "alias"
            alias_parent.symlink_to(actual_parent, target_is_directory=True)
            missing_alias = alias_parent / "worktree"
            missing_actual = actual_parent / "worktree"

            before = orchestration.canonical_managed_path(
                str(missing_alias),
                "missing worktree",
            )
            self.assertEqual(
                before,
                orchestration.canonical_managed_path(
                    str(missing_actual),
                    "realpath worktree",
                ),
            )
            claimed = orchestration.claim_worktree_ownership(
                str(missing_alias),
                state_root=root / "state",
                controller_id="controller",
                task_id="task",
            )
            missing_actual.mkdir()
            after = orchestration.canonical_managed_path(
                str(missing_alias),
                "created worktree",
            )
            self.assertEqual(before, after)
            self.assertEqual(
                orchestration.canonical_managed_path(
                    str(missing_actual),
                    "created realpath worktree",
                ),
                after,
            )
            released = orchestration.release_worktree_ownership(
                str(missing_actual),
                state_root=root / "state",
                controller_id="controller",
                task_id="task",
                expected_revision=claimed["revision"],
            )
            self.assertEqual(released["state"], "released")

    def test_register_claim_sidecars_roll_back_only_candidate_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_root = Path(directory) / "state"
            register_path = orchestration.register_path(
                "project-example",
                "orchestrator",
                root=state_root,
            )
            register = orchestration.new_register(
                "project-example",
                "orchestrator",
                timestamp=TIMESTAMP,
            )
            subject = issue_session("thread-88")
            orchestration.upsert_task(register, subject)
            orchestration.write_register(register_path, register, state_root=state_root)
            existing_claim = (
                state_root
                / "worktree-claims"
                / f"{orchestration.identity_digest('path:/workspace/example.worktrees/issue-88')}.json"
            )
            existing_bytes = existing_claim.read_bytes()

            candidate = orchestration.load_register(register_path)
            candidate_subject = orchestration.resolve_task(candidate, "thread-88")
            candidate_subject["status"] = "waiting"
            orchestration.upsert_task(candidate, candidate_subject)
            orchestration.upsert_task(candidate, review_session("review-88"))
            orchestration.upsert_task(candidate, issue_session("thread-89", issue_number=89))
            new_claim = (
                state_root
                / "worktree-claims"
                / f"{orchestration.identity_digest('path:/workspace/example.worktrees/issue-89')}.json"
            )

            original_atomic_write = orchestration._atomic_json_write

            def fail_register_write(path: Path, payload: dict[str, object], label: str) -> None:
                if label == "register":
                    raise OSError("forced register persistence failure")
                original_atomic_write(path, payload, label)

            with patch.object(
                orchestration,
                "_atomic_json_write",
                side_effect=fail_register_write,
            ), self.assertRaisesRegex(OSError, "forced register persistence failure"):
                orchestration.write_register(
                    register_path,
                    candidate,
                    state_root=state_root,
                )

            self.assertEqual(existing_claim.read_bytes(), existing_bytes)
            self.assertFalse(new_claim.exists())
            persisted = orchestration.load_register(register_path)
            self.assertEqual(
                [item["thread_id"] for item in persisted["tasks"]],
                ["thread-88"],
            )

    def test_corrupt_existing_register_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = orchestration.register_path(
                "project",
                "orchestrator",
                root=Path(directory) / "state",
            )
            path.parent.mkdir(parents=True)
            path.write_text("{broken", encoding="utf-8")
            if os.name != "nt":
                path.chmod(0o600)
            original = path.read_bytes()
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "cannot read",
            ):
                orchestration.write_register(
                    path,
                    orchestration.new_register(
                        "project",
                        "orchestrator",
                        timestamp=TIMESTAMP,
                    ),
                )
            self.assertEqual(path.read_bytes(), original)

    def test_register_rejects_unknown_fields_and_secret_shaped_text(self) -> None:
        register = orchestration.new_register(
            "project",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        register["prompt"] = "not allowed"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "prohibited",
        ):
            orchestration.validate_register(register)
        register = orchestration.new_register(
            "project",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        unsafe = task("thread")
        unsafe["title"] = "password=do-not-store"
        register["tasks"] = [unsafe]
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "secret-shaped",
        ):
            orchestration.validate_register(register)

    def test_stale_live_observation_cannot_replace_newer_state(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        current = task("thread")
        current["last_observed_at"] = "2026-07-30T09:00:00Z"
        orchestration.upsert_task(register, current)
        stale = task("thread", status="completed")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "stale live observation",
        ):
            orchestration.upsert_task(register, stale)

    def test_wait_batches_are_bounded_cursor_aware_and_rotated(self) -> None:
        tasks = [task(f"thread-{index:02d}") for index in range(10)]
        tasks[0]["cursor"] = "cursor-0"
        batches = orchestration.wait_batches(tasks, rotation_offset=1)
        self.assertEqual([len(batch) for batch in batches], [8, 2])
        self.assertEqual(batches[0][0]["threadId"], "thread-01")
        cursor_target = next(
            target
            for batch in batches
            for target in batch
            if target["threadId"] == "thread-00"
        )
        self.assertEqual(cursor_target["afterCursor"], "cursor-0")
        completed = task("completed", status="completed")
        self.assertEqual(orchestration.wait_batches([completed]), [])
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "between 1 and 8",
        ):
            orchestration.wait_batches(tasks, batch_size=9)

    def test_review_session_requires_independent_registered_subject(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        reviewer = review_session("review-88")
        orchestration.upsert_task(register, reviewer)
        self.assertEqual(reviewer["branch_name"], None)
        self.assertEqual(reviewer["review_outcome"], "pending")

        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "must be independent",
        ):
            review_session("thread-88")

        missing_subject = review_session("review-99", issue_number=99)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "review subject is not in this project register",
        ):
            orchestration.upsert_task(register, missing_subject)

        wrong_issue = review_session("review-wrong-issue", issue_number=89)
        wrong_issue["subject_thread_id"] = "thread-88"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "review issue differs",
        ):
            orchestration.upsert_task(register, wrong_issue)

    def test_register_enforces_same_worktree_identity_and_serialized_ownership(self) -> None:
        orchestrator_review = orchestration.new_register(
            "project-example",
            "review-88",
            timestamp=TIMESTAMP,
        )
        orchestrator_subject = issue_session("thread-88")
        orchestrator_subject["status"] = "waiting"
        orchestration.upsert_task(orchestrator_review, orchestrator_subject)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "review task must differ from the orchestrator",
        ):
            orchestration.upsert_task(
                orchestrator_review,
                review_session("review-88"),
            )

        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        same_worktree = review_session("review-same-worktree")
        orchestration.upsert_task(register, same_worktree)
        self.assertEqual(same_worktree["worktree_path"], subject["worktree_path"])

        verifier = verification_session("verify-same-worktree")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "concurrent review or verification owners",
        ):
            orchestration.upsert_task(register, verifier)

        peer = task("peer")
        orchestration.upsert_task(register, peer)
        wrong_subject = review_session("review-peer")
        wrong_subject["subject_thread_id"] = "peer"
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "subject must be an issue session",
        ):
            orchestration.upsert_task(register, wrong_subject)

    def test_only_clear_review_of_unchanged_exact_range_satisfies_gate(self) -> None:
        review = review_session("review-88", status="completed", outcome="clear")
        for field in ("terminal_verified", "final_read", "reconciled"):
            review[field] = True
        self.assertTrue(
            orchestration.review_clears_revision(
                review,
                "0123456789abcdef0123456789abcdef01234567",
                "89abcdef0123456789abcdef0123456789abcdef",
            )
        )
        self.assertFalse(
            orchestration.review_clears_revision(
                review,
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "89abcdef0123456789abcdef0123456789abcdef",
            )
        )
        self.assertFalse(
            orchestration.review_clears_revision(
                review,
                "0123456789abcdef0123456789abcdef01234567",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            )
        )
        review["review_outcome"] = "findings"
        self.assertFalse(
            orchestration.review_clears_revision(
                review,
                "0123456789abcdef0123456789abcdef01234567",
                "89abcdef0123456789abcdef0123456789abcdef",
            )
        )

    def test_stale_review_invalidates_clearance_without_fabricating_terminal_state(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        orchestration.upsert_task(register, review_session("review-88"))
        stale = orchestration.set_review_outcome(
            register,
            thread_id="review-88",
            review_outcome="stale",
        )
        self.assertFalse(orchestration.archive_eligible(stale))
        for field in ("terminal_verified", "final_read", "reconciled"):
            self.assertFalse(stale[field])
        self.assertEqual(stale["status"], "active")
        self.assertFalse(
            orchestration.review_clears_revision(
                stale,
                "0123456789abcdef0123456789abcdef01234567",
                "89abcdef0123456789abcdef0123456789abcdef",
            )
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "only stale invalidation",
        ):
            orchestration.set_review_outcome(
                register,
                thread_id="review-88",
                review_outcome="clear",
            )
        fabricated_clear = copy.deepcopy(stale)
        fabricated_clear["last_observed_at"] = "2026-07-30T09:00:00Z"
        fabricated_clear["status"] = "completed"
        fabricated_clear["review_outcome"] = "clear"
        fabricated_clear["terminal_verified"] = True
        fabricated_clear["final_read"] = True
        fabricated_clear["reconciled"] = True
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "terminal review outcome is immutable",
        ):
            orchestration.upsert_task(register, fabricated_clear)
        stale["status"] = "completed"
        stale["terminal_verified"] = True
        stale["final_read"] = True
        stale["reconciled"] = True
        self.assertTrue(orchestration.archive_eligible(stale))

    def test_blocked_review_requires_explicit_blocked_outcome(self) -> None:
        blocked = review_session("review-88", status="blocked", outcome="blocked")
        for field in ("terminal_verified", "final_read", "reconciled"):
            blocked[field] = True
        blocked["blocker_category"] = "tooling"
        self.assertTrue(orchestration.archive_eligible(blocked))
        blocked["review_outcome"] = "pending"
        self.assertFalse(orchestration.archive_eligible(blocked))

    def test_review_range_is_immutable_and_requires_full_object_ids(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        orchestration.upsert_task(register, subject)
        review = review_session("review-88")
        orchestration.upsert_task(register, review)
        retargeted = copy.deepcopy(review)
        retargeted["last_observed_at"] = "2026-07-30T09:00:00Z"
        retargeted["target_revision"] = "a" * 40
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "revision range are immutable",
        ):
            orchestration.upsert_task(register, retargeted)

        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "Git object ID",
        ):
            review_session("review-short", target_revision="89abcde")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "full Git object ID",
        ):
            orchestration.review_clears_revision(review, "0123456", "89abcde")

    def test_inventory_and_archive_transitions_are_explicit(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        orchestration.set_inventory(
            register,
            complete=True,
            limitation="",
            rotation_offset=3,
        )
        self.assertTrue(register["inventory"]["complete"])
        completed = task("thread-complete", status="completed")
        completed["terminal_verified"] = True
        completed["final_read"] = True
        completed["reconciled"] = True
        completed["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, completed)
        intent = orchestration.set_archive_state(
            register,
            thread_id="thread-complete",
            archive_state="archive_intent",
        )
        self.assertEqual(intent["archive_state"], "archive_intent")
        archived = orchestration.set_archive_state(
            register,
            thread_id="thread-complete",
            archive_state="archived",
        )
        self.assertEqual(archived["status"], "archived_known")
        recovered = orchestration.set_archive_state(
            register,
            thread_id="thread-complete",
            archive_state="unarchived",
        )
        self.assertEqual(recovered["closeout_result"], "recovered")

    def test_archive_eligibility_requires_every_closeout_gate(self) -> None:
        completed = task("thread", status="completed")
        self.assertFalse(orchestration.archive_eligible(completed))
        for field in ("terminal_verified", "final_read", "reconciled"):
            completed[field] = True
        self.assertTrue(orchestration.archive_eligible(completed))
        completed["needed_for_dependency"] = True
        self.assertFalse(orchestration.archive_eligible(completed))
        completed["needed_for_dependency"] = False
        completed["blocker_category"] = "dependency"
        self.assertFalse(orchestration.archive_eligible(completed))

    def test_completed_issue_closeout_requires_unchanged_clear_review_and_passed_verification(
        self,
    ) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        state_root = Path(tempfile.mkdtemp())
        subject = issue_session("thread-88", status="completed")
        for field in ("terminal_verified", "final_read", "reconciled"):
            subject[field] = True
        subject["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, subject)

        review = review_session("review-88", status="completed", outcome="clear")
        for field in ("terminal_verified", "final_read", "reconciled"):
            review[field] = True
        review["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, review)
        orchestration.set_archive_state(
            register,
            thread_id="review-88",
            archive_state="archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="review-88",
            archive_state="archived",
        )

        verifier = verification_session(
            "verify-88",
            status="completed",
            outcome="passed",
        )
        for field in ("terminal_verified", "final_read", "reconciled"):
            verifier[field] = True
        verifier["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, verifier)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "terminal verifier to be authoritatively archived and released",
        ):
            orchestration.set_archive_state(
                register,
                thread_id="thread-88",
                archive_state="archive_intent",
                review_base_revision=subject["base_revision"],
                review_target_revision=review["target_revision"],
            )
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archived",
        )
        orchestration.write_register(
            orchestration.register_path(
                "project-example", "orchestrator", root=state_root
            ),
            register,
            state_root=state_root,
        )
        base = subject["base_revision"]
        target = review["target_revision"]
        self.assertFalse(
            orchestration.archive_eligible(
                subject,
                implementation_review_clear=True,
                implementation_verification_passed=False,
            )
        )
        self.assertTrue(
            orchestration.archive_eligible(
                subject,
                implementation_review_clear=True,
                implementation_verification_passed=True,
            )
        )
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archive_intent",
            review_base_revision=base,
            review_target_revision=target,
            state_root=state_root,
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "same full base/head pair",
        ):
            orchestration.set_archive_state(
                register,
                thread_id="thread-88",
                archive_state="archived",
                review_base_revision=base,
                review_target_revision=target,
                verification_base_revision=base,
                verification_target_revision="a" * 40,
                state_root=state_root,
            )
        archived = orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archived",
            review_base_revision=base,
            review_target_revision=target,
            state_root=state_root,
        )
        self.assertEqual(archived["status"], "archived_known")

    def test_blocked_issue_session_archives_then_requires_safe_cleanup(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        blocked = issue_session("thread-88", status="blocked")
        blocked["terminal_verified"] = True
        blocked["final_read"] = True
        blocked["reconciled"] = True
        blocked["blocker_category"] = "dependency"
        blocked["needed_for_dependency"] = True
        blocked["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, blocked)
        self.assertTrue(orchestration.archive_eligible(blocked))

        blocked["blocker_category"] = None
        self.assertFalse(orchestration.archive_eligible(blocked))
        blocked["blocker_category"] = "dependency"

        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archive_intent",
        )
        archived = orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archived",
        )
        self.assertEqual(archived["cleanup_state"], "active")
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "not eligible for cleanup",
        ):
            orchestration.set_cleanup_state(
                register,
                thread_id="thread-88",
                cleanup_state="cleanup_intent",
                worktree_clean=False,
                branch_evidence_preserved=True,
                task_owned=True,
            )

        intent = orchestration.set_cleanup_state(
            register,
            thread_id="thread-88",
            cleanup_state="cleanup_intent",
            worktree_clean=True,
            branch_evidence_preserved=True,
            task_owned=True,
        )
        self.assertEqual(intent["cleanup_state"], "cleanup_intent")
        cleaned = orchestration.set_cleanup_state(
            register,
            thread_id="thread-88",
            cleanup_state="cleaned",
        )
        self.assertEqual(cleaned["cleanup_state"], "cleaned")

    def test_completed_cleanup_intent_requires_archived_verifier_release(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        state_root = Path(tempfile.mkdtemp())
        subject = issue_session("thread-88", status="completed")
        subject["archive_state"] = "archived"
        subject["status"] = "archived_known"
        subject["closeout_result"] = "archived"
        for field in ("terminal_verified", "final_read", "reconciled"):
            subject[field] = True
        orchestration.upsert_task(register, subject)

        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "terminal verifier to be authoritatively archived and released",
        ):
            orchestration.set_cleanup_state(
                register,
                thread_id="thread-88",
                cleanup_state="cleanup_intent",
                worktree_clean=True,
                branch_evidence_preserved=True,
                task_owned=True,
            )

        verifier = verification_session(
            "verify-88",
            status="completed",
            outcome="passed",
        )
        verifier["archive_state"] = "archived"
        verifier["status"] = "archived_known"
        verifier["closeout_result"] = "archived"
        for field in ("terminal_verified", "final_read", "reconciled"):
            verifier[field] = True
        orchestration.upsert_task(register, verifier)
        claimed = orchestration.claim_worktree_ownership(
            verifier["worktree_path"],
            state_root=state_root,
            controller_id="orchestrator",
            task_id="verify-88",
        )
        orchestration.release_worktree_ownership(
            verifier["worktree_path"],
            state_root=state_root,
            controller_id="orchestrator",
            task_id="verify-88",
            expected_revision=claimed["revision"],
        )
        orchestration.write_register(
            orchestration.register_path(
                "project-example", "orchestrator", root=state_root
            ),
            register,
            state_root=state_root,
        )
        intent = orchestration.set_cleanup_state(
            register,
            thread_id="thread-88",
            cleanup_state="cleanup_intent",
            worktree_clean=True,
            branch_evidence_preserved=True,
            task_owned=True,
            state_root=state_root,
        )
        self.assertEqual(intent["cleanup_state"], "cleanup_intent")

    def test_unsafe_terminal_cleanup_can_be_preserved(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        state_root = Path(tempfile.mkdtemp())
        completed = issue_session("thread-88", status="completed")
        for field in ("terminal_verified", "final_read", "reconciled"):
            completed[field] = True
        completed["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, completed)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "requires the full live review and verification base and target",
        ):
            orchestration.set_archive_state(
                register,
                thread_id="thread-88",
                archive_state="archive_intent",
            )
        self.assertEqual(
            orchestration.resolve_task(register, "thread-88")["archive_state"],
            "unarchived",
        )

        clear_review = review_session(
            "review-88",
            status="completed",
            outcome="clear",
        )
        for field in ("terminal_verified", "final_read", "reconciled"):
            clear_review[field] = True
        clear_review["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, clear_review)
        orchestration.set_archive_state(
            register,
            thread_id="review-88",
            archive_state="archive_intent",
        )
        archived_review = orchestration.set_archive_state(
            register,
            thread_id="review-88",
            archive_state="archived",
        )
        self.assertTrue(
            orchestration.review_clears_revision(
                archived_review,
                "0123456789abcdef0123456789abcdef01234567",
                "89abcdef0123456789abcdef0123456789abcdef",
            )
        )
        verifier = verification_session(
            "verify-88",
            status="completed",
            outcome="passed",
        )
        for field in ("terminal_verified", "final_read", "reconciled"):
            verifier[field] = True
        verifier["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, verifier)
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="verify-88",
            archive_state="archived",
        )
        orchestration.write_register(
            orchestration.register_path(
                "project-example", "orchestrator", root=state_root
            ),
            register,
            state_root=state_root,
        )
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archive_intent",
            review_base_revision="0123456789abcdef0123456789abcdef01234567",
            review_target_revision="89abcdef0123456789abcdef0123456789abcdef",
            state_root=state_root,
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "clearance is stale at archive result",
        ):
            orchestration.set_archive_state(
                register,
                thread_id="thread-88",
                archive_state="archived",
                review_base_revision="0123456789abcdef0123456789abcdef01234567",
                review_target_revision="a" * 40,
            )
        self.assertEqual(
            orchestration.resolve_task(register, "thread-88")["archive_state"],
            "archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archived",
            review_base_revision="0123456789abcdef0123456789abcdef01234567",
            review_target_revision="89abcdef0123456789abcdef0123456789abcdef",
            state_root=state_root,
        )
        preserved = orchestration.set_cleanup_state(
            register,
            thread_id="thread-88",
            cleanup_state="preserved",
        )
        self.assertEqual(preserved["cleanup_state"], "preserved")
        recovered_review = orchestration.set_archive_state(
            register,
            thread_id="review-88",
            archive_state="unarchived",
        )
        self.assertEqual(recovered_review["status"], "completed")

    def test_review_archive_is_atomic_and_unarchive_restores_terminal_status(self) -> None:
        for outcome, terminal_status in (
            ("clear", "completed"),
            ("findings", "completed"),
            ("blocked", "blocked"),
        ):
            with self.subTest(outcome=outcome):
                register = orchestration.new_register(
                    "project-example",
                    "orchestrator",
                    timestamp=TIMESTAMP,
                )
                orchestration.upsert_task(register, issue_session("thread-88"))
                review = review_session(
                    "review-88",
                    status=terminal_status,
                    outcome=outcome,
                )
                for field in ("terminal_verified", "final_read", "reconciled"):
                    review[field] = True
                if outcome == "blocked":
                    review["blocker_category"] = "tooling"
                review["closeout_result"] = "reconciled"
                orchestration.upsert_task(register, review)
                orchestration.set_archive_state(
                    register,
                    thread_id="review-88",
                    archive_state="archive_intent",
                )
                archived = orchestration.set_archive_state(
                    register,
                    thread_id="review-88",
                    archive_state="archived",
                )
                self.assertEqual(archived["status"], "archived_known")
                recovered = orchestration.set_archive_state(
                    register,
                    thread_id="review-88",
                    archive_state="unarchived",
                )
                self.assertEqual(recovered["status"], terminal_status)

    def test_triage_starts_one_foreground_issue_only(self) -> None:
        issues = [
            {
                "issue_number": 91,
                "priority": 5,
                "blocked": False,
                "minor_dependency": True,
                "valuable": True,
                "overlap_keys": ["docs"],
            },
            {
                "issue_number": 92,
                "priority": 4,
                "blocked": False,
                "minor_dependency": False,
                "valuable": True,
                "overlap_keys": ["runtime"],
            },
            {
                "issue_number": 93,
                "priority": 3,
                "blocked": False,
                "minor_dependency": False,
                "valuable": True,
                "overlap_keys": ["runtime"],
            },
            {
                "issue_number": 94,
                "priority": 9,
                "blocked": True,
                "minor_dependency": False,
                "valuable": True,
                "overlap_keys": ["release"],
            },
        ]
        decisions = orchestration.triage_issue_candidates(issues, capacity=3)
        by_issue = {decision["issue_number"]: decision for decision in decisions}
        self.assertEqual(by_issue[91]["decision"], "start")
        self.assertIn("minor dependency", by_issue[91]["reason"])
        self.assertEqual(by_issue[92]["decision"], "defer")
        self.assertIn("Foreground issue #91", by_issue[92]["reason"])
        self.assertEqual(by_issue[93]["decision"], "defer")
        self.assertIn("Foreground issue #91", by_issue[93]["reason"])
        self.assertEqual(by_issue[94]["decision"], "blocked")

    def test_recovery_requires_exact_or_unambiguous_match(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        first = task("thread-1", title="Issue #49 | done")
        second = task("thread-2", title="Issue #49 | done")
        register["tasks"] = [first, second]
        orchestration.validate_register(register)
        self.assertEqual(
            orchestration.resolve_task(register, "thread-1")["thread_id"],
            "thread-1",
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "ambiguous",
        ):
            orchestration.resolve_task(register, "Issue #49 | done")

    def test_unknown_schema_version_requires_explicit_migration(self) -> None:
        register = orchestration.new_register(
            "project",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        future = copy.deepcopy(register)
        future["schema_version"] = 8
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "migrate incompatible",
        ):
            orchestration.validate_register(future)

    def test_schema_v1_register_migrates_to_observed_peer_defaults(self) -> None:
        legacy = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        legacy["schema_version"] = 1
        legacy.pop("launches")
        legacy.pop("state_revision")
        legacy_task = task("legacy-thread")
        for field in (
            "run_mode",
            "worktree_path",
            "branch_name",
            "base_revision",
            "subject_thread_id",
            "target_revision",
            "review_outcome",
            "cleanup_state",
        ):
            legacy_task.pop(field)
        for field in orchestration.TASK_EXTENSION_KEYS:
            legacy_task.pop(field)
        legacy["tasks"] = [legacy_task]
        migrated = orchestration.migrate_register(legacy)
        self.assertEqual(migrated["schema_version"], 7)
        self.assertEqual(migrated["state_revision"], 0)
        self.assertEqual(migrated["decision_policy"], "autopilot")
        self.assertEqual(migrated["gate_decisions"], [])
        self.assertEqual(migrated["launches"], [])
        self.assertEqual(migrated["tasks"][0]["run_mode"], "observed_peer")
        self.assertEqual(migrated["tasks"][0]["cleanup_state"], "not_applicable")

    def test_schema_v2_register_migrates_with_empty_review_and_launch_metadata(
        self,
    ) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 2
        previous.pop("launches")
        previous.pop("state_revision")
        previous_task = issue_session("thread-88")
        for field in (
            "subject_thread_id",
            "target_revision",
            "review_outcome",
        ):
            previous_task.pop(field)
        for field in orchestration.TASK_EXTENSION_KEYS:
            previous_task.pop(field)
        previous["tasks"] = [previous_task]
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(migrated["schema_version"], 7)
        self.assertEqual(migrated["launches"], [])
        self.assertIsNone(migrated["tasks"][0]["subject_thread_id"])
        self.assertIsNone(migrated["tasks"][0]["target_revision"])
        self.assertIsNone(migrated["tasks"][0]["review_outcome"])

    def test_schema_v2_abbreviated_revision_uses_explicit_git_reresolution(self) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 2
        previous.pop("launches")
        previous.pop("state_revision")
        previous_task = issue_session("thread-88")
        previous_task["base_revision"] = "0123456"
        for field in (
            "subject_thread_id",
            "target_revision",
            "review_outcome",
        ):
            previous_task.pop(field)
        for field in orchestration.TASK_EXTENSION_KEYS:
            previous_task.pop(field)
        previous["tasks"] = [previous_task]
        calls: list[tuple[str, str]] = []

        def resolve(worktree_path: str, revision: str) -> str:
            calls.append((worktree_path, revision))
            return "0123456789abcdef0123456789abcdef01234567"

        migrated = orchestration.migrate_register(
            previous,
            legacy_revision_resolver=resolve,
        )
        self.assertEqual(
            calls,
            [("/workspace/example.worktrees/issue-88", "0123456")],
        )
        self.assertEqual(
            migrated["tasks"][0]["base_revision"],
            "0123456789abcdef0123456789abcdef01234567",
        )

    def test_schema_v2_migration_canonicalizes_legacy_worktree_path(self) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 2
        previous.pop("launches")
        previous.pop("state_revision")
        previous_task = issue_session("thread-88")
        previous_task["worktree_path"] = (
            "/workspace/example.worktrees/child/../issue-88"
        )
        for field in (
            "subject_thread_id",
            "target_revision",
            "review_outcome",
        ):
            previous_task.pop(field)
        for field in orchestration.TASK_EXTENSION_KEYS:
            previous_task.pop(field)
        previous["tasks"] = [previous_task]
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(
            migrated["tasks"][0]["worktree_path"],
            "/workspace/example.worktrees/issue-88",
        )

    def test_schema_v3_register_migrates_with_empty_launch_records(self) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 3
        previous.pop("launches")
        previous.pop("state_revision")
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        review = review_session("review-88")
        for item in (subject, review):
            for field in orchestration.TASK_EXTENSION_KEYS:
                item.pop(field)
        previous["tasks"] = [subject, review]
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(migrated["schema_version"], 7)
        self.assertEqual(migrated["launches"], [])
        self.assertEqual(migrated["tasks"][1]["run_mode"], "review_session")

    def test_schema_v4_detached_review_migrates_without_inventing_proof(self) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 4
        previous.pop("state_revision")
        subject = issue_session("thread-88")
        subject["status"] = "waiting"
        review = review_session(
            "review-detached",
            status="completed",
            outcome="clear",
        )
        review["worktree_path"] = "/workspace/example.worktrees/review-88"
        for field in ("terminal_verified", "final_read", "reconciled"):
            review[field] = True
        review["closeout_result"] = "reconciled"
        for item in (subject, review):
            for field in orchestration.TASK_EXTENSION_KEYS:
                item.pop(field)
        previous["tasks"] = [subject, review]
        migrated = orchestration.migrate_register(previous)
        migrated_review = migrated["tasks"][1]
        self.assertEqual(migrated["schema_version"], 7)
        self.assertEqual(migrated_review["worktree_path"], review["worktree_path"])
        self.assertEqual(migrated_review["review_outcome"], "clear")
        self.assertEqual(
            migrated_review["legacy_migration_state"],
            "v4_detached_review",
        )
        self.assertEqual(migrated_review["settings_verification_state"], "legacy_unverified")
        self.assertFalse(
            orchestration.review_clears_revision(
                migrated_review,
                migrated_review["base_revision"],
                migrated_review["target_revision"],
            )
        )

    def test_schema_v4_symlink_review_migration_preserves_ownership_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            implementation_path = root / "implementation"
            implementation_path.mkdir()
            legacy_review_path = root / "legacy-review"
            legacy_review_path.symlink_to(
                implementation_path,
                target_is_directory=True,
            )

            previous = orchestration.new_register(
                "project-example",
                "orchestrator",
                timestamp=TIMESTAMP,
            )
            previous["schema_version"] = 4
            previous.pop("state_revision")
            subject = issue_session("thread-88")
            subject["status"] = "waiting"
            subject["worktree_path"] = str(implementation_path)
            review = review_session(
                "review-legacy-symlink",
                status="completed",
                outcome="clear",
            )
            review["worktree_path"] = str(legacy_review_path)
            for field in ("terminal_verified", "final_read", "reconciled"):
                review[field] = True
            review["closeout_result"] = "reconciled"
            for item in (subject, review):
                for field in orchestration.TASK_EXTENSION_KEYS:
                    item.pop(field)
            previous["tasks"] = [subject, review]
            original = copy.deepcopy(previous)

            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "cannot prove detached worktree ownership",
            ):
                orchestration.migrate_register(previous)
            self.assertEqual(previous, original)
            self.assertEqual(previous["schema_version"], 4)
            self.assertEqual(
                previous["tasks"][1]["worktree_path"],
                str(legacy_review_path),
            )

    def test_schema_v5_register_migrates_with_empty_sdlc_routing_state(self) -> None:
        previous = orchestration.new_register(
            "project-example", "orchestrator", timestamp=TIMESTAMP
        )
        previous["schema_version"] = 5
        previous.pop("sdlc_scope")
        previous.pop("routing_decisions")
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(migrated["schema_version"], 7)
        self.assertIsNone(migrated["sdlc_scope"])
        self.assertEqual(migrated["routing_decisions"], [])

    def test_schema_v6_launches_are_cleared_without_an_explicit_goal_contract(self) -> None:
        previous = json.loads(
            (PLUGIN / "examples" / "register.json").read_text(encoding="utf-8")
        )
        previous["schema_version"] = 6
        previous["launches"][0].pop("goal_contract")
        previous["launches"][0]["selection_source"] = "operator"
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(migrated["schema_version"], 7)
        self.assertEqual(migrated["launches"], [])

    def test_managed_worktree_aliases_cannot_bypass_review_isolation(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        subject = issue_session("thread-88")
        orchestration.upsert_task(register, subject)
        aliased = review_session("review-alias")
        aliased["worktree_path"] = (
            "/workspace/example.worktrees/child/../issue-88"
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "worktree_path must be canonical",
        ):
            orchestration.upsert_task(register, aliased)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            actual_parent = root / "actual"
            actual_parent.mkdir()
            actual_worktree = actual_parent / "shared"
            actual_worktree.mkdir()
            alias_parent = root / "alias"
            alias_parent.symlink_to(actual_parent, target_is_directory=True)

            register = orchestration.new_register(
                "project-example",
                "orchestrator",
                timestamp=TIMESTAMP,
            )
            subject = issue_session("thread-88")
            subject["worktree_path"] = str(actual_worktree)
            subject["status"] = "waiting"
            orchestration.upsert_task(register, subject)
            aliased = review_session("review-inode")
            aliased["worktree_path"] = str(alias_parent / "shared")
            orchestration.upsert_task(register, aliased)
            self.assertEqual(aliased["worktree_path"], str(alias_parent / "shared"))


if __name__ == "__main__":
    unittest.main()
