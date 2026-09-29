from __future__ import annotations
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tests.test_session_reflection_titles import titles

generator = titles._generator


def response(title="Implement workflow improvements"):
    return subprocess.CompletedProcess(
        [],
        0,
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": title},
                    }
                ),
                json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {"input_tokens": 50, "output_tokens": 5},
                    }
                ),
            ]
        ),
        "",
    )


class GeneratorTests(unittest.TestCase):
    def test_limits_and_sensitive_output(self):
        for title in (
            "",
            "one\ntwo",
            "word " * 11,
            "x" * 101,
            " user ",
            "password=abc",
            "me@example.com",
            '"Title"',
        ):
            self.assertFalse(generator.valid_title(title), title)
        self.assertTrue(generator.valid_title(" ".join(["word"] * 10)))

    def test_ephemeral_fast_low_model_independent_of_foreground(self):
        calls = []

        def runner(command, **kwargs):
            calls.append((command, kwargs))
            return response()

        result = generator.generate(
            {"recent_user_messages": ["Implement #148", "Proceed"]}, runner=runner
        )
        self.assertEqual(result["status"], "generated")
        command, options = calls[0]
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn(generator.DEFAULT_MODEL, command)
        self.assertIn('model_reasoning_effort="low"', command)
        self.assertIn("hooks", command)
        self.assertIn("shell_tool", command)
        self.assertLessEqual(options["timeout"], 12)
        self.assertEqual(result["usage"]["output_tokens"], 5)

    def test_invalid_or_unavailable_model_never_falls_back(self):
        for outcome in [
            response(" ".join(["word"] * 11)),
            subprocess.CompletedProcess([], 1, "", "private error"),
        ]:
            calls = []

            def runner(*args, **kwargs):
                calls.append(1)
                return outcome

            result = generator.generate(
                {"recent_user_messages": ["Proceed"]}, runner=runner
            )
            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(len(calls), 1)
            self.assertNotIn("private", json.dumps(result))

        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired("codex", 12)

        self.assertEqual(
            generator.generate({"recent_user_messages": ["Title"]}, runner=timeout)[
                "reason"
            ],
            "timeout",
        )

    def test_context_bounded_and_redacted(self):
        text = generator.context_text(
            {
                "recent_user_messages": ["Implement title updates"]
                + ["x" * 8000] * 20
                + ["password=abc me@example.com /Users/someone/private"]
            }
        )
        self.assertLessEqual(len(text), 6000)
        self.assertIn("Implement title updates", text)
        self.assertNotIn("password=abc", text)
        self.assertNotIn("me@example.com", text)

    def test_stale_inflight_generation_is_discarded(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "state.json"
            titles.event({"session_id": "s", "turn_id": "t1", "prompt": "first"}, path)

            def changed(context):
                titles.event(
                    {"session_id": "s", "turn_id": "t2", "prompt": "new"}, path
                )
                return {"status": "generated", "title": "Old title"}

            with patch.object(generator, "generate", changed):
                self.assertEqual(
                    titles.generate_candidate(path, "s", "t1", 1, {}),
                    {"status": "stale"},
                )
            self.assertNotIn("Old title", path.read_text())
            self.assertIsNone(
                titles.event(
                    {"session_id": "s", "turn_id": "t1", "prompt": "replay"}, path
                )
            )

    def test_current_generated_candidate_and_opt_out(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "state.json"
            titles.event({"session_id": "s", "turn_id": "t", "prompt": "first"}, path)
            with patch.object(
                generator,
                "generate",
                return_value={"status": "generated", "title": "New title"},
            ):
                self.assertEqual(
                    titles.generate_candidate(path, "s", "t", 1, {})["title"],
                    "New title",
                )
            self.assertTrue(titles.current(path, "s", "t", 1))
            state = titles.load(path)
            state["sessions"]["s"]["disabled"] = True
            titles.save(path, state)
            self.assertFalse(titles.current(path, "s", "t", 1))


class InvalidCompletionTests(unittest.TestCase):
    def test_partial_or_tool_response_cannot_supply_title(self):
        for events in [
            [
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": "Title"},
                }
            ],
            [
                {
                    "type": "item.completed",
                    "item": {"type": "command_execution", "text": "Title"},
                },
                {"type": "turn.completed"},
            ],
            [{"type": "turn.failed"}],
        ]:

            def runner(*args, **kwargs):
                return subprocess.CompletedProcess(
                    [], 0, "\n".join(map(json.dumps, events)), ""
                )

            result = generator.generate(
                {"recent_user_messages": ["Title"]}, runner=runner
            )
            self.assertEqual(result["status"], "unavailable")

    def test_escaped_context_stays_valid_json(self):
        data = generator.context_text({"recent_user_messages": ['"' * 700] * 8})
        self.assertEqual(len(json.loads(data)["recent_user_messages"]), 8)
        self.assertLessEqual(len(data), 6000)
