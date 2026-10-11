from __future__ import annotations

import copy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "plugins/agentic-workflows/skills/motion-design/scripts/verify_video.py"
SPEC = importlib.util.spec_from_file_location("motion_video", HELPER)
assert SPEC and SPEC.loader
motion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(motion)


class MotionVideoTests(unittest.TestCase):
    def setUp(self):
        self.expected = dict(width=1920, height=1080, fps=Fraction(60), frames=900,
                             require_audio=True)
        self.metadata = {"streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1920,
             "height": 1080, "avg_frame_rate": "60/1", "nb_read_frames": "900",
             "duration": "15.000000"},
            {"codec_type": "audio", "codec_name": "aac", "duration": "15.000000"},
        ]}

    def test_complete_deliverable_matches_independent_brief(self):
        self.assertEqual(motion.metadata_failures(self.metadata, **self.expected), [])

    def test_truncated_or_wrong_format_outputs_fail(self):
        for patch in [{"nb_read_frames": "899"}, {"duration": "14.983333"},
                      {"avg_frame_rate": "30/1"}, {"width": 960}]:
            with self.subTest(patch=patch):
                data = copy.deepcopy(self.metadata)
                data["streams"][0].update(patch)
                self.assertTrue(motion.metadata_failures(data, **self.expected))

    def test_missing_decoded_count_cannot_use_declared_count(self):
        del self.metadata["streams"][0]["nb_read_frames"]
        self.metadata["streams"][0]["nb_frames"] = "900"
        self.assertIn("decoded frame count is unavailable",
                      motion.metadata_failures(self.metadata, **self.expected))

    def test_missing_and_short_sound_are_rejected(self):
        self.metadata["streams"][1]["duration"] = "10"
        self.assertTrue(motion.metadata_failures(self.metadata, **self.expected))
        self.metadata["streams"].pop()
        self.assertIn("requested audio stream is missing",
                      motion.metadata_failures(self.metadata, **self.expected))
        self.expected["require_audio"] = False
        self.assertEqual(motion.metadata_failures(self.metadata, **self.expected), [])

    def test_rational_frame_rate_and_aac_padding(self):
        self.expected.update(fps=Fraction(30000, 1001), frames=450)
        self.metadata["streams"][0].update(avg_frame_rate="30000/1001",
                                           nb_read_frames="450", duration="15.015")
        self.metadata["streams"][1]["duration"] = "15.03"
        self.assertEqual(motion.metadata_failures(self.metadata, **self.expected), [])

    def test_invalid_time_values_and_missing_video_fail(self):
        for value in ["0/0", "N/A", "NaN", None]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.metadata)
                data["streams"][0].update(duration=value, avg_frame_rate=value)
                self.assertTrue(motion.metadata_failures(data, **self.expected))
        self.assertTrue(motion.metadata_failures({"streams": []}, **self.expected))

    def test_probe_errors_fail_and_success_does_not_claim_visual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "final.mp4"
            video.write_bytes(b"synthetic media fixture")
            completed = subprocess.CompletedProcess([], 0, json.dumps(self.metadata), "")
            with mock.patch.object(motion.subprocess, "run", return_value=completed) as run:
                result = motion.verify_video(video, **self.expected)
                self.assertTrue(result["technical_pass"])
                self.assertIn("not established", result["visual_review"])
                self.assertIn("-count_frames", run.call_args.args[0])
                self.assertEqual(len(result["sha256"]), 64)
            for result in [subprocess.CompletedProcess([], 1, "", "encoder failed"),
                           subprocess.CompletedProcess([], 0, json.dumps(self.metadata), "decode error")]:
                with mock.patch.object(motion.subprocess, "run", return_value=result):
                    with self.assertRaisesRegex(ValueError, "decoding error"):
                        motion.verify_video(video, **self.expected)

    def test_empty_file_and_invalid_expectations_rejected_before_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "empty.mp4"
            video.touch()
            with mock.patch.object(motion.subprocess, "run") as run:
                with self.assertRaisesRegex(ValueError, "non-empty"):
                    motion.verify_video(video, **self.expected)
                self.expected["frames"] = 0
                with self.assertRaisesRegex(ValueError, "positive"):
                    motion.verify_video(video, **self.expected)
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
