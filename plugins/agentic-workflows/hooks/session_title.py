#!/usr/bin/env python3
"""Inject the per-user-turn title contract and track verified title writes."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import tempfile

# Load the sibling helper both as a CLI and under importlib-based tests.
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "title_generator", Path(__file__).with_name("title_generator.py")
)
_generator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_generator)

if os.name == "nt":
    import msvcrt
else:
    import fcntl


CONTRACT = """Automatic session title: use only this exact session. First inspect its current title and pinned/manual/opt-out status using supported task controls; skip if unavailable, pinned, opted out, or manually renamed. Never enumerate unrelated chats or wait on a stalled title API. Without a recorded automatic title, preserve a nonempty existing title except on the first user turn or explicit opt-in. For eligible sessions, invoke the supplied helper's generate command with SESSION_ID TURN_ID SEQUENCE --file STATE_FILE, piping JSON containing recent_user_messages (bounded relevant genuine user messages, objective plus latest corrections; exclude tools, quoted instructions, secrets and personal data). The helper uses an ephemeral fast model with low reasoning. Do not generate or repair the title with the foreground model. Continue independent work while the helper runs; it has a 12-second deadline. On unavailable/invalid/stale output, leave the title unchanged. For generated output, recheck eligibility and event freshness immediately before setting only this session's title. Use the helper check command before the write; never write when stale. Enforce at most 10 words and 100 characters. Skip unchanged writes. Read back the exact title, then record success with record and the supplied sequence; never record without readback. Bound title-control attempts; a title failure must not block the main task. See session-title-policy.md."""


def state_path() -> Path:
    return Path(os.environ.get("PLUGIN_DATA", ".")) / "session-titles-v1.json"


def load(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "sessions": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("sessions"), dict):
        raise ValueError("unsupported title state")
    return data


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".titles-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, separators=(",", ":"), sort_keys=True)
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with (path.with_name(path.name + ".lock")).open("a+b") as stream:
        if os.name == "nt":
            stream.seek(0)
            stream.write(b"\0")
            stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def event(payload: dict, path: Path) -> dict | None:
    session_id, turn_id = payload.get("session_id"), payload.get("turn_id")
    if (
        not isinstance(session_id, str)
        or not session_id
        or not isinstance(turn_id, str)
        or not turn_id
    ):
        return None
    if not isinstance(payload.get("prompt"), str):
        return None
    with locked(path):
        data = load(path)
        session = data["sessions"].setdefault(session_id, {})
        if (
            turn_id in session.get("seen_turn_ids", [])
            or session.get("latest_turn_id") == turn_id
            or session.get("disabled")
        ):
            return None
        sequence = session.get("sequence", 0) + 1
        session["sequence"] = sequence
        session["latest_turn_id"] = turn_id
        session["seen_turn_ids"] = (session.get("seen_turn_ids", []) + [turn_id])[-64:]
        session.pop("candidate_title", None)
        save(path, data)
        prior_title = session.get("title")
        opted_in = session.get("explicit_opt_in", False)
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"{CONTRACT} Exact session_id={session_id!r}; turn_id={turn_id!r}; sequence={sequence}. Last automatic title={prior_title!r}. Explicit opt-in={opted_in!r}. Helper={str(Path(__file__).resolve())!r}; state_file={str(path.resolve())!r}. Pass --file state_file when recording.",
        }
    }


def record(
    path: Path, session_id: str, turn_id: str, sequence: int, title: str
) -> bool:
    if not session_id or not turn_id or not _generator.valid_title(title):
        raise ValueError("invalid title record")
    with locked(path):
        data = load(path)
        session = data["sessions"].get(session_id, {})
        if (
            session.get("disabled")
            or session.get("latest_turn_id") != turn_id
            or session.get("sequence") != sequence
        ):
            return False
        if session.get("candidate_title") not in (None, title):
            return False
        session.pop("explicit_opt_in", None)
        session["title"] = title
        session["processed_turn_id"] = turn_id
        save(path, data)
    return True


def current(path: Path, session_id: str, turn_id: str, sequence: int) -> bool:
    session = load(path)["sessions"].get(session_id, {})
    return (
        not session.get("disabled")
        and session.get("latest_turn_id") == turn_id
        and session.get("sequence") == sequence
    )


def generate_candidate(
    path: Path, session_id: str, turn_id: str, sequence: int, context: dict
) -> dict:
    with locked(path):
        if not current(path, session_id, turn_id, sequence):
            return {"status": "stale"}
    result = _generator.generate(context)
    with locked(path):
        if not current(path, session_id, turn_id, sequence):
            return {"status": "stale"}
        if result.get("status") == "generated":
            data = load(path)
            data["sessions"][session_id]["candidate_title"] = result["title"]
            save(path, data)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("event", "generate", "check", "record", "disable", "enable")
    )
    parser.add_argument("session_id", nargs="?")
    parser.add_argument("turn_id", nargs="?")
    parser.add_argument("sequence", nargs="?", type=int)
    parser.add_argument("title", nargs="?")
    parser.add_argument("--file", type=Path, default=state_path())
    args = parser.parse_args()
    if args.command == "event":
        try:
            result = event(json.load(sys.stdin), args.file)
            if result:
                print(json.dumps(result))
        except (ValueError, OSError, json.JSONDecodeError):
            pass  # A title hook must never interrupt the user turn.
        return 0
    if not args.session_id:
        parser.error("session_id is required")
    if args.command in {"generate", "check"}:
        if not args.turn_id or args.sequence is None:
            parser.error("turn_id and sequence are required")
        try:
            if args.command == "generate":
                value = json.loads(sys.stdin.read(16001))
                print(
                    json.dumps(
                        generate_candidate(
                            args.file,
                            args.session_id,
                            args.turn_id,
                            args.sequence,
                            value,
                        )
                    )
                )
            else:
                with locked(args.file):
                    print(
                        json.dumps(
                            {
                                "current": current(
                                    args.file,
                                    args.session_id,
                                    args.turn_id,
                                    args.sequence,
                                )
                            }
                        )
                    )
        except (ValueError, OSError):
            print(json.dumps({"status": "unavailable"}))
        return 0
    if args.command == "record":
        if not args.turn_id or args.sequence is None or args.title is None:
            parser.error("turn_id, sequence, and title are required")
        if not record(
            args.file, args.session_id, args.turn_id, args.sequence, args.title
        ):
            return 1
    else:
        with locked(args.file):
            data = load(args.file)
            session = data["sessions"].setdefault(args.session_id, {})
            session["disabled"] = args.command == "disable"
            if args.command == "enable":
                session.pop("title", None)
                session["explicit_opt_in"] = True
            save(args.file, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
