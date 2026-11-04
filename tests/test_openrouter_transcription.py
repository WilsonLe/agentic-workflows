from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error
import wave


SCRIPTS = Path(__file__).resolve().parents[1] / "plugins" / "agentic-workflows" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import openrouter_transcribe as stt  # noqa: E402


SYNTHETIC_KEY = "test-key-openrouter-no-live-access"
PAYLOAD = {
    "language": "en",
    "words": [
        {"word": " Hello", "start": 0.1, "end": 0.4, "confidence": 0.9},
        {"word": "again.", "start": 0.45, "end": 2.02},
    ],
    "usage": {"cost": 0.0002},
}


class OpenRouterTranscriptionTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "selected.mp4"
        self.source.write_bytes(b"synthetic source identity")
        self.output = self.root / "result"
        self.key = self.enterContext(
            mock.patch.object(stt.credentials, "load_openrouter_key", return_value=SYNTHETIC_KEY)
        )
        self.probe = self.enterContext(mock.patch.object(stt, "probe_source", return_value=(1, 2.0)))
        self.extract = self.enterContext(
            mock.patch.object(stt, "prepare_audio", return_value=(b"synthetic WAV payload", 2.0))
        )

    def run_transcription(self, language: str = "auto") -> dict:
        return stt.transcribe(self.root, self.source, self.output, language)

    def mock_request(self, payload: dict):
        return mock.patch.object(stt, "request_transcription", return_value=json.dumps(payload).encode())

    def test_one_fixed_request_and_source_bound_private_artifacts(self) -> None:
        raw = json.dumps(PAYLOAD).encode()
        opener = mock.Mock()

        def open_once(request, *, timeout):
            self.assertEqual(request.full_url, stt.ENDPOINT)
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), f"Bearer {SYNTHETIC_KEY}")
            self.assertEqual(timeout, 75)
            body = json.loads(request.data)
            self.assertEqual(body["model"], stt.MODEL)
            self.assertEqual(body["language"], "en")
            self.assertEqual(body["provider"], {"data_collection": "deny"})
            self.assertEqual(body["temperature"], 0)
            self.assertEqual(body["response_format"], "verbose_json")
            self.assertEqual(body["timestamp_granularities"], ["word"])
            self.assertEqual(body["input_audio"]["format"], "wav")
            self.assertEqual(base64.b64decode(body["input_audio"]["data"]), b"synthetic WAV payload")
            self.assertNotIn(str(self.source), request.data.decode())
            self.assertTrue((self.output / stt.ATTEMPT_NAME).is_file(), "reserve before external request")
            response = mock.MagicMock()
            response.__enter__.return_value.read.return_value = raw
            return response

        opener.open.side_effect = open_once
        with mock.patch.object(stt.urllib.request, "build_opener", return_value=opener) as build:
            summary = self.run_transcription("en")
        self.assertTrue(any(isinstance(h, stt.NoRedirect) for h in build.call_args.args))
        opener.open.assert_called_once()
        self.key.assert_called_once_with(self.root)
        source_digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.assertEqual(summary["asset_id"], f"sha256:{source_digest}")
        self.assertEqual(summary["word_count"], 2)
        self.assertEqual(summary["usage_cost_usd"], PAYLOAD["usage"]["cost"])
        self.assertNotIn("Hello", json.dumps(summary))
        transcript = json.loads((self.output / stt.TRANSCRIPT_NAME).read_text())
        self.assertIs(stt.validate_transcript(transcript), transcript)
        self.assertEqual(transcript["source"], {"path": str(self.source), "stream_index": 1, "duration_seconds": 2})
        self.assertEqual(transcript["language"], "en")
        self.assertEqual(transcript["requested_language"], "en")
        self.assertEqual(transcript["provider_response_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(transcript["analysis_to_source"]["audio_sha256"], hashlib.sha256(b"synthetic WAV payload").hexdigest())
        words = transcript["segments"][0]["words"]
        self.assertEqual([word["text"] for word in words], ["Hello", "again."])
        self.assertEqual(words[-1]["end_seconds"], 2.0, "clamp only tolerated rounding to the observed clock")
        self.assertIsNone(words[-1]["confidence"])
        self.assertEqual((self.output / stt.RESPONSE_NAME).read_bytes(), raw)
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        for artifact in self.output.iterdir():
            self.assertEqual(stat.S_IMODE(artifact.stat().st_mode), 0o600)
            self.assertNotIn(SYNTHETIC_KEY.encode(), artifact.read_bytes())

    def test_missing_or_invalid_timing_keeps_raw_response_and_blocks_resubmission(self) -> None:
        cases = (
            {"text": "unmeasured speech"},
            {"words": [{"word": "invalid", "start": True, "end": 1.0}]},
            {"words": [{"word": "invalid", "start": 0.8, "end": 2.08}]},
            {"words": [{"word": "later", "start": 0.9, "end": 1.0},
                       {"word": "earlier", "start": 0.8, "end": 0.9}]},
            {"words": [{"word": "invalid", "start": 2.0, "end": 2.02}]},
        )
        for index, payload in enumerate(cases):
            with self.subTest(payload=payload):
                self.output = self.root / f"malformed-{index}"
                with self.mock_request(payload) as request:
                    with self.assertRaises(stt.TranscriptionError):
                        self.run_transcription()
                    self.assertEqual(json.loads((self.output / stt.RESPONSE_NAME).read_text()), payload)
                    self.assertFalse((self.output / stt.TRANSCRIPT_NAME).exists())
                    with self.assertRaisesRegex(stt.TranscriptionError, "already exists"):
                        self.run_transcription()
                    request.assert_called_once()

    def test_timeout_or_redirect_never_resubmits_and_sanitizes_diagnostics(self) -> None:
        errors = (
            urllib.error.URLError(SYNTHETIC_KEY),
            urllib.error.HTTPError(stt.ENDPOINT, 307, SYNTHETIC_KEY, None, None),
        )
        for index, problem in enumerate(errors):
            with self.subTest(error=type(problem).__name__):
                self.output = self.root / f"failed-{index}"
                opener = mock.Mock()
                opener.open.side_effect = problem
                with mock.patch.object(stt.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaises(stt.TranscriptionError) as outcome:
                        self.run_transcription()
                    self.assertNotIn(SYNTHETIC_KEY, str(outcome.exception))
                    self.assertIn("not retried", str(outcome.exception))
                    self.assertTrue((self.output / stt.ATTEMPT_NAME).is_file())
                    self.assertFalse((self.output / stt.RESPONSE_NAME).exists())
                    with self.assertRaisesRegex(stt.TranscriptionError, "already exists"):
                        self.run_transcription()
                    opener.open.assert_called_once()

    def test_raw_response_cannot_store_an_echoed_key_even_if_json_escaped(self) -> None:
        escaped = SYNTHETIC_KEY.replace("t", "\\u0074")
        raw = ('{"text":"' + escaped + '"}').encode()
        self.assertNotIn(SYNTHETIC_KEY.encode(), raw)
        with mock.patch.object(stt, "request_transcription", return_value=raw):
            with self.assertRaisesRegex(stt.TranscriptionError, "unsafe content"):
                self.run_transcription()
        self.assertFalse((self.output / stt.RESPONSE_NAME).exists())
        self.assertFalse((self.output / stt.TRANSCRIPT_NAME).exists())

    def test_changed_source_never_publishes_transcript_for_old_identity(self) -> None:
        def respond(*_args):
            self.source.write_bytes(b"new source bytes")
            return json.dumps(PAYLOAD).encode()

        with mock.patch.object(stt, "request_transcription", side_effect=respond) as request:
            with self.assertRaisesRegex(stt.TranscriptionError, "source changed during transcription"):
                self.run_transcription()
            request.assert_called_once()
        self.assertTrue((self.output / stt.RESPONSE_NAME).is_file())
        self.assertFalse((self.output / stt.TRANSCRIPT_NAME).exists())

    def test_unavailable_observed_language_is_not_replaced_by_requested_language(self) -> None:
        payload = copy.deepcopy(PAYLOAD)
        del payload["language"]
        with self.mock_request(payload):
            self.run_transcription("en")
        transcript = json.loads((self.output / stt.TRANSCRIPT_NAME).read_text())
        self.assertIsNone(transcript["language"])
        self.assertEqual(transcript["requested_language"], "en")

    def test_offline_recovery_records_one_reviewed_final_endpoint_without_post_or_key_read(self) -> None:
        payload = copy.deepcopy(PAYLOAD)
        payload["language"] = "English"
        payload["words"][-1]["end"] = 2.34
        with self.mock_request(payload):
            with self.assertRaisesRegex(stt.TranscriptionError, "outside the selected audio"):
                self.run_transcription("en")
        self.key.reset_mock()
        attempt_before = (self.output / stt.ATTEMPT_NAME).read_bytes()
        raw_before = (self.output / stt.RESPONSE_NAME).read_bytes()
        with mock.patch.object(stt, "request_transcription") as request:
            with self.assertRaisesRegex(stt.TranscriptionError, "does not match"):
                stt.recover_final_word_end(self.source, self.output, "auto", 1.95)
            with self.assertRaisesRegex(stt.TranscriptionError, "inside both measured clocks"):
                stt.recover_final_word_end(self.source, self.output, "en", 2.01)
            self.extract.return_value = (b"different WAV bytes", 2.0)
            with self.assertRaisesRegex(stt.TranscriptionError, "does not match"):
                stt.recover_final_word_end(self.source, self.output, "en", 1.95)
            self.extract.return_value = (b"synthetic WAV payload", 2.0)
            summary = stt.recover_final_word_end(self.source, self.output, "en", 1.95)
            request.assert_not_called()
        self.key.assert_not_called()
        self.assertEqual(summary["language"], "en")
        transcript = json.loads((self.output / stt.TRANSCRIPT_NAME).read_text())
        self.assertEqual(transcript["segments"][0]["words"][-1]["end_seconds"], 1.95)
        self.assertEqual(transcript["timing_corrections"], [{
            "kind": "reviewed_final_word_end", "word_index": 1,
            "original_end_seconds": 2.34, "corrected_end_seconds": 1.95,
        }])
        self.assertEqual((self.output / stt.ATTEMPT_NAME).read_bytes(), attempt_before)
        self.assertEqual((self.output / stt.RESPONSE_NAME).read_bytes(), raw_before)

    def test_invalid_source_metadata_never_reads_key_or_submits(self) -> None:
        self.probe.side_effect = stt.TranscriptionError("the source container and audio stream must both start at zero")
        with mock.patch.object(stt, "request_transcription") as request:
            with self.assertRaisesRegex(stt.TranscriptionError, "must both start at zero"):
                self.run_transcription()
        self.key.assert_not_called()
        self.extract.assert_not_called()
        request.assert_not_called()
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "local FFmpeg and ffprobe required")
    def test_actual_local_wav_analysis_preserves_exact_sample_clock(self) -> None:
        # Use the real media functions for this case, without credentials or network.
        path = self.root / "actual.wav"
        with wave.open(str(path), "wb") as handle:
            handle.setparams((1, 2, stt.SAMPLE_RATE, 0, "NONE", "not compressed"))
            handle.writeframes(b"\0\0" * 8_000)
        stream, duration = REAL_PROBE(path)
        data, analysis_duration = REAL_PREPARE(path, stream)
        self.assertEqual((stream, duration, analysis_duration), (0, 0.5, 0.5))
        self.assertTrue(data.startswith(b"RIFF"))


REAL_PROBE = stt.probe_source
REAL_PREPARE = stt.prepare_audio


if __name__ == "__main__":
    unittest.main()
