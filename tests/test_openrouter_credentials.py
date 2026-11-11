"""Guard explicit OpenRouter runtime authentication without a checkout key store."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/agentic-workflows/scripts"
sys.path.insert(0, str(SCRIPTS))
stt = importlib.import_module("openrouter_transcribe")
KEY = "synthetic-runtime-key-no-live-access"


class OpenRouterRuntimeCredentialsTests(unittest.TestCase):
    def test_explicit_environment_key_needs_no_file_or_git_discovery(self) -> None:
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": KEY}, clear=True):
            with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("no file read")):
                with mock.patch.object(stt.subprocess, "run", side_effect=AssertionError("no discovery")):
                    self.assertEqual(stt.load_api_key(), KEY)

    def test_missing_or_malformed_key_fails_without_echoing_it(self) -> None:
        for value in ("", "secret with space", "secret\n", "sécret", "x" * 65_537):
            with self.subTest(size=len(value)), mock.patch.dict(
                os.environ, {"OPENROUTER_API_KEY": value}, clear=True,
            ):
                with self.assertRaises(stt.TranscriptionError) as failure:
                    stt.load_api_key()
                if value:
                    self.assertNotIn(value, str(failure.exception))

    def test_media_subprocess_environment_excludes_runtime_key(self) -> None:
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": KEY, "PATH": "/test"}, clear=True):
            with mock.patch.object(stt.subprocess, "run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = b"media metadata"
                self.assertEqual(stt.run_media_tool(["ffprobe"], timeout=5, operation="probe"), b"media metadata")
                self.assertEqual(run.call_args.kwargs["env"], {"PATH": "/test"})
                self.assertEqual(os.environ["OPENROUTER_API_KEY"], KEY)


if __name__ == "__main__":
    unittest.main()
