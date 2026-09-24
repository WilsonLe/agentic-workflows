#!/usr/bin/env python3
"""Install one shared Claude package into an isolated temporary configuration."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="agentic-claude-smoke-") as config:
        environment = dict(os.environ, CLAUDE_CONFIG_DIR=config)
        commands = (
            ["claude", "plugin", "marketplace", "add", "./"],
            ["claude", "plugin", "install", "guided-writing@agentic-workflows"],
            ["claude", "plugin", "list"],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            if command[-1] == "list" and "guided-writing@agentic-workflows" not in result.stdout:
                raise RuntimeError("installed shared skill was not discovered")
    print("Claude package install and discovery passed.")


if __name__ == "__main__":
    main()
