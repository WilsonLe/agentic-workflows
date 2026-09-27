#!/usr/bin/env python3
"""Keep a minimal, secret-free cursor for user-directed session reflection."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile


def load(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "sessions": {}, "candidates": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("sessions"), dict) or not isinstance(data.get("candidates"), dict):
        raise ValueError("unsupported reflection state")
    return data


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".reflection-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, sort_keys=True, separators=(",", ":"))
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    state_root = Path(os.environ.get("PLUGIN_DATA", Path.home() / ".local" / "state" / "agentic-workflows"))
    parser.add_argument("--file", type=Path, default=state_root / "reflection-state.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show")
    session = sub.add_parser("session")
    session.add_argument("session_id")
    session.add_argument("coverage", choices=("complete", "partial", "unavailable"))
    candidate = sub.add_parser("candidate")
    candidate.add_argument("candidate_key")
    candidate.add_argument("issue_url")
    args = parser.parse_args()
    data = load(args.file)
    if args.command == "session":
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", args.session_id):
            parser.error("session_id must be an opaque identifier")
        data["sessions"][args.session_id] = {
            "coverage": args.coverage,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        save(args.file, data)
    elif args.command == "candidate":
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", args.candidate_key):
            parser.error("candidate_key must be a short opaque slug")
        if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[0-9]+", args.issue_url):
            parser.error("issue_url must be a GitHub issue URL")
        data["candidates"][args.candidate_key] = args.issue_url
        save(args.file, data)
    print(json.dumps(data, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
