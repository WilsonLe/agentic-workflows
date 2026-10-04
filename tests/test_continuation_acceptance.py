from __future__ import annotations

import copy
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "plugins/agentic-workflows/skills"


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ASYNC = load(
    "async_feedback", "standard-development-workflow/scripts/check_async_feedback.py"
)
GOAL = load("goal_continuity", "agentic-workflows/scripts/check_goal_continuity.py")


def frame(event, operation=None, pending=(), **extras):
    return {
        "at_ms": 0,
        "event": event,
        "operation": operation,
        "pending": list(pending),
        "indicators": [list(pending)] if pending else [],
        "busy": list(pending),
        "feedback": [operation] if event == "start" else [],
        "action_at_ms": 0,
        "terminal_observed": event == "finish",
        **extras,
    }


def async_trace():
    return {
        "evidence_kind": "fixture",
        "max_indicators": 1,
        "policy_source": "Project A guide",
        "feedback_deadline_ms": 100,
        "timing_source": "fixture observation budget",
        "frames": [
            frame("start", "a", ["a"]),
            frame("sample", pending=["a"]),
            frame("finish", "a", outcome="ready", ready=["a"]),
        ],
    }


def goal_turn(**extras):
    return {
        "observed_goal_id": "goal-1",
        "host_scope": ["chrome", "safari"],
        "remaining": ["chrome", "safari"],
        "progress": False,
        "independent_work": False,
        "controls_available": True,
        "scope_update_supported": False,
        "blocker": "provider unavailable",
        "observed_status": "active",
        **extras,
    }


def goal_trace(turns):
    return {
        "goal_id": "goal-1",
        "initial_scope": ["chrome", "safari"],
        "blocked_after": 3,
        "host_contract": "current host update_goal contract",
        "turns": turns,
    }


class AsyncObservationTests(unittest.TestCase):
    def test_stale_runtime_observation_cannot_pass(self):
        trace = async_trace()
        trace["expected_runtime"] = {
            "revision": "new",
            "environment": "staging",
            "surface": "login",
        }
        trace["observed_runtime"] = dict(trace["expected_runtime"], revision="old")
        self.assertFalse(ASYNC.check_trace(trace)["passed"])
        trace["observed_runtime"] = dict(trace["expected_runtime"])
        self.assertTrue(ASYNC.check_trace(trace)["passed"])

    def test_delayed_work_and_terminal_ready_pass(self):
        trace = async_trace()
        trace["frames"][1]["at_ms"] = 1500
        trace["frames"][2]["at_ms"] = 2000
        result = ASYNC.check_trace(trace)
        self.assertTrue(result["passed"])
        self.assertFalse(result["runtime_verified"])

    def test_disabled_only_control_fails(self):
        trace = async_trace()
        trace["frames"][0].update(feedback=[], indicators=[])
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_stacked_shared_button_and_global_indicators_fail_project_limit(self):
        trace = async_trace()
        trace["frames"][0]["indicators"] = [["a"], ["a"], ["a"]]
        self.assertFalse(ASYNC.check_trace(trace)["passed"])
        del trace["max_indicators"]
        self.assertTrue(ASYNC.check_trace(trace)["passed"])

    def test_accessible_busy_missing_fails(self):
        trace = async_trace()
        trace["frames"][1]["busy"] = []
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_partial_ready_and_missing_terminal_fail(self):
        for change in ("partial", "terminal"):
            with self.subTest(change=change):
                trace = async_trace()
                if change == "partial":
                    trace["frames"][1]["ready"] = ["a"]
                else:
                    trace["frames"].pop()
                self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_warm_revalidation_keeps_cached_content_and_feedback(self):
        trace = async_trace()
        trace["frames"][0].update(cached_ready=True, ready=["a"])
        trace["frames"][1]["ready"] = ["a"]
        self.assertTrue(ASYNC.check_trace(trace)["passed"])
        trace["frames"][0]["ready"] = []
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_late_initial_feedback_and_unobserved_failure_fail(self):
        trace = async_trace()
        for observed in trace["frames"]:
            observed["at_ms"] = 1500
        self.assertFalse(ASYNC.check_trace(trace)["passed"])
        trace = async_trace()
        trace["frames"][-1].update(outcome="failed", terminal_observed=False)
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_overlap_does_not_clear_another_operations_feedback(self):
        trace = async_trace()
        trace["frames"] = [
            frame("start", "a", ["a"]),
            frame("start", "b", ["a", "b"]),
            frame("finish", "b", ["a"], outcome="cancelled"),
            frame("sample", pending=["a"]),
            frame("finish", "a", outcome="empty"),
        ]
        self.assertTrue(ASYNC.check_trace(trace)["passed"])
        trace["frames"][2]["indicators"] = []
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_failure_retry_and_stale_indicator(self):
        trace = async_trace()
        trace["frames"] = [
            frame("start", "a", ["a"]),
            frame("finish", "a", outcome="failed"),
            frame("start", "retry", ["retry"], retry_of="a"),
            frame("finish", "retry", outcome="ready", ready=["retry"]),
        ]
        self.assertTrue(ASYNC.check_trace(trace)["passed"])
        trace["frames"][1]["indicators"] = [["a"]]
        self.assertFalse(ASYNC.check_trace(trace)["passed"])

    def test_empty_trace_unapproved_limit_and_bad_sequence_rejected(self):
        for field, value in (
            ("frames", []),
            ("max_indicators", True),
            ("policy_source", ""),
        ):
            trace = async_trace()
            trace[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                ASYNC.check_trace(trace)
        trace = async_trace()
        trace["frames"][0]["event"] = "finish"
        with self.assertRaises(ValueError):
            ASYNC.check_trace(trace)


class GoalContinuationTests(unittest.TestCase):
    def test_another_goals_terminal_readback_does_not_pass(self):
        trace = goal_trace(
            [
                goal_turn(
                    remaining=[],
                    observed_status="complete",
                    claims_terminal=True,
                    observed_goal_id="different-goal",
                )
            ]
        )
        self.assertFalse(GOAL.check_trace(trace)["passed"])

    def test_unchanged_blocker_transitions_only_at_host_threshold(self):
        result = GOAL.check_trace(goal_trace([goal_turn() for _ in range(3)]))
        self.assertEqual(
            [turn["decision"] for turn in result["turns"]],
            ["continue", "continue", "blocked"],
        )

    def test_active_unchanged_continuation_after_threshold_is_rejected(self):
        trace = goal_trace([goal_turn() for _ in range(4)])
        self.assertFalse(GOAL.check_trace(trace)["passed"])
        trace["turns"][-1]["observed_status"] = "blocked"
        self.assertTrue(GOAL.check_trace(trace)["passed"])

    def test_progress_independent_work_and_changed_blocker_reset_count(self):
        for middle in (
            goal_turn(progress=True),
            goal_turn(independent_work=True),
            goal_turn(blocker="different condition"),
        ):
            trace = goal_trace([goal_turn(), middle, goal_turn()])
            result = GOAL.check_trace(trace)
            self.assertEqual(result["turns"][-1]["blocked_turns"], 1)

    def test_scope_reduction_completes_authorized_remaining_outcome(self):
        trace = goal_trace(
            [
                goal_turn(
                    explicit_scope=["chrome"],
                    remaining=[],
                    observed_status="complete",
                    claims_terminal=True,
                )
            ]
        )
        result = GOAL.check_trace(trace)
        self.assertTrue(result["passed"])
        self.assertEqual(result["turns"][0]["decision"], "complete")
        self.assertEqual(
            result["turns"][0]["scope_reconciliation"], "report-stale-host-scope"
        )
        trace["turns"][0]["remaining"] = ["safari"]
        with self.assertRaises(ValueError):
            GOAL.check_trace(trace)

    def test_scope_change_resets_block_audit(self):
        trace = goal_trace(
            [
                goal_turn(),
                goal_turn(),
                goal_turn(explicit_scope=["chrome"], remaining=["chrome"]),
            ]
        )
        self.assertEqual(GOAL.check_trace(trace)["turns"][-1]["blocked_turns"], 1)

    def test_resume_after_blocked_starts_fresh_audit(self):
        trace = goal_trace(
            [goal_turn() for _ in range(3)]
            + [goal_turn(explicit_resume=True), goal_turn(), goal_turn()]
        )
        decisions = [turn["decision"] for turn in GOAL.check_trace(trace)["turns"]]
        self.assertEqual(decisions, ["continue", "continue", "blocked"] * 2)

    def test_pause_requires_explicit_request_and_resume(self):
        trace = goal_trace(
            [
                goal_turn(explicit_pause=True),
                goal_turn(),
                goal_turn(explicit_resume=True),
            ]
        )
        self.assertEqual(
            [turn["decision"] for turn in GOAL.check_trace(trace)["turns"]],
            ["paused", "paused", "continue"],
        )

    def test_unavailable_control_and_false_terminal_readback_fail_claim(self):
        for change in ({"observed_status": "active"}, {"controls_available": False}):
            trace = goal_trace(
                [
                    goal_turn(
                        remaining=[], observed_status="complete", claims_terminal=True
                    )
                ]
            )
            trace["turns"][0].update(change)
            self.assertFalse(GOAL.check_trace(trace)["passed"])

    def test_remaining_work_prevents_complete_and_early_blocked_claim(self):
        for status in ("complete", "blocked", "paused"):
            trace = goal_trace(
                [goal_turn(observed_status=status, claims_terminal=True)]
            )
            self.assertFalse(GOAL.check_trace(trace)["passed"])

    def test_malformed_trace_fails_closed(self):
        trace = goal_trace([goal_turn()])
        for value in (True, 0, None):
            changed = copy.deepcopy(trace)
            changed["blocked_after"] = value
            with self.assertRaises(ValueError):
                GOAL.check_trace(changed)
        for flag in ("explicit_pause", "explicit_resume", "claims_terminal"):
            changed = copy.deepcopy(trace)
            changed["turns"][0][flag] = "true"
            with self.assertRaises(ValueError):
                GOAL.check_trace(changed)


class ReplayCommandTests(unittest.TestCase):
    def test_documented_examples_run_successfully(self):
        examples = (
            (
                ASYNC,
                "standard-development-workflow/references/composed-async-feedback.md",
            ),
            (GOAL, "agentic-workflows/references/ordinary-goal-continuity.md"),
        )
        for module, reference in examples:
            source = (ROOT / reference).read_text()
            payload = json.loads(
                re.search(r"```json\n(.*?)\n```", source, re.DOTALL).group(1)
            )
            with self.subTest(reference=reference):
                self.assertTrue(module.check_trace(payload)["passed"])

    def test_replay_cli_exit_codes_and_json_output(self):
        cases = ((ASYNC, async_trace()), (GOAL, goal_trace([goal_turn()])))
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / "trace.json"
            for module, payload in cases:
                file.write_text(json.dumps(payload))
                result = subprocess.run(
                    [sys.executable, module.__file__, str(file)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(result.stdout)["passed"])
                failed = copy.deepcopy(payload)
                if module is ASYNC:
                    failed["frames"][0]["feedback"] = []
                else:
                    failed["turns"][0].update(
                        claims_terminal=True, observed_status="complete"
                    )
                file.write_text(json.dumps(failed))
                result = subprocess.run(
                    [sys.executable, module.__file__, str(file)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 3)
                self.assertFalse(json.loads(result.stdout)["passed"])
                file.write_text("{}")
                result = subprocess.run(
                    [sys.executable, module.__file__, str(file)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("error", json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
