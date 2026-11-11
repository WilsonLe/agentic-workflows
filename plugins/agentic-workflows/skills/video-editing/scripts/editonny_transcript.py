#!/usr/bin/env python3
"""Bridge a source-linked OpenRouter transcript to a confirmed Editonny 1.1.0 edit."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


EDITONNY_VERSION = "1.1.0"
ADAPTER = "agentic-workflows/editonny-openrouter"
SUITE_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def read_object(path: Path) -> dict:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path.name}")
    return value


def local_file(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular local file: {path.name}")
    return path


def local_directory(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"Expected a local directory: {path.name}")
    return path


def configure_engine(root: Path) -> None:
    root = root.expanduser().resolve(strict=True)
    marker = local_file(root.parent / "VERSION")
    if marker.read_text(encoding="utf-8").strip() != EDITONNY_VERSION:
        raise ValueError(f"This bridge requires a trusted Editonny {EDITONNY_VERSION} engine")
    helpers = local_directory(root / "helpers")
    for name in ("intake", "common", "project_contract", "workspace", "captions", "render_cut"):
        local_file(helpers / f"{name}.py")
    sys.path[:0] = [str(helpers), str(SUITE_SCRIPTS)]


def inspect_source(source: Path, requested: Path | None) -> dict:
    from intake import inspect_sources, propose_settings
    from openrouter_transcribe import probe_source

    source = local_file(source.expanduser()).resolve()
    overrides = read_object(local_file(requested.expanduser())) if requested is not None else {}
    # Check that the selected file is a supported self-contained media input
    # before native inspection invokes its general-purpose media probe.
    probe_source(source)
    result = inspect_sources([source], detect_language=False)
    try:
        result["proposal"] = propose_settings(result, overrides)
    except ValueError as exc:
        result["proposalBlocked"] = str(exc)
    return result


def project_paths(project: Path) -> tuple[Path, Path]:
    from workspace import managed_revision

    project = local_directory(project.expanduser()).resolve()
    revision = managed_revision(project)
    if project != revision / "project":
        raise ValueError("Select the project directory of a managed Editonny revision")
    local_file(project / "project.json")
    edit = local_directory(revision / "edit")
    local_file(edit / "source_manifest.json")
    local_file(edit / "state.json")
    local_directory(edit / "transcripts")
    return project, edit


def confirmed_source(edit: Path) -> tuple[dict, dict, Path]:
    from project_contract import managed_config
    from workspace import selected_sources

    config = managed_config(edit)
    if not config:
        raise ValueError("A confirmed managed Editonny revision is required")
    sources = selected_sources(read_object(edit / "source_manifest.json"), config)["sources"]
    if len(sources) != 1 or sources[0]["facts"].get("audio_tracks") != 1:
        raise ValueError("The hosted transcript bridge requires one confirmed source with one audio stream")
    source = local_file(Path(sources[0]["path"]))
    if source.stem.casefold() == "cut":
        raise ValueError("The source name conflicts with Editonny's reserved cut transcript")
    return config, sources[0], source


def confirmed_language(config: dict) -> str:
    return config["workflow"]["language"]["transcription"].lower().split("-", 1)[0]


def check_transcript_source(data: dict, config: dict, record: dict, source: Path) -> None:
    from openrouter_transcribe import probe_source

    identity = data["source"]
    if identity["path"] != str(source) or data["asset_id"] != f"sha256:{record['sha256']}":
        raise ValueError("The normalized transcript does not identify the selected source bytes and path")
    stream, duration = probe_source(source)
    if any(not math.isclose(identity["duration_seconds"], seconds, rel_tol=0.0, abs_tol=0.001)
           for seconds in (record["facts"]["duration"], duration)):
        raise ValueError("The normalized transcript duration differs from the selected source")
    if stream != identity["stream_index"]:
        raise ValueError("The normalized transcript audio stream differs from the selected source")
    language = confirmed_language(config)
    if data["requested_language"] != language or (
        language != "auto" and data["language"] not in (None, language)
    ):
        raise ValueError("The normalized transcript language differs from the confirmed settings")


def publish_json(path: Path, value: dict) -> None:
    payload = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".transcript-")
    staged = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(staged, path)
        except FileExistsError as exc:
            if (
                path.is_symlink() or not path.is_file()
                or (os.name != "nt" and path.stat().st_mode & 0o077)
                or path.read_bytes() != payload
            ):
                raise ValueError(f"Preserved conflicting transcript: {path.name}") from exc
    finally:
        staged.unlink(missing_ok=True)


def native_timing(item: dict) -> dict:
    return {"text": item["text"], "start": item["start_seconds"], "end": item["end_seconds"]}


def import_transcript(project: Path, normalized: Path) -> dict:
    from common import content_hash, file_signature
    from openrouter_transcribe import validate_transcript
    from project_contract import digest
    from workspace import revision_lock, verify_sources

    project, edit = project_paths(project)
    normalized = local_file(normalized.expanduser())
    normalized_hash = content_hash(normalized)
    data = validate_transcript(read_object(normalized))
    with revision_lock(project):
        config, record, source = confirmed_source(edit)
        check_transcript_source(data, config, record, source)
        segments = [native_timing(segment) for segment in data["segments"]]
        words = [native_timing(word) for segment in data["segments"] for word in segment["words"]]
        timing = {"words": words, "segments": segments}
        native = {
            "source": str(source), "stem": source.stem, "source_sig": file_signature(source),
            "source_sha256": record["sha256"], "duration": data["source"]["duration_seconds"],
            "language": data["language"], "requested_language": data["requested_language"],
            "engine": f"{data['runtime']}/{data['model']}",
            "provider_response_sha256": data["provider_response_sha256"], **timing,
            "provenance": {
                "adapter": ADAPTER, "editonny_version": EDITONNY_VERSION,
                "normalized_transcript_sha256": normalized_hash,
                "audio_sha256": data["analysis_to_source"]["audio_sha256"],
                "stream_index": data["source"]["stream_index"], "timing_sha256": digest(timing),
            },
        }
        verify_sources({"sources": [record]})
        if content_hash(normalized) != normalized_hash:
            raise ValueError("The normalized transcript changed during import")
        output = edit / "transcripts" / f"{source.stem}.json"
        publish_json(output, native)
        return {"transcript": str(output), "sha256": content_hash(output), "words": len(words)}


def imported_source(edit: Path, config: dict, record: dict, source: Path) -> tuple[dict, Path]:
    from common import file_signature
    from project_contract import digest

    path = local_file(edit / "transcripts" / f"{source.stem}.json")
    data = read_object(path)
    provenance = data.get("provenance")
    if not isinstance(provenance, dict) or provenance.get("adapter") != ADAPTER or (
        provenance.get("editonny_version") != EDITONNY_VERSION
    ):
        raise ValueError("The source transcript must come from this hosted transcript bridge")
    if (
        data.get("source") != str(source) or data.get("source_sha256") != record["sha256"]
        or data.get("source_sig") != file_signature(source)
        or data.get("requested_language") != confirmed_language(config)
    ):
        raise ValueError("The imported transcript no longer matches the confirmed source or language")
    for value in (data.get("provider_response_sha256"), provenance.get("normalized_transcript_sha256"),
                  provenance.get("audio_sha256")):
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            raise ValueError("The imported transcript is missing its hosted provenance")
    if not data.get("words") or digest({"words": data["words"], "segments": data["segments"]}) != provenance.get(
        "timing_sha256"
    ):
        raise ValueError("The imported transcript timing changed; use an unchanged import")
    return data, path


def measured_timeline(
    project: Path, edit: Path, source: Path, source_transcript: Path, contract_hash: str,
) -> tuple[dict, dict, str]:
    from common import content_hash
    from project_contract import digest
    from render_cut import edl_signature, resolve_source

    cut = local_file(edit / "cut.mp4")
    timeline_path = local_file(edit / "cut_timeline.json")
    edl = local_file(edit / "edl.json")
    report_path = local_file(local_directory(edit / "verify") / "cut_report.json")
    if report_path.stat().st_mtime_ns < source_transcript.stat().st_mtime_ns:
        raise ValueError("Run native cut verification after importing the source transcript")
    inputs = {
        "video": content_hash(cut), "edl": content_hash(edl),
        str(timeline_path): content_hash(timeline_path),
        str(project / "project.json"): content_hash(project / "project.json"),
    }
    report = read_object(report_path)
    # Native verify_cut includes the exact path spellings in this identity. Use the
    # paths from its report after resolving them to the current local revision.
    locations = {key: Path(report.get(key) or "") for key in ("video", "edl", "timeline")}
    if any(locations[key].resolve() != current for key, current in (
        ("video", cut), ("edl", edl), ("timeline", timeline_path),
    )):
        raise ValueError("Run native cut verification on the current cut and timeline")
    reported_inputs = {
        "video": inputs["video"], "edl": inputs["edl"],
        str(locations["edl"].parent / "cut_timeline.json"): inputs[str(timeline_path)],
        str(locations["edl"].parent.parent / "project/project.json"): inputs[str(project / "project.json")],
    }
    verification = digest(reported_inputs)
    if report.get("verificationIdentity") != verification or report.get("status") not in ("passed", "failed"):
        raise ValueError("Native cut verification is stale or missing; rerun verify_cut.py")
    if any(flag["code"] in {"DURATION", "PREVIEW", "SOURCE-MISSING", "STALE-TIMELINE"} for flag in report["flags"]):
        raise ValueError("Resolve the native cut verification's media or timeline findings before mapping")
    timeline = read_object(timeline_path)
    decisions = read_object(edl)
    if (
        timeline.get("video") != "cut.mp4" or timeline.get("preview") is not False
        or timeline.get("contractHash") != contract_hash or decisions.get("contractHash") != contract_hash
        or timeline.get("edl_sig") != edl_signature(decisions)
    ):
        raise ValueError("Use the full native cut and timeline for the currently confirmed settings and EDL")
    segments = timeline.get("segments")
    if not segments:
        raise ValueError("The measured cut timeline has no segments")
    for segment in segments:
        alias = segment["source"]
        if (
            Path(segment["source_path"]).resolve() != source
            or resolve_source(decisions["sources"][alias], edit).resolve() != source
        ):
            raise ValueError("The measured cut timeline uses a source outside the confirmed selection")
        # Native caption lookup uses filenames, while a native EDL can name the
        # same source with an alias. Change only the in-memory lookup key.
        segment["source"] = source.stem
    return timeline, inputs, verification


def map_cut(project: Path) -> dict:
    from captions import words_from_sources
    from common import content_hash, file_signature
    from project_contract import settings_hash
    from workspace import revision_lock, verify_sources

    project, edit = project_paths(project)
    with revision_lock(project):
        config, record, source = confirmed_source(edit)
        if config["workflow"]["video"]["timing"] != "cfr":
            raise ValueError("Hosted cut mapping requires a confirmed constant-frame-rate edit")
        contract_hash = settings_hash(config)
        source_transcript, source_path = imported_source(edit, config, record, source)
        source_transcript_hash = content_hash(source_path)
        timeline, inputs, verification = measured_timeline(project, edit, source, source_path, contract_hash)
        words, mode, warnings = words_from_sources(edit, timeline, None, "sources")
        duration = timeline["duration"]
        if warnings:
            raise ValueError("Native word mapping found uncertain cut boundaries; inspect the cut and EDL")
        if mode != "sources" or not words or any(not 0 <= w["start"] < w["end"] <= duration for w in words):
            raise ValueError("The measured cut has no complete in-bounds hosted words")
        cut = edit / "cut.mp4"
        native = {
            "source": str(cut), "source_sig": file_signature(cut), "source_sha256": inputs["video"],
            "duration": duration, "language": source_transcript["language"],
            "engine": source_transcript["engine"], "words": words, "segments": [],
            "provider_response_sha256": source_transcript["provider_response_sha256"],
            "provenance": {
                "adapter": ADAPTER, "editonny_version": EDITONNY_VERSION,
                "mode": "native-cut-timeline", "settings_sha256": contract_hash,
                "timeline_sha256": inputs[str(edit / "cut_timeline.json")], "edl_sha256": inputs["edl"],
                "source_transcript_sha256": source_transcript_hash, "verification_identity": verification,
            },
        }
        verify_sources({"sources": [record]})
        if any(content_hash(path) != expected for path, expected in (
            (cut, inputs["video"]), (edit / "edl.json", inputs["edl"]),
            (edit / "cut_timeline.json", inputs[str(edit / "cut_timeline.json")]),
            (project / "project.json", inputs[str(project / "project.json")]),
            (source_path, source_transcript_hash),
        )):
            raise ValueError("The measured cut or its transcript inputs changed during mapping")
        output = edit / "transcripts/cut.json"
        publish_json(output, native)
        return {"transcript": str(output), "sha256": content_hash(output), "words": len(words)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect")
    load = commands.add_parser("import")
    mapping = commands.add_parser("map-cut")
    for command in (inspect, load, mapping):
        command.add_argument("--engine-root", type=Path, required=True)
    inspect.add_argument("--source", type=Path, required=True)
    inspect.add_argument("--requested", type=Path)
    for command in (load, mapping):
        command.add_argument("--project", type=Path, required=True)
    load.add_argument("--transcript", type=Path, required=True)
    args = parser.parse_args()
    try:
        configure_engine(args.engine_root)
        if args.command == "inspect":
            result = inspect_source(args.source, args.requested)
        elif args.command == "import":
            result = import_transcript(args.project, args.transcript)
        else:
            result = map_cut(args.project)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, ImportError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Editonny transcript bridge: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
