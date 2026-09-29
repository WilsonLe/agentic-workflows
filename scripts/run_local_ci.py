#!/usr/bin/env python3
"""Run the checks previously split across automatic GitHub Actions jobs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*arguments: str) -> None:
    print(f"+ {' '.join(arguments)}", flush=True)
    subprocess.run(arguments, cwd=ROOT, check=True)


def main() -> int:
    for executable in ("magick", "claude"):
        if shutil.which(executable) is None:
            raise SystemExit(f"Local CI requires {executable} on PATH.")

    run(sys.executable, "scripts/validate_repository.py")
    run(sys.executable, "scripts/generate_plugin_packages.py", "--check")
    run("claude", "plugin", "validate", ".")
    for package in sorted((ROOT / "generated/claude/plugins").iterdir()):
        if package.is_dir():
            run("claude", "plugin", "validate", str(package.relative_to(ROOT)))
    run(sys.executable, "scripts/smoke_claude_package.py")
    print("Local CI passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
