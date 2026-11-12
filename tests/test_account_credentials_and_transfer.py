from __future__ import annotations

import base64
import importlib
from contextlib import redirect_stdout
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "agentic-workflows" / "scripts"
sys.path.insert(0, str(SCRIPTS))

common = importlib.import_module("account_credential_common")
transfer = importlib.import_module("agentic_workflow_config_transfer")

SYNTHETIC_DO = "dop_v1_" + "synthetic-digitalocean-token-for-tests-only"
SYNTHETIC_RAILWAY = "synthetic-railway-account-token-for-tests-only"
PASSPHRASE = b"synthetic passphrase for tests only"


class ProtectedCredentialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def source(self, name: str, value: str) -> Path:
        path = self.root / name
        path.write_text(value, encoding="utf-8")
        path.chmod(0o600)
        return path

    def test_atomic_private_write_uses_protected_modes_and_rejects_implicit_replace(self) -> None:
        destination = self.root / "config" / "credentials.json"
        common.atomic_private_write(destination, b"first")
        self.assertEqual(stat.S_IMODE(destination.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o400)
        with self.assertRaises(common.CredentialError):
            common.atomic_private_write(destination, b"second")
        self.assertEqual(destination.read_bytes(), b"first")
        common.atomic_private_write(destination, b"second", replace=True)
        self.assertEqual(destination.read_bytes(), b"second")

    def test_atomic_private_write_syncs_file_and_parent_directory(self) -> None:
        destination = self.root / "durable" / "credentials.json"
        with mock.patch.object(common.os, "fsync", wraps=os.fsync) as sync:
            common.atomic_private_write(destination, b"durable")
        expected_calls = 1 if os.name == "nt" else 2
        self.assertGreaterEqual(sync.call_count, expected_calls)

    def test_source_rejects_symlink_and_broad_permissions(self) -> None:
        source = self.source("token", SYNTHETIC_DO)
        link = self.root / "link"
        link.symlink_to(source)
        with self.assertRaises(common.CredentialError):
            common.validate_private_file(link, mode=0o600)
        source.chmod(0o644)
        with self.assertRaises(common.CredentialError):
            common.validate_private_file(source, mode=0o600)



class TransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.payload = transfer.validate_payload(
            {
                "schema_version": 2,
                "preferences": {
                    "preferred_workflow_ids": [
                        "railway-account-operations",
                        "standard-development-workflow",
                    ],
                    "default_workflow_id": "standard-development-workflow",
                    "response_language": "en-AU",
                },

            }
        )

    def portable_envelope(self) -> dict[str, object]:
        return transfer.encrypt_payload(
            self.payload,
            "portable-passphrase",
            PASSPHRASE,
        )

    def test_portable_round_trip_contains_no_plaintext_preferences(self) -> None:
        envelope = self.portable_envelope()
        encoded = transfer.canonical_json(envelope)
        for value in ("en-AU", "standard-development-workflow"):
            self.assertNotIn(value.encode(), encoded)
        decoded = transfer.decrypt_envelope(
            envelope,
            passphrase_provider=lambda: PASSPHRASE,
        )
        self.assertEqual(decoded, self.payload)

    def test_non_ascii_passphrase_is_normalized_cross_platform(self) -> None:
        composed = transfer.normalize_passphrase("long-passphrase-é-2026")
        decomposed = transfer.normalize_passphrase("long-passphrase-e\u0301-2026")
        self.assertEqual(composed, decomposed)

    def test_wrong_passphrase_and_tampering_fail_authentication(self) -> None:
        envelope = self.portable_envelope()
        with self.assertRaises(transfer.TransferError):
            transfer.decrypt_envelope(
                envelope,
                passphrase_provider=lambda: b"wrong passphrase long enough",
            )
        tampered = json.loads(json.dumps(envelope))
        ciphertext = bytearray(base64.b64decode(tampered["ciphertext"]))
        ciphertext[-1] ^= 1
        tampered["ciphertext"] = base64.b64encode(ciphertext).decode()
        with self.assertRaises(transfer.TransferError):
            transfer.decrypt_envelope(
                tampered,
                passphrase_provider=lambda: PASSPHRASE,
            )

    def test_tampered_authenticated_metadata_fails(self) -> None:
        envelope = self.portable_envelope()
        envelope["origin_plugin"] = "different-plugin"
        with self.assertRaises(transfer.TransferError):
            transfer.decrypt_envelope(
                envelope,
                passphrase_provider=lambda: PASSPHRASE,
            )

    def test_unknown_payload_and_envelope_fields_are_rejected(self) -> None:
        bad_payload = json.loads(json.dumps(self.payload))
        bad_payload["unexpected"] = True
        with self.assertRaises(transfer.TransferError):
            transfer.validate_payload(bad_payload)
        envelope = self.portable_envelope()
        envelope["unexpected"] = True
        with self.assertRaises(transfer.TransferError):
            transfer.decrypt_envelope(
                envelope,
                passphrase_provider=lambda: PASSPHRASE,
            )

    def test_export_file_is_private_and_self_decrypts(self) -> None:
        path = self.root / "portable.agenticx"
        envelope = self.portable_envelope()
        transfer.write_export(path, envelope)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        loaded = transfer.read_envelope(path)
        self.assertEqual(
            transfer.decrypt_envelope(loaded, passphrase_provider=lambda: PASSPHRASE),
            self.payload,
        )

    def test_import_applies_only_preferences_with_protected_modes(self) -> None:
        preferences = self.root / "prefs" / "config.json"
        transfer.apply_payload(self.payload, preferences_path=preferences)
        self.assertEqual(stat.S_IMODE(preferences.stat().st_mode), 0o400)
        self.assertEqual(json.loads(preferences.read_text()), self.payload["preferences"])
        self.assertEqual(set(self.root.iterdir()), {preferences.parent})

    def test_atomic_preference_write_failure_preserves_prior_state(self) -> None:
        preferences = self.root / "prefs" / "config.json"
        old = b'{"response_language":"vi"}'
        common.atomic_private_write(preferences, old)
        with mock.patch.object(common.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(transfer.TransferError):
                transfer.apply_payload(self.payload, preferences_path=preferences)
        self.assertEqual(preferences.read_bytes(), old)

    def test_legacy_preference_only_payload_normalizes_to_current_version(self) -> None:
        legacy = {"schema_version": 1, "preferences": self.payload["preferences"], "credentials": {}}
        envelope = transfer.encrypt_payload(legacy, "portable-passphrase", PASSPHRASE)
        self.assertEqual(
            transfer.decrypt_envelope(envelope, passphrase_provider=lambda: PASSPHRASE), self.payload,
        )

    def test_legacy_provider_credentials_rejected_before_writes_without_exposure(self) -> None:
        legacy = {
            "schema_version": 1, "preferences": self.payload["preferences"],
            "credentials": {"railway": {"token_type": "account", "token": SYNTHETIC_RAILWAY}},
        }
        with mock.patch.object(transfer, "atomic_private_write") as write:
            with self.assertRaisesRegex(transfer.TransferError, "authenticate Infisical separately") as failure:
                transfer.apply_payload(legacy, preferences_path=self.root / "prefs.json")
            write.assert_not_called()
        self.assertNotIn(SYNTHETIC_RAILWAY, str(failure.exception))
        envelope = transfer.encrypt_payload(legacy, "portable-passphrase", PASSPHRASE)
        with self.assertRaisesRegex(transfer.TransferError, "authenticate Infisical separately"):
            transfer.decrypt_envelope(envelope, passphrase_provider=lambda: PASSPHRASE)
        self.assertFalse((self.root / "prefs.json").exists())

    def test_current_payload_rejects_credentials_unknown_version_and_boolean_version(self) -> None:
        for extra in ({"credentials": {}}, {"schema_version": 3}, {"schema_version": True}):
            with self.subTest(extra=extra), self.assertRaises(transfer.TransferError):
                transfer.validate_payload({**self.payload, **extra})

    def test_sanitized_preview_contains_only_preference_field_names(self) -> None:
        self.assertEqual(transfer.sanitized_preview(self.payload), {
            "preference_fields": sorted(self.payload["preferences"]),
        })
        self.assertNotIn("en-AU", json.dumps(transfer.sanitized_preview(self.payload)))

    def test_cli_export_and_import_use_only_preferences_and_make_no_provider_calls(self) -> None:
        original = self.root / "original" / "config.json"
        restored = self.root / "restored" / "config.json"
        archive = self.root / "preferences.agenticx"
        common.atomic_private_write(original, transfer.canonical_json(self.payload["preferences"]))
        with mock.patch.object(transfer, "local_key", return_value=b"k" * transfer.KEY_BYTES):
            with mock.patch.object(transfer.subprocess, "run", side_effect=AssertionError("no provider calls")):
                for args in (
                    ["export", "--output", str(archive), "--preferences-file", str(original)],
                    ["import", str(archive), "--preferences-file", str(restored)],
                ):
                    with mock.patch.object(sys, "argv", ["transfer", *args]), redirect_stdout(io.StringIO()) as stdout:
                        transfer.main()
                    self.assertNotIn("en-AU", stdout.getvalue())
                    self.assertNotIn("providers", stdout.getvalue())
        self.assertEqual(json.loads(restored.read_text()), self.payload["preferences"])
        self.assertEqual(set(self.root.iterdir()), {original.parent, restored.parent, archive})

    def test_import_rejects_unsafe_destination_and_git_writes(self) -> None:
        path = self.root / "prefs.json"
        path.write_text("old")
        path.chmod(0o644)
        with self.assertRaises(common.CredentialError):
            transfer.apply_payload(self.payload, preferences_path=path)
        self.assertEqual(path.read_text(), "old")
        project = self.root / "project"
        (project / ".git").mkdir(parents=True)
        with self.assertRaises(transfer.TransferError):
            transfer.apply_payload(self.payload, preferences_path=project / "prefs.json")
        self.assertFalse((project / "prefs.json").exists())


if __name__ == "__main__":
    unittest.main()
