from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


titles = load_module("session_title", ROOT / "plugins/agentic-workflows/hooks/session_title.py")
reflection = load_module("reflection_state", ROOT / "plugins/agentic-workflows/skills/session-reflection/scripts/reflection_state.py")


class TitleHookTests(unittest.TestCase):
    def test_packaged_hook_emits_codex_context_and_ignores_bad_input(self) -> None:
        plugin = ROOT / "plugins/agentic-workflows"
        definition = json.loads((plugin / "hooks/hooks.json").read_text())
        command = definition["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        self.assertIn("${PLUGIN_ROOT}/hooks/title_background.py", command)
        self.assertTrue(definition["hooks"]["UserPromptSubmit"][0]["hooks"][0]["async"])
        self.assertFalse((ROOT / "generated/claude/plugins/agentic-workflows/hooks").exists())
        with tempfile.TemporaryDirectory() as directory:
            script = plugin / "hooks/session_title.py"
            event = subprocess.run(
                [sys.executable, str(script), "event", "--file", str(Path(directory) / "state.json")],
                input=json.dumps({"session_id": "s", "turn_id": "t", "prompt": "Improve issue search"}),
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(json.loads(event.stdout)["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
            bad = subprocess.run(
                [sys.executable, str(script), "event", "--file", str(Path(directory) / "state.json")],
                input="not-json", capture_output=True, text=True, check=True,
            )
            self.assertEqual(bad.stdout, "")

    def test_exact_session_duplicate_and_stale_turn(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "titles.json"
            first = {"session_id": "session-a", "turn_id": "turn-1", "prompt": "Please implement issue 127"}
            output = titles.event(first, path)
            self.assertIn("sequence=1", output["hookSpecificOutput"]["additionalContext"])
            self.assertIsNone(titles.event(first, path))
            steering = {**first, "prompt": "Change the scope"}
            self.assertIn("sequence=2", titles.event(steering, path)["hookSpecificOutput"]["additionalContext"])
            second = {**first, "turn_id": "turn-2", "prompt": "Also fix the title"}
            titles.event(second, path)
            self.assertFalse(titles.record(path, "session-a", "turn-1", 1, "Implement issue 127"))
            self.assertTrue(titles.record(path, "session-a", "turn-2", 3, "Implement issue 127 and session titles"))
            self.assertEqual(titles.load(path)["sessions"]["session-a"]["title"], "Implement issue 127 and session titles")
            other = {"session_id": "session-b", "turn_id": "turn-1", "prompt": "Different work"}
            titles.event(other, path)
            self.assertNotIn("title", titles.load(path)["sessions"]["session-b"])

    def test_secret_prompt_not_persisted_or_injected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "titles.json"
            output = titles.event({"session_id": "s", "turn_id": "t", "prompt": "password=very-secret"}, path)
            self.assertNotIn("very-secret", json.dumps(output))
            self.assertNotIn("very-secret", path.read_text())
            self.assertIsNone(titles.event({"session_id": "s", "prompt": "invalid"}, path))

    def test_opt_out_and_event_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "titles.json"
            titles.save(path, {"version": 1, "sessions": {"s": {"disabled": True}}})
            self.assertIsNone(titles.event({"session_id": "s", "turn_id": "t", "prompt": "new"}, path))
            self.assertIsNone(titles.event({"session_id": "s", "turn_id": "t", "prompt": None}, path))
            self.assertFalse(titles.record(path, "s", "t", 1, "Title"))


class ReflectionLedgerTests(unittest.TestCase):
    def test_complete_source_timestamp_controls_trace_reuse(self) -> None:
        script = ROOT / "plugins/agentic-workflows/skills/session-reflection/scripts/reflection_state.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            subprocess.run([sys.executable, str(script), "--file", str(path), "session",
                            "session-a", "complete", "--source-updated-at",
                            "2026-09-29T00:00:00Z"], check=True, capture_output=True, text=True)
            same = subprocess.run([sys.executable, str(script), "--file", str(path),
                                   "session-check", "session-a", "--source-updated-at",
                                   "2026-09-29T00:00:00Z"], check=True, capture_output=True,
                                  text=True)
            changed = subprocess.run([sys.executable, str(script), "--file", str(path),
                                      "session-check", "session-a", "--source-updated-at",
                                      "2026-09-29T01:00:00Z"], check=True,
                                     capture_output=True, text=True)
            self.assertEqual(json.loads(same.stdout)["decision"], "skip_unchanged_trace")
            self.assertEqual(json.loads(changed.stdout)["decision"], "read_trace")

    def test_rerun_reuses_links_without_transcripts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            state = reflection.load(path)
            state["sessions"]["session-a"] = "complete"
            state["sessions"]["session-b"] = "unavailable"
            state["candidates"]["workflow-dedup"] = "https://github.com/anhminhsoft/agentic-workflows/issues/127"
            reflection.save(path, state)
            rerun = reflection.load(path)
            self.assertEqual(rerun, state)
            self.assertEqual(len(rerun["candidates"]), 1)
            self.assertNotIn("raw transcript", path.read_text())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
