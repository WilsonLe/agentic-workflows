from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins/agentic-workflows/skills/music-composition/scripts/synthesize_score.py"
)
SPEC = importlib.util.spec_from_file_location("synthesize_score", SCRIPT)
assert SPEC and SPEC.loader
score = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score)


class MusicCompositionTests(unittest.TestCase):
    def brief(self, **values):
        return score.validate_brief({"duration": 0.8, "sample_rate": 8000, **values})

    def test_stereo_wav_is_reproducible_decodable_and_has_headroom(self):
        config = self.brief(cues={"reveal": 0.4})
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.wav", Path(directory) / "b.wav"
            for path in (first, second):
                score.write_wav(path, score.synthesize(config), config["sample_rate"])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            report = score.inspect_wav(first)
            self.assertEqual(report["frames"], 6400)
            self.assertEqual(report["channels"], 2)
            self.assertEqual(report["duration"], 0.8)
            self.assertGreater(report["rms"], 0.01)
            self.assertLessEqual(report["peak"], 0.851)
            with wave.open(str(first), "rb") as audio:
                self.assertEqual(audio.getsampwidth(), 2)
                raw = audio.readframes(6400)
                self.assertEqual(raw[:4], b"\0" * 4)
                self.assertEqual(raw[-4:], b"\0" * 4)
            pcm = score.synthesize(config)
            self.assertNotEqual(pcm[::2], pcm[1::2])

    def test_seed_harmony_percussion_and_cues_change_audio(self):
        baseline = score.synthesize(self.brief())
        for change in (
            {"seed": 11},
            {"percussion": False},
            {"chords": [[50, 53, 57]]},
            {"cues": {"accent": 0.5}},
        ):
            with self.subTest(change=change):
                self.assertNotEqual(score.synthesize(self.brief(**change)), baseline)

    def test_shared_timeline_overrides_independent_timing(self):
        config = score.validate_brief(
            {"duration": 15, "bpm": 128, "cues": {"wrong": 10}},
            {"duration": 0.7, "bpm": 90, "cues": {"actual": 0.2}, "fps": 60},
        )
        self.assertEqual(
            (config["duration"], config["bpm"], config["cues"]),
            (0.7, 90, {"actual": 0.2}),
        )
        self.assertEqual(len(score.synthesize({**config, "sample_rate": 8000})), 11200)

    def test_boundary_cues_short_files_and_rounding(self):
        for duration in (0.000125, 0.003, 0.10006):
            with self.subTest(duration=duration):
                config = self.brief(
                    duration=duration, cues={"start": 0, "end": duration}
                )
                pcm = score.synthesize(config)
                self.assertEqual(len(pcm), round(duration * 8000) * 2)
                self.assertEqual(pcm[:2].tolist(), [0, 0])
                self.assertEqual(pcm[-2:].tolist(), [0, 0])

    def test_invalid_inputs_fail_before_render(self):
        invalid = [
            {"duration": 0},
            {"duration": 121},
            {"duration": float("nan")},
            {"duration": float("inf")},
            {"duration": 0.000001},
            {"sample_rate": 12000},
            {"sample_rate": True},
            {"seed": -1},
            {"seed": 10**400},
            {"seed": 1.2},
            {"bpm": 300},
            {"bpm": True},
            {"beats_per_chord": 0},
            {"chords": []},
            {"chords": [[100]]},
            {"chords": [[True]]},
            {"chords": ["wrong"]},
            {"percussion": 1},
            {"cues": []},
            {"cues": {"late": 1}},
            {"cues": {"": 0}},
            {"cues": {"bad": float("nan")}},
            {"unknown": 1},
            {"cues": {str(i): 0 for i in range(257)}},
        ]
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.brief(**change)
        with self.assertRaises(ValueError):
            score.validate_brief({}, {"duration": 1})

    def test_cli_duplicate_keys_and_source_overwrite_preserve_files(self):
        with tempfile.TemporaryDirectory() as directory:
            brief = Path(directory) / "brief.json"
            output = Path(directory) / "nested/score.wav"
            brief.write_text('{"duration":1,"duration":2}')
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--brief",
                    str(brief),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate JSON key", result.stderr)
            self.assertFalse(output.parent.exists())
            brief.write_text(json.dumps({"duration": 0.1, "sample_rate": 8000}))
            before = brief.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--brief",
                    str(brief),
                    "--output",
                    str(brief),
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(brief.read_bytes(), before)

    def test_existing_output_is_preserved_without_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.wav"
            path.write_bytes(b"keep")
            with self.assertRaises(ValueError):
                score.write_wav(path, score.synthesize(self.brief()), 8000)
            self.assertEqual(path.read_bytes(), b"keep")
            score.write_wav(path, score.synthesize(self.brief()), 8000, overwrite=True)
            self.assertEqual(score.inspect_wav(path)["frames"], 6400)
            self.assertEqual(list(Path(directory).glob(".score-*")), [])


if __name__ == "__main__":
    unittest.main()
