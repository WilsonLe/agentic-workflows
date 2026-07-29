#!/usr/bin/env python3
"""Run the complete local validation contract for this repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_SURFACES = (
    "plugins",
    "scripts",
    "tests",
)


def run(*arguments: str) -> None:
    command = [*arguments]
    print(f"+ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, "scripts/validate_plugin_packages.py")
    run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v")
    run(sys.executable, "-m", "ruff", "check", *PYTHON_SURFACES)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
