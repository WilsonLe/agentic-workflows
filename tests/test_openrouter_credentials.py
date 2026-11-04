from __future__ import annotations

import importlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "agentic-workflows" / "scripts"
sys.path.insert(0, str(SCRIPTS))

common = importlib.import_module("account_credential_common")
KEY = b"synthetic-openrouter-key-for-tests-only\r\n"
OTHER = b"synthetic-different-openrouter-key\n"


@unittest.skipUnless(os.name == "posix", "requires owner-only POSIX file permissions")
class OpenRouterCredentialTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name).resolve()
        self.source_root = self.scratch / "source repo"
        self.destination_root = self.scratch / "linked worktree"
        self.make_repo(self.source_root)
        self.git(self.source_root, "worktree", "add", "-qb", "feature", str(self.destination_root))
        self.destination_root.chmod(0o755)
        self.source_key = self.key_path(self.source_root)
        self.destination_key = self.key_path(self.destination_root)
        self.write_key(self.source_key, KEY)

    @staticmethod
    def git(root: Path, *args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)

    def make_repo(self, root: Path) -> None:
        root.mkdir(mode=0o755)
        root.chmod(0o755)
        self.git(root, "init", "-q")
        self.git(root, "config", "core.excludesFile", os.devnull)
        (root / ".gitignore").write_text("/.cli/\n", encoding="utf-8")
        self.git(root, "add", ".gitignore")
        self.git(
            root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "fixture",
        )

    @staticmethod
    def key_path(root: Path) -> Path:
        return root / ".cli" / "openrouter" / "api-key"

    @staticmethod
    def write_key(path: Path, contents: bytes) -> None:
        path.parent.parent.mkdir(mode=0o700, exist_ok=True)
        path.parent.mkdir(mode=0o700, exist_ok=True)
        path.write_bytes(contents)
        path.chmod(0o600)

    def copy_cli(
        self, *, source_root: Path | None = None, destination_root: Path | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(SCRIPTS / "copy_openrouter_key.py"),
             "--source-root", str(source_root or self.source_root),
             "--destination-root", str(destination_root or self.destination_root)],
            capture_output=True, check=False, timeout=20,
        )
        self.assertNotIn(KEY.strip(), result.stdout + result.stderr)
        self.assertNotIn(OTHER.strip(), result.stdout + result.stderr)
        return result

    def test_copy_preserves_bytes_and_is_independent_private_and_idempotent(self) -> None:
        copied = self.copy_cli()
        self.assertEqual(copied.returncode, 0, copied.stderr)
        self.assertEqual(self.destination_key.read_bytes(), KEY)
        self.assertFalse(self.destination_key.samefile(self.source_key))
        self.assertEqual(stat.S_IMODE(self.destination_key.stat().st_mode), 0o600)
        for directory in (self.destination_key.parent, self.destination_key.parent.parent):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        for root in (self.source_root, self.destination_root):
            self.git(root, "check-ignore", "-q", ".cli/openrouter/api-key")
            self.assertEqual(self.git(root, "ls-files", "--", ".cli"), b"")
        first_inode = self.destination_key.stat().st_ino
        repeated = self.copy_cli()
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn(b"already present", repeated.stdout)
        self.assertEqual(self.destination_key.stat().st_ino, first_inode)
        self.assertEqual(common.load_openrouter_key(self.destination_root), KEY.strip().decode("ascii"))

    def test_copy_leaves_existing_conflicting_destination_untouched(self) -> None:
        self.write_key(self.destination_key, OTHER)
        rejected = self.copy_cli()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn(b"different OpenRouter key", rejected.stderr)
        self.assertEqual(self.destination_key.read_bytes(), OTHER)
        self.assertEqual(self.source_key.read_bytes(), KEY)

    def test_copy_refuses_a_destination_created_after_preflight(self) -> None:
        link = os.link

        def race(source: Path, destination: Path) -> None:
            self.write_key(destination, OTHER)
            link(source, destination)

        with mock.patch.object(common.os, "link", side_effect=race):
            with self.assertRaises(common.CredentialError):
                common.copy_openrouter_key(self.source_root, self.destination_root)
        self.assertEqual(self.destination_key.read_bytes(), OTHER)
        self.assertEqual(list(self.destination_key.parent.iterdir()), [self.destination_key])

    def test_copy_rejects_same_root_unrelated_repo_and_forged_gitfile(self) -> None:
        same = self.copy_cli(destination_root=self.source_root)
        self.assertNotEqual(same.returncode, 0)
        unrelated = self.scratch / "unrelated"
        self.make_repo(unrelated)
        rejected = self.copy_cli(destination_root=unrelated)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse(self.key_path(unrelated).exists())
        alias = self.scratch / "gitfile alias"
        alias.mkdir()
        (alias / ".git").write_text(f"gitdir: {self.source_root / '.git'}\n", encoding="utf-8")
        (alias / ".gitignore").write_text("/.cli/\n", encoding="utf-8")
        forged = self.copy_cli(destination_root=alias)
        self.assertNotEqual(forged.returncode, 0)
        self.assertIn(b"registered Git worktree", forged.stderr)
        self.assertFalse(self.key_path(alias).exists())

    def test_copy_rejects_unignored_destination_and_tracked_source(self) -> None:
        ignore = self.destination_root / ".gitignore"
        ignore.write_text("", encoding="utf-8")
        refused = self.copy_cli()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn(b"ignored and untracked", refused.stderr)
        self.assertFalse(self.destination_key.exists())
        ignore.write_text("/.cli/\n", encoding="utf-8")
        self.git(self.source_root, "add", "-f", str(self.source_key))
        with mock.patch.dict(os.environ, {"GIT_INDEX_FILE": str(self.scratch / "alternate index")}):
            refused = self.copy_cli()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn(b"ignored and untracked", refused.stderr)
        self.assertFalse(self.destination_key.exists())

    def test_copy_rejects_symlinked_worktree_directories_and_shared_inode(self) -> None:
        alias = self.scratch / "alias"
        alias.symlink_to(self.destination_root, target_is_directory=True)
        self.assertNotEqual(self.copy_cli(destination_root=alias).returncode, 0)
        outside = self.scratch / "outside"
        outside.mkdir(mode=0o700)
        linked_cli = self.destination_root / ".cli"
        linked_cli.symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.copy_cli().returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])
        linked_cli.unlink()
        linked_cli.mkdir(mode=0o700)
        self.destination_key.parent.mkdir(mode=0o700)
        os.link(self.source_key, self.destination_key)
        shared = self.copy_cli()
        self.assertNotEqual(shared.returncode, 0)
        self.assertIn(b"independent regular file", shared.stderr)
        self.assertTrue(self.destination_key.samefile(self.source_key))

    def test_loader_requires_exact_worktree_and_never_uses_inherited_key(self) -> None:
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": OTHER.strip().decode("ascii")}):
            self.assertEqual(common.load_openrouter_key(self.source_root), KEY.strip().decode("ascii"))
            with self.assertRaises(common.CredentialError):
                common.load_openrouter_key(self.destination_root)
        with self.assertRaises(common.CredentialError):
            common.load_openrouter_key(self.scratch)
        with self.assertRaises(common.CredentialError):
            common.load_openrouter_key(self.source_key.parent)
        self.source_key.chmod(0o644)
        with self.assertRaises(common.CredentialError):
            common.load_openrouter_key(self.source_root)
        self.source_key.chmod(0o600)
        self.source_key.parent.parent.chmod(0o755)
        with self.assertRaises(common.CredentialError):
            common.load_openrouter_key(self.source_root)

    def test_invalid_file_content_is_never_printed_or_copied(self) -> None:
        for bad in (b"", b"a\x00b", KEY + b"\n", KEY + OTHER, b"\xff", b"a" * 65_537):
            with self.subTest(size=len(bad)):
                self.source_key.write_bytes(bad)
                rejected = self.copy_cli()
                self.assertNotEqual(rejected.returncode, 0)
                self.assertFalse(self.destination_key.exists())


if __name__ == "__main__":
    unittest.main()
