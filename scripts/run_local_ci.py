#!/usr/bin/env python3
"""Run the checks previously split across automatic GitHub Actions jobs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*arguments: str) -> None:
    print(f"+ {' '.join(arguments)}", flush=True)
    subprocess.run(arguments, cwd=ROOT, check=True)


def main() -> int:
    for executable in ("magick",):
        if shutil.which(executable) is None:
            raise SystemExit(f"Local CI requires {executable} on PATH.")

    run(sys.executable, "scripts/validate_repository.py")
    run(sys.executable, "scripts/generate_plugin_packages.py", "--check")
    with tempfile.TemporaryDirectory(prefix="agentic-local-ci-") as scratch:
        run(sys.executable, "scripts/generate_plugin_packages.py", "--build", scratch)
        run(sys.executable, "scripts/validate_plugin_packages.py", "--build-root", scratch)
    print("Local CI passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
