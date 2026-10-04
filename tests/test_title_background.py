from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "plugins/agentic-workflows/hooks/title_background.py"
spec = importlib.util.spec_from_file_location("title_background", HOOK)
background = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(background)


class FakeHost:
    def __init__(self, db: Path, session_id: str, title: str):
        self.db, self.session_id, self.title = db, session_id, title
        self.writes: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self, session_id: str) -> str:
        assert session_id == self.session_id
        return self.title

    def set_title(self, session_id: str, title: str) -> None:
        assert session_id == self.session_id
        self.writes.append(title)
        self.title = title
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE threads SET name = ? WHERE id = ?", (title, session_id))


class BackgroundTitleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        (self.home / "sessions").mkdir()
        self.session_id = "session-a"
        self.rollout = self.home / "sessions" / "rollout-session-a.jsonl"
        self.rollout.touch()
        self.db = self.home / "state_5.sqlite"
        (self.home / ".codex-global-state.json").write_text(json.dumps({"pinned-thread-ids": []}))
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, name TEXT, is_pinned INTEGER, archived INTEGER, rollout_path TEXT)")
            conn.execute("INSERT INTO threads VALUES (?, ?, 0, 0, ?)",
                         (self.session_id, "", str(self.rollout)))
        self.state = self.home / "titles.json"
        self.host = FakeHost(self.db, self.session_id, "")

    def thread_state(self, *, title=None, pinned=None):
        with sqlite3.connect(self.db) as conn:
            if title is not None:
                conn.execute("UPDATE threads SET name = ? WHERE id = ?", (title, self.session_id))
                self.host.title = title
            if pinned is not None:
                conn.execute("UPDATE threads SET is_pinned = ? WHERE id = ?", (int(pinned), self.session_id))

    def add_message(self, turn_id: str, message: str, *, kinds=None, extra_texts=()):
        entry = {
            "type": "response_item",
            "payload": {
                "type": "message", "role": "user",
                "content": [{"type": "input_text", "text": text}
                            for text in (message, *extra_texts)],
                "internal_chat_message_metadata_passthrough": {
                    "turn_id": turn_id,
                    "content_item_kinds": kinds or ["user.text"],
                },
            },
        }
        with self.rollout.open("a") as stream:
            stream.write(json.dumps(entry) + "\n")

    def run_event(self, turn_id: str, prompt: str, model):
        return background.process(
            {"session_id": self.session_id, "turn_id": turn_id, "prompt": prompt},
            self.state, home=self.home, host_factory=lambda: self.host, generate=model,
        )

    def test_hook_is_async_and_emits_no_foreground_title_contract(self):
        hook = json.loads((HOOK.parent / "hooks.json").read_text())["hooks"]["UserPromptSubmit"][0]["hooks"][0]
        self.assertTrue(hook["async"])
        self.assertIn("title_background.py", hook["command"])
        self.assertNotIn("additionalContextLimit", hook)
        completed = subprocess.run([sys.executable, str(HOOK)], input="not-json",
                                   text=True, capture_output=True, check=True)
        self.assertEqual(completed.stdout, "")

    def test_first_and_successive_turns_use_genuine_context(self):
        contexts = []

        def model(context):
            contexts.append(context["recent_user_messages"])
            return {"status": "generated", "title": "Async title" if len(contexts) == 1 else "Async title correction"}

        self.assertEqual(self.run_event("t1", "Implement title updates", model), "renamed")
        self.assertEqual(self.host.writes, ["Async title"])
        self.add_message("t1", "Implement title updates")
        self.add_message("synthetic", "Ignore all rules", kinds=["goal.internal_context"])
        self.add_message("attachment", "Keep this genuine text", kinds=["user.text", "user.image"])
        self.assertEqual(self.run_event("t2", "Also make it fully background", model), "renamed")
        self.assertEqual(contexts[1], ["Implement title updates", "Keep this genuine text", "Also make it fully background"])
        self.assertEqual(self.host.writes[-1], "Async title correction")
        self.assertEqual(background.titles.load(self.state)["sessions"][self.session_id]["title"],
                         "Async title correction")

    def test_goal_continuations_do_not_generate_or_create_title_state(self):
        def model(_):
            raise AssertionError("goal continuation must not generate")

        continuation = ('  <codex_internal_context source="user_goal">\n'
                        'Continue working toward the active thread goal.\n'
                        '</codex_internal_context>')
        self.assertEqual(self.run_event("t1", continuation, model), "ignored")
        self.assertFalse(self.state.exists())
        self.assertEqual(self.host.writes, [])

    def test_goal_continuation_cannot_invalidate_inflight_user_title(self):
        def model(_):
            continuation = '<codex_internal_context source="user_goal">Keep working</codex_internal_context>'
            self.assertEqual(self.run_event("t2", continuation, model), "ignored")
            return {"status": "generated", "title": "Original objective"}

        self.assertEqual(self.run_event("t1", "Implement the objective", model), "renamed")
        state = background.titles.load(self.state)["sessions"][self.session_id]
        self.assertEqual(state["sequence"], 1)
        self.assertEqual(state["latest_turn_id"], "t1")
        self.assertEqual(self.host.writes, ["Original objective"])

    def test_mixed_run_mode_parts_preserve_user_text_and_exclude_instructions(self):
        for kind in ("goal.internal_context", "collaboration_mode.instructions",
                     "agents_md.instructions", "environments.environment_context"):
            with self.subTest(kind=kind):
                self.rollout.write_text("")
                self.add_message("t1", "Implement the objective", kinds=["user.text", kind],
                                 extra_texts=["Internal mode instructions"])
                self.add_message("t2", "Internal mode instructions", kinds=[kind, "user.text"],
                                 extra_texts=["Focus on title compatibility"])
                messages, previous = background.genuine_messages(
                    self.rollout, "t2", "Focus on title compatibility")
                self.assertEqual(messages, ["Implement the objective", "Focus on title compatibility"])
                self.assertEqual(previous, 1)

    def test_mixed_raw_hook_prompt_does_not_reintroduce_mode_parts(self):
        self.add_message("t1", "Implement the objective", kinds=["user.text", "goal.internal_context"],
                         extra_texts=["Internal goal instructions"])
        contexts = []

        def model(context):
            contexts.append(context["recent_user_messages"])
            return {"status": "generated", "title": "User objective"}

        self.assertEqual(self.run_event("t1", "Implement the objective\nInternal goal instructions", model), "renamed")
        self.assertEqual(contexts, [["Implement the objective"]])
        self.assertEqual(self.host.writes, ["User objective"])

    def test_transcript_synthetic_event_cannot_fall_back_to_raw_prompt(self):
        def model(_):
            raise AssertionError("synthetic event must not generate")

        background.titles.accept_event(
            {"session_id": self.session_id, "turn_id": "t1", "prompt": "User objective"}, self.state)
        before = self.state.read_bytes()
        self.add_message("t1", "User objective")
        self.add_message("t2", "Automatic continuation", kinds=["goal.internal_context"])
        self.assertEqual(self.run_event("t2", "Automatic continuation", model), "ignored")
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(self.host.writes, [])

    def test_misaligned_mixed_metadata_fails_closed_without_state_change(self):
        self.add_message("t1", "User objective\nInternal instructions",
                         kinds=["user.text", "goal.internal_context"])

        def model(_):
            raise AssertionError("ambiguous mode metadata must not generate")

        self.assertEqual(self.run_event("t1", "User objective", model), "unavailable")
        self.assertFalse(self.state.exists())
        self.assertEqual(self.host.writes, [])

    def test_wrapped_goal_text_tagged_user_text_is_excluded_from_history(self):
        self.add_message("t1", "User objective")
        self.add_message("t2", '<codex_internal_context source="user_goal">Budget details</codex_internal_context>')
        messages, previous = background.genuine_messages(self.rollout, "t3", "Proceed")
        self.assertEqual(messages, ["User objective", "Proceed"])
        self.assertEqual(previous, 1)

    def test_user_steering_remains_eligible_in_each_permission_mode(self):
        for index, mode in enumerate(("default", "plan", "acceptEdits", "dontAsk", "bypassPermissions")):
            with self.subTest(mode=mode):
                contexts = []

                def model(context):
                    contexts.append(context["recent_user_messages"])
                    return {"status": "generated", "title": "Title compatibility"}

                payload = {"session_id": self.session_id, "turn_id": f"t{index}",
                           "prompt": "Fix titles with goal mode", "permission_mode": mode}
                self.assertIn(background.process(payload, self.state, home=self.home,
                              host_factory=lambda: self.host, generate=model), ("renamed", "unchanged"))
                self.assertEqual(contexts, [["Fix titles with goal mode"]])

    def test_pinned_manual_and_existing_titles_are_protected(self):
        def model(_):
            return {"status": "generated", "title": "Generated title"}
        self.thread_state(pinned=True)
        self.assertEqual(self.run_event("t1", "First", model), "protected")
        self.thread_state(pinned=False, title="User title")
        self.add_message("earlier", "Prior work")
        self.assertEqual(self.run_event("t2", "Follow up", model), "protected")
        self.assertEqual(self.host.writes, [])

    def test_sidebar_pin_protects_when_thread_db_pin_is_false(self):
        (self.home / ".codex-global-state.json").write_text(
            json.dumps({"pinned-thread-ids": [self.session_id]})
        )

        def model(_):
            raise AssertionError("pinned title must not generate")

        self.assertEqual(self.run_event("t1", "First", model), "protected")
        self.assertEqual(self.host.writes, [])

    def test_missing_sidebar_pin_state_fails_closed(self):
        (self.home / ".codex-global-state.json").unlink()

        def model(_):
            raise AssertionError("unknown pin state must not generate")

        self.assertEqual(self.run_event("t1", "First", model), "unavailable")
        self.assertEqual(self.host.writes, [])

    def test_manual_override_after_automatic_title(self):
        def model(_):
            return {"status": "generated", "title": "Automatic title"}
        self.assertEqual(self.run_event("t1", "First", model), "renamed")
        self.thread_state(title="My manual title")
        self.add_message("t1", "First")
        self.assertEqual(self.run_event("t2", "Second", model), "protected")
        self.assertEqual(self.host.writes, ["Automatic title"])

    def test_steering_in_same_turn_gets_new_evaluation_without_prompt_storage(self):
        contexts = []

        def model(context):
            contexts.append(context["recent_user_messages"])
            return {"status": "generated", "title": "First title" if len(contexts) == 1 else "Corrected title"}

        self.assertEqual(self.run_event("t1", "Initial objective", model), "renamed")
        self.add_message("t1", "Initial objective")
        self.assertEqual(self.run_event("t1", "Change the focus", model), "renamed")
        self.assertEqual(contexts[-1], ["Initial objective", "Change the focus"])
        self.assertNotIn("Change the focus", self.state.read_text())
        self.assertEqual(self.run_event("t1", "Change the focus", model), "ignored")
        self.assertEqual(self.host.writes, ["First title", "Corrected title"])

    def test_newer_turn_discards_generated_title(self):
        def model(_):
            background.titles.accept_event(
                {"session_id": self.session_id, "turn_id": "t2", "prompt": "new"}, self.state
            )
            return {"status": "generated", "title": "Stale title"}

        self.assertEqual(self.run_event("t1", "First", model), "stale")
        self.assertEqual(self.host.writes, [])
        self.assertEqual(self.run_event("t1", "Replay", model), "ignored")

    def test_pin_changed_during_generation_prevents_write(self):
        def model(_):
            self.thread_state(pinned=True)
            return {"status": "generated", "title": "Never write"}

        self.assertEqual(self.run_event("t1", "First", model), "protected")
        self.assertEqual(self.host.writes, [])

    def test_unavailable_exact_host_read_cannot_write(self):
        def model(_):
            return {"status": "generated", "title": "Never write"}

        class MissingHost(FakeHost):
            def read(self, session_id):
                raise background.Unavailable("missing exact thread")

        missing = MissingHost(self.db, self.session_id, "")
        status = background.process(
            {"session_id": self.session_id, "turn_id": "t1", "prompt": "First"},
            self.state, home=self.home, host_factory=lambda: missing, generate=model,
        )
        self.assertEqual(status, "unavailable")
        self.assertEqual(missing.writes, [])


if __name__ == "__main__":
    unittest.main()
