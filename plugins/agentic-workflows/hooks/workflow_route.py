#!/usr/bin/env python3
"""Route ordinary Codex repository changes to the installed SDLC skill."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills" / "standard-development-workflow" / "SKILL.md"


def event(payload: dict) -> dict | None:
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd or not isinstance(payload.get("prompt"), str):
        return None
    if not Path(cwd).is_dir() or not SKILL.is_file():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or result.stdout.strip() != "true":
        return None

    try:
        remotes = subprocess.run(
            ["git", "remote"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        remotes = None
    missing_remote = remotes is not None and remotes.returncode == 0 and not remotes.stdout.strip()

    context = (
        "This Codex task is in a Git repository. If the active user-authored objective "
        "calls for planning or making code, documentation, configuration, or artifact changes, "
        f"read and apply the installed Standard Development Workflow at {SKILL}. "
        "Consider the full active objective when the latest user message is a terse continuation. "
        "Use its ordinary approval and evidence gates. "
        "Before the final response, inspect tracked changes and the live PR handoff state. "
        "For ordinary tracked edits, finish checks, commit and push, then open or update a "
        "reviewable PR before the final response. Read back its URL, exact head, base, state, "
        "and checks; a pushed branch alone is incomplete. Preserve work and report a concrete "
        "blocker if PR handoff is impossible. Read-only, no-diff, and explicit local-only work "
        "does not need a PR. "
        "Do not activate $sdlc-loop autopilot or infer merge or deployment authority "
        "unless the user directly invoked it; then follow its verified control-plane gates."
    )
    if missing_remote:
        context += (
            " This checkout has no Git remote. If tracked changes are made and the user did "
            "not request local-only work, preserve the diff or commit and explicitly report "
            "PR handoff blocked by the missing remote before ending the turn."
        )
    if payload.get("permission_mode") == "plan":
        context += " Current mode is Plan: plan the work without mutating files or external state."
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = event(payload) if isinstance(payload, dict) else None
        if result:
            print(json.dumps(result))
    except (OSError, ValueError, json.JSONDecodeError):
        pass  # Routing guidance must never interrupt a user turn.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
