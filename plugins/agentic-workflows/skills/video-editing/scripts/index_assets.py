#!/usr/bin/env python3
"""Index explicit local media without modifying source assets or editorial labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value: {value}")


def index_asset(path: Path, ffprobe: str = "ffprobe") -> dict:
    source = path.resolve(strict=True)
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError(f"expected a non-empty local media file: {source}")
    before = source.stat()
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(source)],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"ffprobe could not inspect {source}: {type(error).__name__}") from error
    if result.returncode or result.stderr.strip():
        raise ValueError(f"ffprobe failed for {source}: {result.stderr.strip()}")
    try:
        metadata = json.loads(result.stdout, parse_constant=reject_constant)
    except (ValueError, TypeError) as error:
        raise ValueError(f"invalid ffprobe JSON for {source}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"invalid ffprobe object for {source}")
    streams = metadata.get("streams")
    container = metadata.get("format", {})
    if (not isinstance(streams, list) or not streams
            or not all(isinstance(stream, dict) for stream in streams)
            or not any(stream.get("codec_type") in {"video", "audio"} for stream in streams)
            or not isinstance(container, dict)):
        raise ValueError(f"missing media streams or invalid container for {source}")
    duration = container.get("duration")
    if duration is not None:
        try:
            duration = float(duration)
        except (TypeError, ValueError) as error:
            raise ValueError(f"invalid duration for {source}") from error
        if not math.isfinite(duration) or duration < 0:
            raise ValueError(f"invalid duration for {source}")
    after = source.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (
            after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError(f"source changed during indexing: {source}")
    return {
        "asset_id": "sha256:" + digest.hexdigest(),
        "path": str(source), "bytes": after.st_size,
        "container": container, "duration_seconds": duration,
        "streams": streams, "annotations": {},
    }


def build_index(paths: list[Path], ffprobe: str = "ffprobe") -> dict:
    if not paths:
        raise ValueError("select at least one local media file")
    resolved = sorted({path.resolve(strict=True) for path in paths}, key=str)
    return {"schema_version": 1, "assets": [index_asset(path, ffprobe) for path in resolved]}


def write_index(output: Path, record: dict, *, overwrite: bool = False) -> None:
    """Publish a completed file; exclusive create also protects against races."""
    content = json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent,
            prefix=".asset-index-", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        if overwrite:
            os.replace(temporary, output)
        else:
            # Linking publishes atomically without replacing an existing path.
            os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assets", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--overwrite", action="store_true")
    arguments = parser.parse_args()
    try:
        sources = {path.resolve(strict=True) for path in arguments.assets}
        output = arguments.output.resolve()
        if output in sources or (
            output.exists() and any(os.path.samefile(output, source) for source in sources)
        ):
            raise ValueError("output must not replace a source asset")
        if output.exists() and not arguments.overwrite:
            raise ValueError("output exists; select a new index or use --overwrite")
        record = build_index(arguments.assets, arguments.ffprobe)
        write_index(output, record, overwrite=arguments.overwrite)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Asset indexing failed: {error}\n")
    print(f"Indexed {len(record['assets'])} local assets: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
