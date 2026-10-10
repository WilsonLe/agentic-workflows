"""Behavior checks for the five workflow improvements in issues 134–138."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

from tests.test_standard_workflow_records import task_run


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workflow = load_module(
    "workflow_efficiencies_record",
    ROOT / "plugins/agentic-workflows/skills/standard-development-workflow/scripts/standard_workflow_record.py",
)
history = load_module(
    "workflow_efficiencies_history",
    ROOT / "plugins/agentic-workflows/skills/session-reflection/scripts/session_evidence.py",
)
reflection = load_module(
    "workflow_efficiencies_reflection_state",
    ROOT / "plugins/agentic-workflows/skills/session-reflection/scripts/reflection_state.py",
)


def release_check(kind: str, check_id: str) -> dict[str, object]:
    return {
        "id": check_id,
        "kind": kind,
        "claim": "Critical behavior remains available.",
        "critical": True,
        "safe_probe": True,
        "state": "passed",
        "revision": "a" * 40,
        "environment": "staging",
        "observed_at": "2026-09-29T00:00:00Z",
        "evidence_ref": "staging-readback",
        "authority_ref": "",
        "live_effect": "synthetic",
        "configured_state": "enabled" if kind == "worker" else "",
        "runtime_state": "running" if kind == "worker" else "",
        "store_state": "present" if kind == "durable_record" else "",
        "read_surface_state": "present" if kind == "durable_record" else "",
        "read_surface_freshness": "current" if kind == "durable_record" else "",
        "failure_action": "approved rollback",
    }


def release_matrix() -> dict[str, object]:
    return {
        "applicability": "required",
        "reason": "Stateful cutover.",
        "baseline_ref": "pre-release-store-and-worker-readback",
        "rollback_ref": "release-runbook",
        "checks": [release_check("durable_record", "enquiry"),
                   release_check("worker", "notification-worker")],
    }


def decision(item_id: str, kind: str = "stable_choice", dependencies=None):
    return {
        "id": item_id,
        "kind": kind,
        "question": f"Choose {item_id}.",
        "dependencies": dependencies or [],
        "state": "pending",
        "answer_ref": "",
        "confirmed_value": "",
        "authority_ref": "",
        "ask_count": 0,
        "reask_reason": "",
    }


def pr_handoff(changed: bool = True) -> dict[str, object]:
    return {
        "worktree_changed": changed,
        "changed_paths": ["src/app.py"] if changed else [],
        "explicit_local_only": False,
        "override_ref": "",
        "state": "ready" if changed else "not_applicable",
        "branch": "codex/issue-1" if changed else "",
        "base_branch": "main" if changed else "",
        "head_revision": "a" * 40 if changed else "",
        "pr_url": "https://github.com/example/repository/pull/2" if changed else "",
        "pr_head_revision": "a" * 40 if changed else "",
        "pr_base_branch": "main" if changed else "",
        "pr_state": "draft" if changed else "",
        "review_state": "pending" if changed else "",
        "checks_state": "passed" if changed else "unavailable",
        "readback_ref": "github-pr-readback" if changed else "",
        "blocker": "",
        "existing_pr_url": "",
        "preserved_work_ref": "",
    }


def decomposition() -> dict[str, object]:
    child = {
        "issue": "https://github.com/example/repo/issues/11",
        "branch": "codex/child-11",
        "deliverable": "Complete the notification worker.",
        "dependencies": [],
        "test_refs": ["worker-unit", "queue-integration"],
        "pr_url": "https://github.com/example/repo/pull/12",
        "pr_base": "codex/parent-10",
        "head_revision": "b" * 40,
        "base_revision": "a" * 40,
        "checks_revision": "b" * 40,
        "review_revision": "b" * 40,
        "verification_revision": "b" * 40,
        "base_at_merge_revision": "a" * 40,
        "verification_state": "passed",
        "checks_state": "passed",
        "review_state": "passed",
        "state": "merged",
        "merge_evidence_ref": "child-pr-merge-readback",
        "issue_state": "closed",
        "issue_readback_ref": "child-issue-readback",
    }
    return {
        "mode": "parent",
        "decision_ref": "approved split plan",
        "parent_issue": "https://github.com/example/repo/issues/10",
        "parent_branch": "codex/parent-10",
        "default_branch": "main",
        "default_revision_at_branch": "a" * 40,
        "parent_base_revision": "a" * 40,
        "branch_creation_ref": "git-branch-readback",
        "children": [child],
        "combined_tests_state": "passed",
        "combined_tests_revision": "a" * 40,
        "combined_evidence_ref": "parent-integration-ci",
        "main_merge_state": "merged",
        "main_approval_ref": "user-approved-parent-branch",
        "main_approval_scope": "branch",
        "approved_branch": "codex/parent-10",
        "approved_head_revision": "a" * 40,
        "approved_pr_url": "https://github.com/example/repo/pull/13",
        "parent_head_revision": "a" * 40,
        "parent_pr_url": "https://github.com/example/repo/pull/13",
        "parent_pr_base": "main",
        "parent_pr_head_revision": "a" * 40,
        "parent_pr_child_issues": ["https://github.com/example/repo/issues/11"],
        "parent_pr_readback_ref": "parent-pr-readback",
        "main_auto_merge_state": "disabled",
    }


class WorkflowDeliveryTests(unittest.TestCase):
    def test_large_request_groups_coupled_outcomes_and_small_request_stays_single(self):
        outcomes = [
            {"id": "schema", "cohesion_group": "store", "deliverable": "Persist enquiries",
             "dependencies": [], "test_refs": ["migration-test"]},
            {"id": "api", "cohesion_group": "store", "deliverable": "Expose enquiries",
             "dependencies": ["schema"], "test_refs": ["api-test"]},
            {"id": "worker", "cohesion_group": "notifications", "deliverable": "Send alerts",
             "dependencies": ["api"], "test_refs": ["queue-test"]},
            {"id": "inbox", "cohesion_group": "inbox", "deliverable": "Show staff inbox",
             "dependencies": ["api"], "test_refs": ["browser-test"]},
        ]
        plan = workflow.decomposition_plan({"outcomes": outcomes,
                                             "one_pr_requested": False})
        self.assertEqual(plan["mode"], "parent")
        self.assertEqual(len(plan["children"]), 3)
        self.assertEqual(plan["children"][1]["dependencies"], ["store"])
        self.assertEqual(plan["children"][2]["dependencies"], ["store"])
        self.assertEqual(set(plan["children"][0]["test_refs"]),
                         {"migration-test", "api-test"})
        small = workflow.decomposition_plan({"outcomes": outcomes[:2],
                                              "one_pr_requested": False})
        self.assertEqual(small["mode"], "single")
        explicit = workflow.decomposition_plan({"outcomes": outcomes,
                                                 "one_pr_requested": True})
        self.assertEqual(explicit["reason"], "explicit_one_pr")

    def test_optional_contracts_validate_in_a_complete_task_record(self):
        record = task_run()
        record["release_invariants"] = release_matrix()
        record["interaction_decisions"] = {"questions": [decision("region")],
                                           "independent_work": []}
        record["pr_handoff"] = pr_handoff()
        single = decomposition()
        single.update(mode="single", children=[], main_merge_state="not_requested")
        record["decomposition"] = single
        workflow.validate_record(record, require_final=True)
        record["pr_handoff"]["pr_head_revision"] = "b" * 40
        with self.assertRaisesRegex(workflow.RecordError, "PR head does not match"):
            workflow.validate_record(record, require_final=True)

    def test_stateful_release_detects_missing_visible_record_and_stopped_worker(self):
        matrix = release_matrix()
        runtime = {"state": "available", "active_revision": "a" * 40}
        workflow.validate_release_invariants(matrix, release_readback=runtime, require_final=True)
        missing = copy.deepcopy(matrix)
        missing["checks"][0]["read_surface_state"] = "absent"
        with self.assertRaisesRegex(workflow.RecordError, "missing visible record"):
            workflow.validate_release_invariants(missing, release_readback=runtime)
        stale_visible = copy.deepcopy(matrix)
        stale_visible["checks"][0]["read_surface_freshness"] = "stale"
        with self.assertRaisesRegex(workflow.RecordError, "stale visible record"):
            workflow.validate_release_invariants(stale_visible, release_readback=runtime)
        stopped = copy.deepcopy(matrix)
        stopped["checks"][1]["runtime_state"] = "stopped"
        with self.assertRaisesRegex(workflow.RecordError, "stopped worker"):
            workflow.validate_release_invariants(stopped, release_readback=runtime)

    def test_stateful_release_blocks_unproven_or_stale_critical_flow(self):
        matrix = release_matrix()
        matrix["checks"].append(release_check("queue", "staff-alert-job"))
        matrix["checks"].append(release_check("external_flow", "customer-acknowledgement"))
        matrix["checks"][2]["live_effect"] = "synthetic"
        matrix["checks"][3]["live_effect"] = "synthetic"
        workflow.validate_release_invariants(
            matrix, release_readback={"state": "available", "active_revision": "a" * 40},
            require_final=True,
        )
        matrix["checks"][3]["state"] = "blocked"
        with self.assertRaisesRegex(workflow.RecordError, "critical release invariant"):
            workflow.validate_release_invariants(matrix, require_final=True)
        matrix["checks"][3]["state"] = "passed"
        matrix["checks"][3]["revision"] = "b" * 40
        with self.assertRaisesRegex(workflow.RecordError, "stale revision"):
            workflow.validate_release_invariants(
                matrix, release_readback={"state": "available", "active_revision": "a" * 40}
            )
        matrix["checks"][3]["revision"] = "a" * 40
        matrix["checks"][3]["live_effect"] = "not_exercised"
        with self.assertRaisesRegex(workflow.RecordError, "no end-to-end outcome proof"):
            workflow.validate_release_invariants(matrix)

    def test_provider_choices_bundle_and_dependents_wait(self):
        record = {"questions": [
            decision("billing-plan"), decision("admin-allowlist"),
            decision("oauth-consent", "just_in_time_consent", ["billing-plan"]),
            decision("db-private-entry", "private_entry", ["billing-plan"]),
        ], "independent_work": ["implement-auth-route"]}
        self.assertEqual(workflow.interaction_plan(record), {
            "action": "ask_grouped", "question_ids": ["billing-plan", "admin-allowlist"]
        })
        for item in record["questions"][:2]:
            item["ask_count"] = 1
        self.assertEqual(workflow.interaction_plan(record), {
            "action": "continue_independent_work", "question_ids": [],
            "work_refs": ["implement-auth-route"]
        })
        for item in record["questions"][:2]:
            item.update(state="answered", answer_ref="user-turn", confirmed_value="confirmed")
        self.assertEqual(workflow.interaction_plan(record), {
            "action": "ask_just_in_time", "question_ids": ["oauth-consent"]
        })
        record["questions"][2].update(state="approved", answer_ref="user-turn",
                                      authority_ref="exact-oauth-scope")
        self.assertEqual(workflow.interaction_plan(record)["question_ids"], ["db-private-entry"])
        record["questions"][3].update(state="answered", answer_ref="private-prompt-complete")
        self.assertEqual(workflow.interaction_plan(record)["action"], "continue_independent_work")

    def test_provider_reask_and_secret_entry_are_rejected(self):
        record = {"questions": [decision("project")]}
        record["questions"][0]["ask_count"] = 2
        with self.assertRaisesRegex(workflow.RecordError, "repeats without material change"):
            workflow.validate_interaction_decisions(record)
        record["questions"][0]["reask_reason"] = "Project changed."
        workflow.validate_interaction_decisions(record)
        private = {"questions": [decision("password", "private_entry")]}
        private["questions"][0]["confirmed_value"] = "must-not-store"
        with self.assertRaisesRegex(workflow.RecordError, "cannot store a private value"):
            workflow.validate_interaction_decisions(private)
        cycle = {"questions": [decision("a", dependencies=["b"]),
                               decision("b", dependencies=["a"])]}
        with self.assertRaisesRegex(workflow.RecordError, "cyclic dependencies"):
            workflow.validate_interaction_decisions(cycle)

    def test_changed_worktree_requires_exact_live_pr(self):
        handoff = pr_handoff()
        for path in ("src/app.py", "docs/guide.md", ".github/workflows/ci.yml"):
            handoff["changed_paths"] = [path]
            workflow.validate_pr_handoff(handoff, task_status="completed", require_final=True)
        stale = copy.deepcopy(handoff)
        stale["pr_head_revision"] = "b" * 40
        with self.assertRaisesRegex(workflow.RecordError, "PR head does not match"):
            workflow.validate_pr_handoff(stale, task_status="completed", require_final=True)
        pending = copy.deepcopy(handoff)
        pending["state"] = "pending"
        with self.assertRaisesRegex(workflow.RecordError, "lacks a reviewable PR"):
            workflow.validate_pr_handoff(pending, task_status="completed", require_final=True)
        workflow.validate_pr_handoff(pr_handoff(False), task_status="completed", require_final=True)
        failed = copy.deepcopy(handoff)
        failed["checks_state"] = "failed"
        with self.assertRaisesRegex(workflow.RecordError, "failing PR checks"):
            workflow.validate_pr_handoff(failed, task_status="completed", require_final=True)
        duplicate = copy.deepcopy(handoff)
        duplicate["existing_pr_url"] = "https://github.com/example/repo/pull/1"
        with self.assertRaisesRegex(workflow.RecordError, "not duplicated"):
            workflow.validate_pr_handoff(duplicate, task_status="completed", require_final=True)
        blocked = copy.deepcopy(handoff)
        blocked.update(state="blocked", blocker="remote permission denied",
                       preserved_work_ref="commit-a")
        workflow.validate_pr_handoff(blocked, task_status="blocked", require_final=True)
        blocked["preserved_work_ref"] = ""
        with self.assertRaisesRegex(workflow.RecordError, "preserved_work_ref"):
            workflow.validate_pr_handoff(blocked, task_status="blocked", require_final=True)
        closed = copy.deepcopy(handoff)
        closed["pr_state"] = "closed"
        with self.assertRaisesRegex(workflow.RecordError, "pr_state"):
            workflow.validate_pr_handoff(closed, task_status="completed", require_final=True)

    def test_parent_child_merge_needs_checked_children_and_branch_approval(self):
        plan = decomposition()
        workflow.validate_decomposition(plan)
        no_approval = copy.deepcopy(plan)
        no_approval["main_approval_ref"] = ""
        with self.assertRaisesRegex(workflow.RecordError, "main_approval_ref"):
            workflow.validate_decomposition(no_approval)
        fixed = copy.deepcopy(plan)
        fixed["parent_head_revision"] = "b" * 40
        fixed["parent_pr_head_revision"] = "b" * 40
        fixed["combined_tests_revision"] = "b" * 40
        workflow.validate_decomposition(fixed)
        legacy = copy.deepcopy(fixed)
        del legacy["main_approval_scope"]
        del legacy["approved_branch"]
        workflow.validate_decomposition(legacy)
        stale = copy.deepcopy(fixed)
        stale["main_approval_scope"] = "commit"
        with self.assertRaisesRegex(workflow.RecordError, "approval is stale"):
            workflow.validate_decomposition(stale)
        wrong_branch = copy.deepcopy(plan)
        wrong_branch["approved_branch"] = "codex/other-parent"
        with self.assertRaisesRegex(workflow.RecordError, "different parent branch"):
            workflow.validate_decomposition(wrong_branch)
        wrong_approval = copy.deepcopy(plan)
        wrong_approval["approved_pr_url"] = "https://github.com/example/repo/pull/14"
        with self.assertRaisesRegex(workflow.RecordError, "different parent PR"):
            workflow.validate_decomposition(wrong_approval)
        wrong_base = copy.deepcopy(plan)
        wrong_base["children"][0]["pr_base"] = "main"
        with self.assertRaisesRegex(workflow.RecordError, "wrong branch"):
            workflow.validate_decomposition(wrong_base)
        red_child = copy.deepcopy(plan)
        red_child["children"][0]["checks_state"] = "failed"
        with self.assertRaisesRegex(workflow.RecordError, "without required gates"):
            workflow.validate_decomposition(red_child)
        stale_child = copy.deepcopy(plan)
        stale_child["children"][0]["checks_revision"] = "c" * 40
        with self.assertRaisesRegex(workflow.RecordError, "stale head or parent-base"):
            workflow.validate_decomposition(stale_child)
        stale_parent_base = copy.deepcopy(plan)
        stale_parent_base["children"][0]["base_at_merge_revision"] = "c" * 40
        with self.assertRaisesRegex(workflow.RecordError, "stale head or parent-base"):
            workflow.validate_decomposition(stale_parent_base)
        auto_merge = copy.deepcopy(plan)
        auto_merge["main_merge_state"] = "approval_pending"
        auto_merge["main_auto_merge_state"] = "enabled"
        with self.assertRaisesRegex(workflow.RecordError, "auto-merge requires"):
            workflow.validate_decomposition(auto_merge)
        missing_link = copy.deepcopy(plan)
        missing_link["parent_pr_child_issues"] = []
        with self.assertRaisesRegex(workflow.RecordError, "does not link every child"):
            workflow.validate_decomposition(missing_link)
        open_child_issue = copy.deepcopy(plan)
        open_child_issue["children"][0]["issue_state"] = "open"
        with self.assertRaisesRegex(workflow.RecordError, "lacks closed issue readback"):
            workflow.validate_decomposition(open_child_issue)
        unfinished = copy.deepcopy(plan)
        unfinished["children"][0]["state"] = "pr_open"
        with self.assertRaisesRegex(workflow.RecordError, "unfinished children"):
            workflow.validate_decomposition(unfinished)
        cycle = copy.deepcopy(plan)
        cycle["children"][0]["dependencies"] = [cycle["children"][0]["issue"]]
        with self.assertRaisesRegex(workflow.RecordError, "invalid dependency"):
            workflow.validate_decomposition(cycle)

    def test_branch_approval_precedes_full_tests_but_does_not_bypass_merge_gates(self):
        for tests_state in ("pending", "failed"):
            with self.subTest(tests_state=tests_state):
                plan = decomposition()
                plan.update(main_merge_state="approved", combined_tests_state=tests_state,
                            combined_evidence_ref="")
                workflow.validate_decomposition(plan)
                plan["main_merge_state"] = "merged"
                with self.assertRaisesRegex(workflow.RecordError, "without combined tests"):
                    workflow.validate_decomposition(plan)
                plan.update(main_merge_state="approved", main_auto_merge_state="enabled")
                with self.assertRaisesRegex(workflow.RecordError, "without combined tests"):
                    workflow.validate_decomposition(plan)
        stale_readback = decomposition()
        stale_readback["parent_head_revision"] = "b" * 40
        with self.assertRaisesRegex(workflow.RecordError, "head does not match"):
            workflow.validate_decomposition(stale_readback)
        for tested_revision in (None, "b" * 40):
            plan = decomposition()
            if tested_revision is None:
                del plan["combined_tests_revision"]
            else:
                plan["combined_tests_revision"] = tested_revision
            with self.assertRaisesRegex(workflow.RecordError, "combined test revision"):
                workflow.validate_decomposition(plan)


def thread_page(thread_number: int) -> dict[str, object]:
    turns = []
    for index in range(10):
        turns.append({"id": f"turn-{thread_number}-{index}", "items": [
            {"id": f"user-{thread_number}-{index}", "type": "userMessage",
             "content": [{"type": "text", "text": "Please preserve the approval gate. " * 12}]},
            {"id": f"command-{thread_number}-{index}", "type": "commandExecution",
             "status": "completed", "command": "secret arguments omitted", "output": "x" * 9000},
            {"id": f"outcome-{thread_number}-{index}", "type": "agentMessage",
             "phase": "final_answer", "text": "The result is reviewable. " * 10},
        ]})
    turns[-1]["items"][0]["content"][0]["text"] = "Correction: keep the main merge approval."
    return {"thread": {"id": f"thread-{thread_number}", "createdAt": 1, "updatedAt": 2},
            "page": {"nextCursor": "older", "hasMore": True}, "turns": turns}


class ReflectionEvidenceTests(unittest.TestCase):
    def test_ten_long_sessions_fit_budget_and_keep_coverage(self):
        projected = [history.triage_page(thread_page(index)) for index in range(10)]
        output = json.dumps(projected)
        self.assertLess(len(output), 40_000)
        for item in projected:
            self.assertLessEqual(len(json.dumps(item, separators=(",", ":"))), 3200)
            self.assertEqual(len(item["turn_ids"]), 10)
            self.assertTrue(item["has_more"])
            self.assertEqual(item["page_next_cursor"], "older")
            self.assertEqual(item["tool_item_count"], 10)
            self.assertTrue(any("Correction:" in message["excerpt"] for message in item["messages"]))
            self.assertFalse(any("secret arguments" in message["excerpt"] for message in item["messages"]))

    def test_selected_detail_redacts_and_does_not_emit_other_items(self):
        page = thread_page(1)
        page["turns"][0]["items"][1]["output"] = (
            'worker failed to start; password=hunter2; Bearer abcdefghijklmnopqrstuvwxyz '
            '"access_token":"token-material"'
        )
        detail = history.detail_item(page, item_id="command-1-0")
        self.assertIn("worker failed to start", detail["excerpt"])
        self.assertNotIn("hunter2", json.dumps(detail))
        self.assertNotIn("abcdefghijkl", json.dumps(detail))
        self.assertNotIn("token-material", json.dumps(detail))
        self.assertNotIn("x" * 9000, json.dumps(detail))
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", json.dumps(detail))
        self.assertNotIn("command-1-1", json.dumps(detail))
        wrapped = {"content": [{"type": "text", "text": json.dumps(page)}]}
        self.assertEqual(history.triage_page(wrapped)["thread_id"], "thread-1")

    def test_older_page_correction_and_unread_cursor_remain_visible(self):
        recent = thread_page(1)
        recent["page"]["nextCursor"] = "older-page"
        older = thread_page(2)
        older["turns"][0]["items"][0]["content"][0]["text"] = (
            "Correction: the worker never started."
        )
        newer_summary = history.triage_page(recent)
        older_summary = history.triage_page(older, requested_cursor="older-page")
        self.assertEqual(newer_summary["page_next_cursor"], "older-page")
        self.assertTrue(newer_summary["has_more"])
        self.assertEqual(older_summary["requested_cursor"], "older-page")
        self.assertTrue(any("worker never started" in item["excerpt"]
                            for item in older_summary["messages"]))
        self.assertEqual(len(older_summary["turn_ids"]), len(older["turns"]))

    def test_many_failed_tools_keep_bounded_output_and_failure_count(self):
        page = thread_page(3)
        page["turns"][0]["items"].extend(
            {"id": f"failed-{index:04d}-long-identifier", "type": "mcpToolCall",
             "status": "failed", "error": "secret output" * 100}
            for index in range(150)
        )
        projection = history.triage_page(page)
        self.assertEqual(projection["failed_tool_item_count"], 150)
        self.assertLessEqual(len(json.dumps(projection, separators=(",", ":"))), 3200)
        self.assertTrue(projection["truncated"])

    def test_unchanged_complete_history_skips_trace_but_not_partial_or_changed(self):
        state = {"version": 1, "sessions": {
            "complete": {"coverage": "complete", "source_updated_at": "2026-09-29T00:00:00Z"},
            "partial": {"coverage": "partial", "source_updated_at": "2026-09-29T00:00:00Z"},
        }, "candidates": {"worker-gap": "https://github.com/example/repo/issues/134"}}
        self.assertEqual(reflection.session_read_decision(
            state, "complete", "2026-09-29T00:00:00Z"), "skip_unchanged_trace"
        )
        self.assertEqual(reflection.session_read_decision(
            state, "complete", "2026-09-29T01:00:00Z"), "read_trace"
        )
        self.assertEqual(reflection.session_read_decision(
            state, "partial", "2026-09-29T00:00:00Z"), "read_trace"
        )
        self.assertEqual(len(state["candidates"]), 1)


if __name__ == "__main__":
    unittest.main()
