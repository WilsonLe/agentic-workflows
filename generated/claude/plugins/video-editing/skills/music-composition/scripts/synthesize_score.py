#!/usr/bin/env python3
"""Original deterministic synthesis starter: stdlib stereo PCM and shared cues."""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
import tempfile
import wave

DEFAULTS = {
    "duration": 15,
    "bpm": 128,
    "sample_rate": 48000,
    "seed": 2301,
    "beats_per_chord": 8,
    "chords": [[45, 48, 52], [48, 52, 55], [41, 45, 48], [43, 47, 50]],
    "percussion": True,
    "cues": {},
}


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    result = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )
    if not isinstance(result, dict):
        raise ValueError("input must be a JSON object")
    return result


def number(
    value: object, name: str, low: float, high: float, *, integer: bool = False
) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    if integer and not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{name} must be between {low} and {high}")
    return value


def validate_brief(brief: dict, timeline: dict | None = None) -> dict:
    if not isinstance(brief, dict) or set(brief) - set(DEFAULTS):
        raise ValueError("brief contains unknown fields or is not an object")
    config = {**DEFAULTS, **brief}
    if timeline is not None:
        if not isinstance(timeline, dict) or not {"duration", "cues"} <= set(timeline):
            raise ValueError("timeline requires duration and cues")
        for name in ("duration", "bpm", "cues"):
            if name in timeline:
                config[name] = timeline[name]
    number(config["duration"], "duration", 0, 120)
    if config["duration"] <= 0:
        raise ValueError("duration must be greater than zero")
    number(config["bpm"], "bpm", 30, 240)
    number(config["sample_rate"], "sample_rate", 8000, 48000, integer=True)
    if config["sample_rate"] not in (8000, 16000, 24000, 44100, 48000):
        raise ValueError("unsupported sample_rate")
    frames = round(config["duration"] * config["sample_rate"])
    if not 1 <= frames <= 5_760_000:
        raise ValueError("duration must produce 1 to 5760000 frames")
    number(config["seed"], "seed", 0, 2**32 - 1, integer=True)
    number(config["beats_per_chord"], "beats_per_chord", 1, 32, integer=True)
    chords = config["chords"]
    if not isinstance(chords, list) or not 1 <= len(chords) <= 16:
        raise ValueError("chords requires 1 to 16 chords")
    for chord in chords:
        if not isinstance(chord, list) or not 1 <= len(chord) <= 8:
            raise ValueError("each chord requires 1 to 8 notes")
        for note in chord:
            number(note, "MIDI note", 24, 84, integer=True)
    if not isinstance(config["percussion"], bool):
        raise ValueError("percussion must be boolean")
    cues = config["cues"]
    if not isinstance(cues, dict) or len(cues) > 256:
        raise ValueError("cues must be an object with at most 256 entries")
    for name, value in cues.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("cue names must be nonempty strings")
        number(value, f"cue {name}", 0, config["duration"])
    return config


def frequency(note: int) -> float:
    return 440 * 2 ** ((note - 69) / 12)


def synthesize(config: dict) -> array:
    config = validate_brief(config)
    rate = config["sample_rate"]
    count = round(config["duration"] * rate)
    left, right = array("f", [0]) * count, array("f", [0]) * count
    rng = random.Random(config["seed"])
    beat = 60 / config["bpm"]
    tau = math.tau

    def add(start, duration, oscillator, gain=1, pan=0):
        first, last = (
            max(0, math.ceil(start * rate)),
            min(count, math.ceil((start + duration) * rate)),
        )
        lg, rg = gain * math.sqrt((1 - pan) / 2), gain * math.sqrt((1 + pan) / 2)
        for i in range(first, last):
            value = oscillator(i / rate - start)
            left[i] += value * lg
            right[i] += value * rg

    def pluck(t, f):
        return (
            (math.sin(tau * f * t) + 0.24 * math.sin(tau * 2 * f * t))
            * min(1, t / 0.006)
            * math.exp(-8 * t)
        )

    for b in range(math.ceil(config["duration"] / beat)):
        start = b * beat
        chord = config["chords"][
            (b // config["beats_per_chord"]) % len(config["chords"])
        ]
        bass = frequency(chord[0] - 12)
        add(
            start,
            beat * 0.88,
            lambda t, f=bass: math.sin(tau * f * t)
            * min(1, t / 0.008)
            * math.exp(-7 * t),
            0.17,
        )
        # Harmonic bed follows the same progression as bass and motif.
        for note in chord:
            f = frequency(note)
            add(
                start,
                beat,
                lambda t, f=f: math.sin(tau * f * t)
                * math.sin(math.pi * t / beat) ** 2,
                0.025,
            )
        for half in range(2):
            f = frequency(chord[(b * 2 + half) % len(chord)] + 12)
            add(
                start + half * beat / 2,
                0.55,
                lambda t, f=f: pluck(t, f),
                0.06,
                -0.3 if half == 0 else 0.3,
            )
        if config["percussion"]:
            add(
                start,
                0.27,
                lambda t: math.sin(
                    tau * (48 * t + 42 * 0.032 * (1 - math.exp(-t / 0.032)))
                )
                * (1 - math.exp(-900 * t))
                * math.exp(-17 * t),
                0.35,
            )
            if b % 4 in (1, 3):
                noise = [rng.uniform(-1, 1) for _ in range(math.ceil(0.15 * rate) + 1)]
                add(
                    start,
                    0.15,
                    lambda t, noise=noise: noise[int(t * rate)] * math.exp(-35 * t),
                    0.085,
                )
            for half in range(2):
                noise = [rng.uniform(-1, 1) for _ in range(math.ceil(0.05 * rate) + 2)]
                add(
                    start + half * beat / 2,
                    0.05,
                    lambda t, noise=noise: (
                        noise[int(t * rate) + 1] - noise[int(t * rate)]
                    )
                    * math.exp(-70 * t),
                    0.028,
                    -0.45 if half == 0 else 0.45,
                )
    for _, cue in sorted(config["cues"].items(), key=lambda item: (item[1], item[0])):
        noise = [rng.uniform(-1, 1) for _ in range(math.ceil(0.35 * rate) + 2)]
        add(
            cue - 0.28,
            0.35,
            lambda t, noise=noise: noise[int(t * rate)]
            * math.sin(math.pi * t / 0.35) ** 2,
            0.08,
        )
        add(
            cue,
            0.18,
            lambda t: math.sin(tau * 880 * t)
            * (1 - math.exp(-1500 * t))
            * math.exp(-30 * t),
            0.055,
            0.2,
        )
    peak = max(max(map(abs, left)), max(map(abs, right)))
    scale = 0.85 / peak if peak else 0
    pcm = array("h")
    # Zero endpoints and proportionate fades also handle extremely short briefs.
    for i, (left_sample, right_sample) in enumerate(zip(left, right)):
        fade = min(
            1,
            i / max(1, min(0.012 * rate, count / 2)),
            (count - 1 - i) / max(1, min(0.32 * rate, count / 2)),
        )
        pcm.extend(
            (
                round(left_sample * scale * fade * 32767),
                round(right_sample * scale * fade * 32767),
            )
        )
    if sys.byteorder != "little":
        pcm.byteswap()
    return pcm


def write_wav(path: Path, pcm: array, rate: int, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise ValueError(
            f"output exists: {path}; use --overwrite for an intended replacement"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix=".score-", suffix=".wav", dir=path.parent
    )
    os.close(handle)
    try:
        with wave.open(temporary, "wb") as audio:
            audio.setnchannels(2)
            audio.setsampwidth(2)
            audio.setframerate(rate)
            audio.writeframes(pcm.tobytes())
        if overwrite:
            os.replace(temporary, path)
        else:
            # Atomic no-clobber publication, even if another writer appeared meanwhile.
            os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def inspect_wav(path: Path) -> dict:
    with wave.open(str(path), "rb") as audio:
        frames, rate = audio.getnframes(), audio.getframerate()
        channels, width = audio.getnchannels(), audio.getsampwidth()
        if channels != 2 or width != 2:
            raise ValueError("expected 16-bit stereo PCM WAV")
        raw = audio.readframes(frames)
    if len(raw) != frames * channels * width or not frames:
        raise ValueError("empty or truncated WAV")
    samples = array("h")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    peak = max(map(abs, samples)) / 32768
    rms = math.sqrt(sum((value / 32768) ** 2 for value in samples) / len(samples))
    return {
        "path": str(path.resolve()),
        "frames": frames,
        "sample_rate": rate,
        "channels": channels,
        "duration": frames / rate,
        "peak": peak,
        "rms": rms,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brief", type=Path, required=True)
    parser.add_argument("--timeline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        config = validate_brief(
            read_json(args.brief), read_json(args.timeline) if args.timeline else None
        )
        if args.output.resolve() in {
            path.resolve() for path in (args.brief, args.timeline) if path is not None
        }:
            raise ValueError("output must not replace a source brief or timeline")
        if args.output.exists() and not args.overwrite:
            raise ValueError(
                "output exists; use --overwrite for an intended replacement"
            )
        write_wav(
            args.output,
            synthesize(config),
            config["sample_rate"],
            overwrite=args.overwrite,
        )
        report = inspect_wav(args.output)
        report.update(
            {
                "bpm": config["bpm"],
                "seed": config["seed"],
                "cues": config["cues"],
                "listening": "unobserved",
            }
        )
        print(json.dumps(report, indent=2))
    except (ValueError, OSError, wave.Error) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
