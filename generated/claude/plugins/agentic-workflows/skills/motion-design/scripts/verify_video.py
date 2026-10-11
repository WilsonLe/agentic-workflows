#!/usr/bin/env python3
"""Check a finished video's decoded properties against the requested deliverable."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def metadata_failures(
    metadata: dict,
    *,
    width: int,
    height: int,
    fps: Fraction,
    frames: int,
    require_audio: bool,
) -> list[str]:
    failures = []
    streams = metadata.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if len(videos) != 1:
        return ["expected exactly one video stream"]
    video = videos[0]
    if (video.get("width"), video.get("height")) != (width, height):
        failures.append("video dimensions differ from the brief")
    try:
        if Fraction(video["avg_frame_rate"]) != fps:
            failures.append("average frame rate differs from the brief")
    except (KeyError, ValueError, ZeroDivisionError, TypeError):
        failures.append("video frame rate is unavailable")
    try:
        if int(video["nb_read_frames"]) != frames:
            failures.append("decoded frame count differs from the brief")
    except (KeyError, ValueError, TypeError):
        failures.append("decoded frame count is unavailable")
    expected_duration = frames / fps
    try:
        duration = Fraction(video["duration"])
        if abs(duration - expected_duration) > Fraction(1, 1000):
            failures.append("video duration differs from the brief")
    except (KeyError, ValueError, ZeroDivisionError, TypeError):
        failures.append("video duration is unavailable")
    if require_audio and not audios:
        failures.append("requested audio stream is missing")
    for audio in audios:
        try:
            if abs(Fraction(audio["duration"]) - expected_duration) > Fraction(1, 10):
                failures.append("audio duration differs from the video by more than 0.1s")
        except (KeyError, ValueError, ZeroDivisionError, TypeError):
            failures.append("audio duration is unavailable")
    return failures


def verify_video(
    path: Path,
    *,
    width: int,
    height: int,
    fps: Fraction,
    frames: int,
    require_audio: bool = False,
    ffprobe: str = "ffprobe",
    timeout: float = 300,
) -> dict:
    if min(width, height, frames) <= 0 or fps <= 0 or timeout <= 0:
        raise ValueError("dimensions, frame count, fps, and timeout must be positive")
    path = path.expanduser().resolve(strict=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("video must be a non-empty regular file")
    result = subprocess.run(
        [ffprobe, "-v", "error", "-count_frames", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=timeout, check=False,
    )
    if result.returncode != 0 or result.stderr.strip():
        raise ValueError("ffprobe failed or reported a media decoding error")
    metadata = json.loads(result.stdout)
    if not isinstance(metadata, dict) or not isinstance(metadata.get("streams"), list):
        raise ValueError("ffprobe did not return a stream inventory")
    if any(not isinstance(stream, dict) for stream in metadata["streams"]):
        raise ValueError("ffprobe returned an invalid stream inventory")
    failures = metadata_failures(
        metadata, width=width, height=height, fps=fps, frames=frames,
        require_audio=require_audio,
    )
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(chunk)
    return {
        "technical_pass": not failures,
        "failures": failures,
        "file": str(path),
        "sha256": sha.hexdigest(),
        "bytes": path.stat().st_size,
        "expected": {"width": width, "height": height, "fps": str(fps),
                     "frames": frames, "duration_seconds": float(frames / fps),
                     "require_audio": require_audio},
        "streams": [{k: s.get(k) for k in (
            "codec_type", "codec_name", "width", "height", "pix_fmt",
            "avg_frame_rate", "nb_read_frames", "duration", "channels", "sample_rate",
        ) if k in s} for s in metadata["streams"]],
        "visual_review": "not established by this technical check",
        "audio_listening": "not established by this technical check",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--fps", type=Fraction, required=True)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    try:
        result = verify_video(
            args.video, width=args.width, height=args.height, fps=args.fps,
            frames=args.frames, require_audio=args.require_audio,
            ffprobe=args.ffprobe, timeout=args.timeout,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        result = {"technical_pass": False, "failures": [str(error)]}
    print(json.dumps(result, indent=2))
    return 0 if result["technical_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
