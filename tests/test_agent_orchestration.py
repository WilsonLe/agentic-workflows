from __future__ import annotations

import copy
import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

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
) -> dict[str, object]:
    return orchestration.default_task(
        thread_id=thread_id,
        project_id="project-example",
        status=status,
        observed_at=TIMESTAMP,
        host_id="local",
        title=f"Issue #{issue_number} | working",
        issue_number=issue_number,
        run_mode="issue_session",
        worktree_path=f"/workspace/example.worktrees/issue-{issue_number}",
        branch_name=f"codex/issue-{issue_number}",
        base_revision="0123456789abcdef0123456789abcdef01234567",
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
                / "orchestration-state-v2.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
        self.assertIn("task", schema["$defs"])

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
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archive_intent",
        )
        orchestration.set_archive_state(
            register,
            thread_id="thread-88",
            archive_state="archived",
        )
        preserved = orchestration.set_cleanup_state(
            register,
            thread_id="thread-88",
            cleanup_state="preserved",
        )
        self.assertEqual(preserved["cleanup_state"], "preserved")

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
        future["schema_version"] = 3
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
            "cleanup_state",
        ):
            legacy_task.pop(field)
        legacy["tasks"] = [legacy_task]
        migrated = orchestration.migrate_register(legacy)
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual(migrated["tasks"][0]["run_mode"], "observed_peer")
        self.assertEqual(migrated["tasks"][0]["cleanup_state"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
