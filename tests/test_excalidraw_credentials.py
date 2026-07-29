from __future__ import annotations

import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "excalidraw" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import excalidraw_credential_common as common  # noqa: E402
import excalidraw_configure_credentials as configure  # noqa: E402
import account_credential_common as shared  # noqa: E402

SYNTHETIC_KEY = "synthetic-excalidraw-personal-key-for-tests-only"


class ExcalidrawCredentialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def source(self, text: str = SYNTHETIC_KEY, mode: int = 0o600) -> Path:
        source = self.root / "excalidraw.key"
        source.write_text(text, encoding="utf-8")
        source.chmod(mode)
        return source

    def test_secure_source_requires_exact_confirmation(self) -> None:
        source = self.source(mode=0o644)
        with self.assertRaises(common.CredentialError):
            configure.secure_source(source, None)
        secured = configure.secure_source(source, configure.SECURE_SOURCE_CONFIRMATION)
        self.assertEqual(stat.S_IMODE(secured.stat().st_mode), 0o600)

    def test_source_rejects_symlink_and_git_location(self) -> None:
        source = self.source()
        link = self.root / "link"
        link.symlink_to(source)
        with self.assertRaises(common.CredentialError):
            common.inspect_source(link)
        repository = self.root / "repo"
        (repository / ".git").mkdir(parents=True)
        inside = repository / "key"
        inside.write_text(SYNTHETIC_KEY, encoding="utf-8")
        inside.chmod(0o600)
        with self.assertRaises(common.CredentialError):
            common.inspect_source(inside)

    def test_read_token_accepts_personal_json_and_rejects_workspace(self) -> None:
        source = self.source(
            json.dumps({"token_type": "personal", "token": SYNTHETIC_KEY})
        )
        self.assertEqual(configure.read_token(source), SYNTHETIC_KEY)
        source.write_text(
            json.dumps({"token_type": "workspace", "token": SYNTHETIC_KEY}),
            encoding="utf-8",
        )
        with self.assertRaises(common.CredentialError):
            configure.read_token(source)

    def test_protected_record_is_strict_and_owner_only(self) -> None:
        destination = self.root / "config" / "credentials.json"
        common.atomic_private_write(
            destination, common.encode_credential(SYNTHETIC_KEY)
        )
        self.assertEqual(stat.S_IMODE(destination.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o400)
        record = common.load_credential(destination)
        self.assertEqual(record["provider"], "excalidraw")
        self.assertEqual(record["token_type"], "personal")
        self.assertEqual(record["token"], SYNTHETIC_KEY)

    def test_provider_adapter_uses_shared_credential_primitives(self) -> None:
        self.assertIs(common.atomic_private_write, shared.atomic_private_write)
        self.assertIs(common.validate_private_file, shared.validate_private_file)
        self.assertIs(common.validate_token, shared.validate_token)

    def test_archive_moves_verified_source_and_fails_on_collision(self) -> None:
        source = self.source()
        with mock.patch.object(shared.Path, "home", return_value=self.root / "home"):
            archived = common.archive_source(source)
            self.assertFalse(source.exists())
            self.assertTrue(archived.is_file())
            self.assertEqual(stat.S_IMODE(archived.stat().st_mode), 0o400)
            replacement = self.source()
            with self.assertRaises(common.CredentialError):
                common.archive_source(replacement)

    def test_archive_failure_moves_source_back(self) -> None:
        source = self.source()
        home = self.root / "home"
        with (
            mock.patch.object(shared.Path, "home", return_value=home),
            mock.patch.object(
                shared.Path,
                "chmod",
                side_effect=(None, OSError("synthetic chmod failure"), None),
            ),
        ):
            with self.assertRaises(common.CredentialError):
                common.archive_source(source)
        self.assertTrue(source.is_file())
        self.assertFalse(
            (
                home
                / ".config"
                / "amsoft"
                / "excalidraw"
                / "imported-sources"
                / source.name
            ).exists()
        )

    def test_redaction_removes_exact_key(self) -> None:
        text = common.redact_exact(f"header={SYNTHETIC_KEY}", SYNTHETIC_KEY)
        self.assertNotIn(SYNTHETIC_KEY, text)
        self.assertIn("[REDACTED_EXCALIDRAW_KEY]", text)


if __name__ == "__main__":
    unittest.main()
