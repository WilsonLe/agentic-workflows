from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "agentic-workflows" / "scripts"
sys.path.insert(0, str(SCRIPTS))

transfer = importlib.import_module("agentic_workflow_config_transfer")


class CrossPlatformEnvelopeTests(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return transfer.validate_payload(
            {
                "schema_version": 1,
                "preferences": {
                    "preferred_workflow_ids": ["standard-development-workflow"],
                    "default_workflow_id": "standard-development-workflow",
                    "response_language": "en-AU",
                },
                "credentials": {
                    "railway": {
                        "token_type": "account",
                        "token": "synthetic-cross-platform-token",
                    }
                },
            }
        )

    def test_portable_envelope_round_trip_is_platform_neutral(self) -> None:
        passphrase = transfer.normalize_passphrase("portable-passphrase-2026")
        payload = self.payload()
        envelope = transfer.encrypt_payload(payload, "portable-passphrase", passphrase)
        serialized = transfer.canonical_json(envelope)
        reloaded = json.loads(serialized)
        self.assertEqual(
            transfer.decrypt_envelope(
                reloaded,
                passphrase_provider=lambda: passphrase,
            ),
            payload,
        )

    def test_unicode_normalization_matches_across_operating_systems(self) -> None:
        self.assertEqual(
            transfer.normalize_passphrase("portable-é-passphrase"),
            transfer.normalize_passphrase("portable-e\u0301-passphrase"),
        )

    def test_newline_conventions_do_not_change_envelope_meaning(self) -> None:
        passphrase = transfer.normalize_passphrase("portable-passphrase-2026")
        envelope = transfer.encrypt_payload(
            self.payload(),
            "portable-passphrase",
            passphrase,
        )
        compact = transfer.canonical_json(envelope).decode("utf-8")
        crlf = json.dumps(envelope, indent=2).replace("\n", "\r\n")
        self.assertEqual(json.loads(compact), json.loads(crlf))
        self.assertEqual(
            transfer.decrypt_envelope(
                json.loads(crlf),
                passphrase_provider=lambda: passphrase,
            ),
            self.payload(),
        )


if __name__ == "__main__":
    unittest.main()
