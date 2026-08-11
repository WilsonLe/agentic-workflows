from __future__ import annotations

import copy
import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "agent-orchestration"
SCRIPT = PLUGIN / "scripts" / "orchestration_state.py"
SPEC = importlib.util.spec_from_file_location("orchestration_state", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
orchestration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orchestration)

TIMESTAMP = "2026-07-30T08:00:00Z"


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
        worktree_path=f"/workspace/example.worktrees/review-{issue_number}",
        base_revision="0123456789abcdef0123456789abcdef01234567",
        subject_thread_id=f"thread-{issue_number}",
        target_revision=target_revision,
        review_outcome=outcome,
    )


class AgentOrchestrationTests(unittest.TestCase):
    def test_example_register_and_schema_metadata_are_valid(self) -> None:
        example = json.loads(
            (PLUGIN / "examples" / "register.json").read_text(encoding="utf-8")
        )
        orchestration.validate_register(example)
        schema = json.loads(
            (
                PLUGIN
                / "schemas"
                / "orchestration-state-v3.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 3)
        self.assertIn("task", schema["$defs"])
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        validator.validate(example)
        invalid = copy.deepcopy(example)
        invalid["tasks"][1]["branch_name"] = "review-must-be-detached"
        with self.assertRaises(ValidationError):
            validator.validate(invalid)

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
            "Goal is clear. I have no further questions.",
            "Omit `token_budget`",
            "after context compaction",
            "Mark it blocked only after the same blocking condition",
            "Goal Mode increases persistence, not authority",
        ):
            self.assertIn(marker, activation)

    def test_activation_description_distinguishes_explicit_and_ambiguous_use(self) -> None:
        skill = (
            PLUGIN / "skills" / "orchestration" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("explicit operator designation", skill)
        self.assertIn("main branch", skill)
        self.assertIn("Never create subagents", skill)
        self.assertIn("new project worktree", skill)
        self.assertIn("never performs code review itself", skill)
        self.assertIn("separate detached worktree", skill)

    def test_issue_session_contract_uses_codex_tasks_not_subagents(self) -> None:
        skill_root = PLUGIN / "skills" / "orchestration"
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                skill_root / "SKILL.md",
                skill_root / "references" / "portfolio-triage.md",
                skill_root / "references" / "issue-session-lifecycle.md",
            ]
        )
        for marker in (
            "Never create subagents",
            "host's Codex task creation capability",
            "worktree starting from the verified `main` branch",
            "one issue-specific branch",
            "bounded task reads, follow-up messages, and cursor-aware waits",
            "archive the exact Codex task",
            "Never delete unmerged work",
        ):
            self.assertIn(marker, combined)
        self.assertNotIn("spawn_agent", combined)
        self.assertNotIn("fork_thread", combined)

    def test_review_contract_is_independent_asynchronous_and_exact_head(self) -> None:
        review = (
            PLUGIN
            / "skills"
            / "orchestration"
            / "references"
            / "review-session-lifecycle.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "The control plane never performs code review",
            "must not review its own work",
            "Start asynchronously at a stable review point",
            "detached review worktree pinned to the exact candidate head",
            "The review task is read-only",
            "Any base or head change makes every earlier review",
            "terminal `clear` result reconciled",
            "Capacity exhaustion is a recorded deferral",
        ):
            self.assertIn(marker, review)

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
            Path("/windows-local/AMSoft/agent-orchestration"),
        )
        self.assertEqual(
            orchestration.state_directory(
                platform_name="posix",
                environment={"XDG_STATE_HOME": "/xdg"},
                home=Path("/home"),
            ),
            Path("/xdg/amsoft/agent-orchestration"),
        )
        self.assertEqual(
            orchestration.state_directory(
                platform_name="posix",
                environment={},
                home=Path("/home"),
            ),
            Path("/home/.local/state/amsoft/agent-orchestration"),
        )
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "absolute",
        ):
            orchestration.state_directory(
                environment={"AMSOFT_ORCHESTRATION_STATE_DIR": "relative"},
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

    def test_register_enforces_reviewer_subject_and_worktree_independence(self) -> None:
        orchestrator_review = orchestration.new_register(
            "project-example",
            "review-88",
            timestamp=TIMESTAMP,
        )
        orchestration.upsert_task(orchestrator_review, issue_session("thread-88"))
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "reviewer must differ from the orchestrator",
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
        orchestration.upsert_task(register, subject)
        same_worktree = review_session("review-same-worktree")
        same_worktree["worktree_path"] = subject["worktree_path"]
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "reuses the managed worktree",
        ):
            orchestration.upsert_task(register, same_worktree)

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
        orchestration.upsert_task(register, issue_session("thread-88"))
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
        orchestration.upsert_task(register, issue_session("thread-88"))
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

    def test_unsafe_terminal_cleanup_can_be_preserved(self) -> None:
        register = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        completed = issue_session("thread-88", status="completed")
        for field in ("terminal_verified", "final_read", "reconciled"):
            completed[field] = True
        completed["closeout_result"] = "reconciled"
        orchestration.upsert_task(register, completed)
        with self.assertRaisesRegex(
            orchestration.OrchestrationStateError,
            "requires the full live review base and target",
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
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archive_intent",
            review_base_revision="0123456789abcdef0123456789abcdef01234567",
            review_target_revision="89abcdef0123456789abcdef0123456789abcdef",
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

    def test_triage_starts_independent_minor_dependency_lanes_concurrently(self) -> None:
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
        self.assertEqual(by_issue[92]["decision"], "start")
        self.assertEqual(by_issue[93]["decision"], "defer")
        self.assertIn("overlap", by_issue[93]["reason"])
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
        future["schema_version"] = 4
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
        legacy["tasks"] = [legacy_task]
        migrated = orchestration.migrate_register(legacy)
        self.assertEqual(migrated["schema_version"], 3)
        self.assertEqual(migrated["tasks"][0]["run_mode"], "observed_peer")
        self.assertEqual(migrated["tasks"][0]["cleanup_state"], "not_applicable")

    def test_schema_v2_register_migrates_with_empty_review_metadata(self) -> None:
        previous = orchestration.new_register(
            "project-example",
            "orchestrator",
            timestamp=TIMESTAMP,
        )
        previous["schema_version"] = 2
        previous_task = issue_session("thread-88")
        for field in (
            "subject_thread_id",
            "target_revision",
            "review_outcome",
        ):
            previous_task.pop(field)
        previous["tasks"] = [previous_task]
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(migrated["schema_version"], 3)
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
        previous_task = issue_session("thread-88")
        previous_task["base_revision"] = "0123456"
        for field in (
            "subject_thread_id",
            "target_revision",
            "review_outcome",
        ):
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
        previous["tasks"] = [previous_task]
        migrated = orchestration.migrate_register(previous)
        self.assertEqual(
            migrated["tasks"][0]["worktree_path"],
            "/workspace/example.worktrees/issue-88",
        )

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
            orchestration.upsert_task(register, subject)
            aliased = review_session("review-inode")
            aliased["worktree_path"] = str(alias_parent / "shared")
            with self.assertRaisesRegex(
                orchestration.OrchestrationStateError,
                "reuses the managed worktree",
            ):
                orchestration.upsert_task(register, aliased)


if __name__ == "__main__":
    unittest.main()
