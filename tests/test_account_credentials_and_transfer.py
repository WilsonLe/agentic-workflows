from __future__ import annotations

import base64
import importlib
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
cloudflare_api = importlib.import_module("cloudflare_api")
cloudflare = importlib.import_module("cloudflare_configure_credentials")
digitalocean = importlib.import_module("digitalocean_configure_credentials")
digitalocean_cli = importlib.import_module("digitalocean_cli")
transfer = importlib.import_module("agentic_workflow_config_transfer")

SYNTHETIC_CF = "cfut_" + "synthetic-cloudflare-token-for-tests-only"
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
            common.read_private_text(link)
        source.chmod(0o644)
        with self.assertRaises(common.CredentialError):
            common.read_private_text(source)

    def test_cloudflare_classification_rejects_global_key_and_conflicts(self) -> None:
        self.assertEqual(
            cloudflare.classify_token(SYNTHETIC_CF, "auto"),
            "user_api_token",
        )
        with self.assertRaises(common.CredentialError):
            cloudflare.classify_token("cfk_synthetic-global-key", "auto")
        with self.assertRaises(common.CredentialError):
            cloudflare.classify_token(SYNTHETIC_CF, "account_api_token")

    def test_cloudflare_tls_uses_loaded_default_trust(self) -> None:
        default_context = mock.Mock()
        default_context.cert_store_stats.return_value = {"x509_ca": 10}
        with mock.patch.object(
            cloudflare_api.ssl,
            "create_default_context",
            return_value=default_context,
        ) as create_context:
            self.assertIs(cloudflare_api.tls_context(), default_context)
        create_context.assert_called_once_with()

    def test_cloudflare_tls_uses_readable_macos_system_bundle_fallback(self) -> None:
        default_context = mock.Mock()
        default_context.cert_store_stats.return_value = {"x509_ca": 0}
        fallback_context = mock.Mock()
        bundle = self.source("system-ca.pem", "synthetic CA bundle")
        with (
            mock.patch.object(
                cloudflare_api.ssl,
                "create_default_context",
                side_effect=(default_context, fallback_context),
            ) as create_context,
            mock.patch.object(cloudflare_api.platform, "system", return_value="Darwin"),
            mock.patch.object(cloudflare_api, "Path", return_value=bundle),
        ):
            self.assertIs(cloudflare_api.tls_context(), fallback_context)
        self.assertEqual(
            create_context.call_args_list,
            [mock.call(), mock.call(cafile=str(bundle))],
        )

    def test_cloudflare_tls_fails_closed_without_trusted_bundle(self) -> None:
        default_context = mock.Mock()
        default_context.cert_store_stats.return_value = {"x509_ca": 0}
        with (
            mock.patch.object(
                cloudflare_api.ssl,
                "create_default_context",
                return_value=default_context,
            ),
            mock.patch.object(cloudflare_api.platform, "system", return_value="Linux"),
        ):
            with self.assertRaises(cloudflare_api.CloudflareAPIError):
                cloudflare_api.tls_context()

    def test_digitalocean_yaml_extracts_only_matching_access_token(self) -> None:
        config = self.source(
            "doctl.yml",
            "access-token: " + SYNTHETIC_DO + "\noutput: json\ncontext: default\n",
        )
        self.assertEqual(digitalocean.yaml_token(config), SYNTHETIC_DO)

    def test_redaction_removes_exact_tokens(self) -> None:
        output = common.redact_exact(
            f"stdout={SYNTHETIC_CF} stderr={SYNTHETIC_DO}",
            [SYNTHETIC_CF, SYNTHETIC_DO],
        )
        self.assertNotIn(SYNTHETIC_CF, output)
        self.assertNotIn(SYNTHETIC_DO, output)
        self.assertEqual(output.count("[REDACTED]"), 2)

    def test_digitalocean_default_context_account_get_is_read_only(self) -> None:
        self.assertTrue(
            digitalocean_cli.is_read_only(
                ["--context", "default", "account", "get", "--output", "json"]
            )
        )
        self.assertFalse(digitalocean_cli.is_read_only(["compute", "droplet", "create"]))
        with self.assertRaises(common.CredentialError):
            digitalocean_cli.is_read_only(
                ["account", "get", "--access-token", SYNTHETIC_DO]
            )

    def test_digitalocean_child_environment_strips_inherited_tokens(self) -> None:
        binary = self.root / "doctl"
        binary.write_text(
            "#!/bin/sh\nprintf '%s|%s' \"$DIGITALOCEAN_ACCESS_TOKEN\" "
            "\"${DIGITALOCEAN_TOKEN-unset}\"\n",
            encoding="utf-8",
        )
        binary.chmod(0o700)
        with mock.patch.dict(
            os.environ,
            {
                "DIGITALOCEAN_ACCESS_TOKEN": "inherited-access",
                "DIGITALOCEAN_TOKEN": "inherited-alias",
            },
        ):
            result = digitalocean_cli.run_doctl(
                SYNTHETIC_DO,
                ["account", "get"],
                executable=str(binary),
            )
        self.assertEqual(result.stdout, f"{SYNTHETIC_DO}|unset")


class TransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.payload = transfer.validate_payload(
            {
                "schema_version": 1,
                "preferences": {
                    "preferred_workflow_ids": [
                        "railway-account-operations",
                        "standard-development-workflow",
                    ],
                    "default_workflow_id": "standard-development-workflow",
                    "response_language": "en-AU",
                },
                "credentials": {
                    "railway": {
                        "token_type": "account",
                        "token": SYNTHETIC_RAILWAY,
                    },
                    "cloudflare": {
                        "token_type": "user_api_token",
                        "token": SYNTHETIC_CF,
                    },
                    "digitalocean": {
                        "token_type": "personal_access_token",
                        "token": SYNTHETIC_DO,
                    },
                },
            }
        )

    def portable_envelope(self) -> dict[str, object]:
        return transfer.encrypt_payload(
            self.payload,
            "portable-passphrase",
            PASSPHRASE,
        )

    def test_portable_round_trip_contains_no_plaintext_secret(self) -> None:
        envelope = self.portable_envelope()
        encoded = transfer.canonical_json(envelope)
        for token in (SYNTHETIC_RAILWAY, SYNTHETIC_CF, SYNTHETIC_DO):
            self.assertNotIn(token.encode(), encoded)
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

    def test_import_applies_all_records_with_protected_modes(self) -> None:
        preferences = self.root / "prefs" / "config.json"
        paths = {
            provider: self.root / provider / "credentials.json"
            for provider in transfer.PROVIDER_PATHS
        }
        transfer.apply_payload(
            self.payload,
            verify=False,
            preferences_path=preferences,
            provider_paths=paths,
        )
        for path in (preferences, *paths.values()):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o400)
        self.assertEqual(
            json.loads(paths["railway"].read_text())["token_type"],
            "account",
        )
        self.assertEqual(
            json.loads(paths["cloudflare"].read_text())["provider"],
            "cloudflare",
        )

    def test_import_rolls_back_every_record_on_verification_failure(self) -> None:
        preferences = self.root / "prefs" / "config.json"
        paths = {
            provider: self.root / provider / "credentials.json"
            for provider in transfer.PROVIDER_PATHS
        }
        old_preferences = transfer.canonical_json(
            {
                "preferred_workflow_ids": [],
                "default_workflow_id": None,
                "response_language": None,
            }
        )
        common.atomic_private_write(preferences, old_preferences)
        old_records: dict[str, bytes] = {}
        for provider, path in paths.items():
            record = (
                json.dumps({"token_type": "account", "token": "old-railway"}).encode()
                if provider == "railway"
                else common.encode_credential(
                    provider,
                    next(iter(transfer.TOKEN_TYPES[provider])),
                    f"old-{provider}",
                )
            )
            common.atomic_private_write(path, record)
            old_records[provider] = record
        with mock.patch.object(
            transfer,
            "verify_imported_credentials",
            side_effect=transfer.TransferError("synthetic failure"),
        ):
            with self.assertRaises(transfer.TransferError):
                transfer.apply_payload(
                    self.payload,
                    verify=True,
                    preferences_path=preferences,
                    provider_paths=paths,
                )
        self.assertEqual(preferences.read_bytes(), old_preferences)
        for provider, path in paths.items():
            self.assertEqual(path.read_bytes(), old_records[provider])

    def test_sanitized_preview_has_no_secret_derived_values(self) -> None:
        preview = transfer.sanitized_preview(self.payload)
        text = json.dumps(preview)
        for token in (SYNTHETIC_RAILWAY, SYNTHETIC_CF, SYNTHETIC_DO):
            self.assertNotIn(token, text)
        self.assertEqual(
            sorted(preview["providers"]),
            ["cloudflare", "digitalocean", "railway"],
        )


if __name__ == "__main__":
    unittest.main()
