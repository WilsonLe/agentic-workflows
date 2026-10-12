from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/video-editing/skills/video-editing/scripts/index_assets.py"
SPEC = importlib.util.spec_from_file_location("media_index", SCRIPT)
assert SPEC and SPEC.loader
media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(media)


class AssetIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "clip with spaces.mp4"
        self.source.write_bytes(b"synthetic source")
        self.metadata = {
            "format": {"duration": "2.500", "format_name": "mov,mp4"},
            "streams": [
                {"index": 0, "codec_type": "video", "width": 720, "height": 1280,
                 "avg_frame_rate": "30000/1001", "tags": {"rotate": "90"}},
                {"index": 1, "codec_type": "audio", "sample_rate": "48000", "channels": 2},
            ],
        }

    def probe(self, metadata=None, returncode=0, stderr=""):
        return mock.patch.object(media.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], returncode, json.dumps(self.metadata if metadata is None else metadata), stderr,
        ))

    def test_content_identity_streams_and_source_preservation(self):
        duplicate = self.root / "duplicate.mp4"
        duplicate.write_bytes(self.source.read_bytes())
        before = self.source.read_bytes()
        with self.probe() as run:
            record = media.build_index([duplicate, self.source, self.source])
        assets = record["assets"]
        self.assertEqual(len(assets), 2)
        self.assertEqual(assets[0]["asset_id"], assets[1]["asset_id"])
        self.assertEqual(assets[0]["asset_id"], "sha256:" + hashlib.sha256(before).hexdigest())
        self.assertEqual(assets[0]["duration_seconds"], 2.5)
        self.assertEqual(assets[0]["streams"], self.metadata["streams"])
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(run.call_args.args[0][-1], str(duplicate.resolve()))
        self.source.write_bytes(b"new take")
        with self.probe():
            changed = media.index_asset(self.source)
        self.assertNotEqual(changed["asset_id"], assets[0]["asset_id"])

    def test_still_and_audio_metadata_do_not_invent_durations_or_video(self):
        for stream in [{"codec_type": "video", "codec_name": "png"},
                       {"codec_type": "audio", "sample_rate": "48000"}]:
            with self.subTest(stream=stream), self.probe({"streams": [stream]}):
                asset = media.index_asset(self.source)
                self.assertIsNone(asset["duration_seconds"])
                self.assertEqual(asset["streams"], [stream])

    def test_failures_do_not_publish_partial_index(self):
        output = self.root / "index.json"
        output.write_text("existing editorial state")
        for metadata in [[], {}, {"streams": []}, {"streams": ["bad"]},
                         {"streams": [{"codec_type": "subtitle"}]},
                         {**self.metadata, "format": {"duration": "NaN"}},
                         {**self.metadata, "format": {"duration": -1}}]:
            with self.subTest(metadata=metadata), self.probe(metadata), self.assertRaises(ValueError):
                record = media.build_index([self.source])
                media.write_index(output, record, overwrite=True)
            self.assertEqual(output.read_text(), "existing editorial state")
        for code, stderr in [(1, "bad codec"), (0, "decode error")]:
            with self.probe(returncode=code, stderr=stderr), self.assertRaises(ValueError):
                media.index_asset(self.source)
        for error in [FileNotFoundError(), subprocess.TimeoutExpired("ffprobe", 60)]:
            with mock.patch.object(media.subprocess, "run", side_effect=error), self.assertRaises(ValueError):
                media.index_asset(self.source)
        with mock.patch.object(media.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, "not JSON", "",
        )), self.assertRaises(ValueError):
            media.index_asset(self.source)

    def test_empty_missing_and_changing_sources_fail(self):
        empty = self.root / "empty.wav"
        empty.touch()
        with self.probe() as run:
            with self.assertRaises(ValueError):
                media.index_asset(empty)
            with self.assertRaises(FileNotFoundError):
                media.index_asset(self.root / "missing.mp4")
            run.assert_not_called()

        def changing(*args, **kwargs):
            self.source.write_bytes(b"changed during probe")
            return subprocess.CompletedProcess([], 0, json.dumps(self.metadata), "")

        with mock.patch.object(media.subprocess, "run", side_effect=changing), self.assertRaisesRegex(
            ValueError, "source changed",
        ):
            media.index_asset(self.source)

    def test_completed_writes_preserve_existing_index_unless_requested(self):
        output = self.root / "index.json"
        media.write_index(output, {"schema_version": 1, "assets": []})
        before = output.read_bytes()
        with self.assertRaises(FileExistsError):
            media.write_index(output, {"replacement": True})
        self.assertEqual(output.read_bytes(), before)
        media.write_index(output, {"replacement": True}, overwrite=True)
        self.assertEqual(json.loads(output.read_text()), {"replacement": True})
        self.assertFalse(list(self.root.glob(".asset-index-*")))

    def test_cli_rejects_source_overwrite_and_existing_output_before_probe(self):
        alias = self.root / "alias.json"
        alias.hardlink_to(self.source)
        for output in (self.source, alias):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(self.source), "--output", str(output),
                 "--overwrite", "--ffprobe", "missing-binary"], capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source asset", result.stderr)
        self.assertEqual(self.source.read_bytes(), b"synthetic source")


if __name__ == "__main__":
    unittest.main()
