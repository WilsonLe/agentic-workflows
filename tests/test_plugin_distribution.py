from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_plugin_packages.py"
PUBLISHER = ROOT / "scripts/publish_plugin_distribution.py"
CLAUDE = Path("generated/claude/plugins/agentic-workflows")
OPENCODE = Path("generated/opencode/agentic-workflows")


def run(*args: str | Path, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def files(root: Path) -> dict[Path, tuple[bytes, int]]:
    return {
        path.relative_to(root): (path.read_bytes(), path.stat().st_mode & stat.S_IXUSR)
        for path in root.rglob("*")
        if path.is_file()
    }


@unittest.skipUnless(os.name == "posix", "distribution checks require POSIX executable bits")
class BuildDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.output = self.scratch / "distribution"

    def generate(self, mode: str, output: Path | None = None) -> subprocess.CompletedProcess:
        return run(sys.executable, GENERATOR, mode, output or self.output, check=False)

    def build(self, output: Path | None = None) -> None:
        result = self.generate("--build", output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reproduces_existing_packages_without_changing_source(self) -> None:
        source = ROOT / "plugins/agentic-workflows"
        before = files(source)
        self.output.mkdir()
        self.build()
        second = self.scratch / "second"
        self.build(second)
        self.assertEqual(files(self.output), files(second))
        self.assertEqual(files(source), before)
        for path in (CLAUDE, OPENCODE):
            helper = "scripts/qr_code_generator.py"
            self.assertEqual(files(self.output / path)[Path(helper)], before[Path(helper)])
            self.assertFalse((self.output / path / "hooks").exists())
        self.assertEqual(
            json.loads((self.output / "opencode.json").read_text())["skills"],
            [f"./{OPENCODE.as_posix()}/skills"],
        )
        self.assertEqual(
            [path.name for path in (self.output / CLAUDE.parent).iterdir()],
            ["agentic-workflows"],
        )

    def test_check_reports_missing_changed_wrong_mode_extra_and_unsafe_entries(self) -> None:
        self.build()
        (self.output / "opencode.json").unlink()
        asset = self.output / CLAUDE / "CAPABILITIES.md"
        asset.write_text("changed", encoding="utf-8")
        asset.chmod(0o755)
        (self.output / "extra").mkdir()
        (self.output / "link").symlink_to(ROOT)
        result = self.generate("--check-build")
        self.assertNotEqual(result.returncode, 0)
        for message in (
            "distribution file missing: opencode.json",
            f"distribution content differs: {CLAUDE / asset.name}",
            f"distribution executable mode differs: {CLAUDE / asset.name}",
            "distribution unexpected entry: extra",
            "distribution unsafe entry: link",
        ):
            self.assertIn(message, result.stdout)

    def test_build_refuses_unsafe_or_nonempty_output(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "keep"
        sentinel.write_text("keep", encoding="utf-8")
        result = self.generate("--build")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("new or empty directory", result.stderr)
        self.assertEqual(sentinel.read_text(), "keep")
        link = self.scratch / "link"
        link.symlink_to(self.output)
        result = self.generate("--build", link)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not be a symlink", result.stderr)
        result = self.generate("--build", ROOT / "plugins/unsafe-build")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the source checkout", result.stderr)


@unittest.skipUnless(os.name == "posix", "Git publication tests require POSIX modes and hooks")
class PublishDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        self.remote = root / "origin.git"
        self.work = root / "checkout"
        self.work.mkdir()
        run("git", "init", "--bare", "--initial-branch=main", self.remote)
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Distribution test")
        self.git("config", "user.email", "distribution@example.invalid")
        self.git("remote", "add", "origin", str(self.remote))
        self.git("commit", "--allow-empty", "-m", "initial")
        self.git("push", "origin", "main")
        self.distribution = root / "distribution"
        (self.distribution / OPENCODE).mkdir(parents=True)
        (self.distribution / "opencode.json").write_text("{}", encoding="utf-8")
        self.asset = self.distribution / OPENCODE / "helper"
        self.asset.write_text("one", encoding="utf-8")
        self.asset.chmod(0o755)

    def git(self, *args: str) -> str:
        return run("git", *args, cwd=self.work).stdout.strip()

    def remote_git(self, *args: str) -> str:
        return run("git", *args, cwd=self.remote).stdout.strip()

    def publish(self) -> subprocess.CompletedProcess:
        return run(
            sys.executable, PUBLISHER, "--source", self.git("rev-parse", "HEAD"),
            "--build-root", self.distribution, cwd=self.work, check=False,
        )

    def assert_published(self) -> str:
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Published", result.stdout)
        return self.remote_git("rev-parse", "dist")

    def advance_main(self) -> None:
        self.git("commit", "--allow-empty", "-m", "next source")
        self.git("push", "origin", "main")

    def test_first_publish_identical_rebuild_and_forward_rollback(self) -> None:
        first = self.assert_published()
        self.assertIn(
            f"Source-Commit: {self.git('rev-parse', 'HEAD')}",
            self.remote_git("log", "-1", "--format=%B", first),
        )
        self.assertTrue(self.remote_git("ls-tree", first, str(OPENCODE / self.asset.name)).startswith("100755"))
        self.advance_main()
        unchanged = self.publish()
        self.assertEqual(unchanged.returncode, 0, unchanged.stdout + unchanged.stderr)
        self.assertIn("already matches", unchanged.stdout)
        self.assertEqual(self.remote_git("rev-parse", "dist"), first)
        self.asset.write_text("two", encoding="utf-8")
        second = self.assert_published()
        self.assertEqual(self.remote_git("rev-parse", f"{second}^"), first)
        self.advance_main()
        self.asset.write_text("one", encoding="utf-8")
        rollback = self.assert_published()
        self.assertEqual(self.remote_git("rev-parse", f"{rollback}^"), second)
        self.assertEqual(self.remote_git("rev-parse", f"{rollback}^{{tree}}"), self.remote_git("rev-parse", f"{first}^{{tree}}"))
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_stale_source_is_skipped(self) -> None:
        first = self.assert_published()
        stale = self.git("rev-parse", "HEAD")
        self.advance_main()
        self.git("checkout", "--detach", stale)
        self.asset.write_text("stale", encoding="utf-8")
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no longer origin/main", result.stdout)
        self.assertEqual(self.remote_git("rev-parse", "dist"), first)

    def test_rejected_push_keeps_last_distribution(self) -> None:
        first = self.assert_published()
        self.advance_main()
        self.asset.write_text("new candidate", encoding="utf-8")
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pre-receive hook declined", result.stderr)
        self.assertEqual(self.remote_git("rev-parse", "dist"), first)
