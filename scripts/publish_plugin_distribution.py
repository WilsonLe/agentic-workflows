#!/usr/bin/env python3
"""Publish a verified portable distribution to origin's dist branch."""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path


MAIN_REF = "refs/heads/main"
DIST_REF = "refs/heads/dist"


def git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, text=True, stdout=subprocess.PIPE
    ).stdout.strip()


def remote_revision(ref: str) -> str:
    return git("ls-remote", "--refs", "origin", ref).partition("\t")[0]


def publish(source: str, distribution: Path) -> None:
    if source != git("rev-parse", "HEAD"):
        raise SystemExit("Source revision must match the publisher checkout.")
    if source != remote_revision(MAIN_REF):
        print("Source is no longer origin/main. Skipping distribution publish.")
        return

    parent = remote_revision(DIST_REF)
    if parent:
        git("fetch", "--no-tags", "origin", DIST_REF)
        if parent != git("rev-parse", "FETCH_HEAD"):
            raise SystemExit("origin/dist changed during publish. Retry from main.")

    git_dir = git("rev-parse", "--absolute-git-dir")
    with tempfile.TemporaryDirectory(prefix="plugin-dist-index-") as scratch:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(scratch) / "index"))
        stage = ("--git-dir", git_dir, "--work-tree", str(distribution))
        git(*stage, "read-tree", "--empty", cwd=distribution, env=env)
        git(
            *stage, "-c", "core.filemode=true", "-c", "core.autocrlf=false",
            "add", "--force", "--", "generated", "opencode.json",
            cwd=distribution, env=env,
        )
        tree = git(*stage, "write-tree", cwd=distribution, env=env)

    if parent and tree == git("rev-parse", f"{parent}^{{tree}}"):
        print("Portable distribution already matches origin/dist.")
        return

    parents = ["-p", parent] if parent else []
    commit = git(
        "-c", "user.name=github-actions[bot]",
        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit-tree", tree, *parents,
        "-m", "Publish portable plugin distribution", "-m", f"Source-Commit: {source}",
    )
    if source != remote_revision(MAIN_REF):
        print("Source is no longer origin/main. Skipping distribution publish.")
        return
    git("push", "origin", f"{commit}:{DIST_REF}")
    print(f"Published {commit} from source {source}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="full source commit SHA")
    parser.add_argument("--build-root", type=Path, required=True, help="verified distribution directory")
    args = parser.parse_args()
    publish(args.source, args.build_root.resolve(strict=True))
