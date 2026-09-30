from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/agentic-workflows/hooks/workflow_route.py"


def load_route():
    spec = importlib.util.spec_from_file_location("workflow_route", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route = load_route()


class WorkflowRouteHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repository)], check=True)
        self.nested = self.repository / "src"
        self.nested.mkdir()
        self.other = self.root / "ordinary-directory"
        self.other.mkdir()

    def payload(self, prompt: str, *, cwd: Path | None = None, mode: str = "default") -> dict:
        return {
            "session_id": "session-a",
            "turn_id": "turn-a",
            "cwd": str(cwd or self.nested),
            "prompt": prompt,
            "permission_mode": mode,
        }

    def context(self, payload: dict) -> str:
        result = route.event(payload)
        self.assertIsNotNone(result)
        self.assertEqual(result["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        return result["hookSpecificOutput"]["additionalContext"]

    def test_plain_edit_and_terse_followup_receive_the_same_conditional_route(self) -> None:
        initial = self.context(self.payload("Hide Website Templates in the header and add a footer link"))
        followup = self.context(self.payload("Proceed"))
        self.assertEqual(initial, followup)
        self.assertIn(str(route.SKILL), initial)
        self.assertIn("For ordinary tracked edits", initial)
        self.assertIn("open or update a reviewable PR before the final response", initial)
        self.assertIn("Read back its URL, exact head, base, state, and checks", initial)
        self.assertIn("a pushed branch alone is incomplete", initial)
        self.assertIn("directly invoked", initial)

    def test_read_only_local_only_and_plan_boundaries_are_present(self) -> None:
        read_only = self.context(self.payload("Inspect the navigation code"))
        self.assertIn("Read-only, no-diff, and explicit local-only work does not need a PR", read_only)
        local_only = self.context(self.payload("Make the edit but keep it local"))
        self.assertIn("explicit local-only work", local_only)
        plan = self.context(self.payload("Plan a navigation change", mode="plan"))
        self.assertIn("plan the work without mutating", plan)
        self.assertNotIn("Current mode is Plan", read_only)

    def test_non_git_and_invalid_payloads_emit_no_route(self) -> None:
        self.assertIsNone(route.event(self.payload("Edit a file", cwd=self.other)))
        self.assertIsNone(route.event(self.payload("Edit a file", cwd=self.root / "missing")))
        self.assertIsNone(route.event({"cwd": str(self.nested), "prompt": None}))
        self.assertIsNone(route.event({"cwd": None, "prompt": "Edit a file"}))

    def test_hook_keeps_prompt_contents_out_of_output(self) -> None:
        secret = "password=synthetic-private-value"
        output = self.context(self.payload(f"Edit the page; {secret}"))
        self.assertNotIn(secret, output)
        self.assertNotIn("Edit the page", output)

    def test_packaged_command_is_registered_and_bad_json_is_nonblocking(self) -> None:
        hooks = json.loads((SCRIPT.parent / "hooks.json").read_text())
        handlers = hooks["hooks"]["UserPromptSubmit"][0]["hooks"]
        self.assertIn("title_background.py", handlers[0]["command"])
        self.assertTrue(handlers[0]["async"])
        self.assertIn("workflow_route.py", handlers[1]["command"])
        self.assertLessEqual(
            len(self.context(self.payload("Change the footer navigation", mode="plan"))),
            handlers[1]["additionalContextLimit"],
        )
        valid = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(self.payload("Change the footer navigation")),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            json.loads(valid.stdout)["hookSpecificOutput"]["hookEventName"],
            "UserPromptSubmit",
        )
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="not-json",
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(completed.stdout, "")


if __name__ == "__main__":
    unittest.main()
