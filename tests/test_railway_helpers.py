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
PLUGIN = ROOT / "plugins" / "railway-account"
INSTALLER = PLUGIN / "scripts" / "railway_configure_credentials.py"
LAUNCHER = PLUGIN / "scripts" / "railway_cli.py"
SYNTHETIC_TOKEN = "synthetic-railway-account-token-for-tests-only"


class RailwayHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "downloaded-token.txt"
        self.destination = self.root / "config" / "credentials.json"
        self.source.write_text(SYNTHETIC_TOKEN + "\n", encoding="utf-8")

    def installer(self, *extra: str, source: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                str(source or self.source),
                "--destination",
                str(self.destination),
                "--confirm-account-token",
                "I_CONFIRM_RAILWAY_ACCOUNT_TOKEN",
                *extra,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def install_valid_credentials(self) -> None:
        result = self.installer()
        self.assertEqual(result.returncode, 0, result.stderr)

    def fake_railway(self) -> Path:
        binary_directory = self.root / "bin"
        binary_directory.mkdir(exist_ok=True)
        binary = binary_directory / "railway"
        binary.write_text(
            """#!/bin/sh
if [ "$1" = "variable" ] && [ "$2" = "list" ]; then
  printf '%s\\n' '{"DATABASE_URL":"private-value","PUBLIC_NAME":"visible-value"}'
  printf '%s\\n' 'warning-with-private-value' >&2
  exit 0
fi
printf 'api=%s project=%s args=%s\\n' "$RAILWAY_API_TOKEN" "${RAILWAY_TOKEN-unset}" "$*"
printf 'stderr-token=%s\\n' "$RAILWAY_API_TOKEN" >&2
""",
            encoding="utf-8",
        )
        binary.chmod(0o700)
        return binary_directory

    def launcher(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        child_environment = os.environ.copy()
        child_environment["PATH"] = f"{self.fake_railway()}:{child_environment.get('PATH', '')}"
        if environment:
            child_environment.update(environment)
        return subprocess.run(
            [
                sys.executable,
                str(LAUNCHER),
                "--credentials-file",
                str(self.destination),
                *arguments,
            ],
            text=True,
            capture_output=True,
            check=False,
            env=child_environment,
        )

    def test_installs_plaintext_account_token_with_protected_modes(self) -> None:
        result = self.installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SYNTHETIC_TOKEN, result.stdout + result.stderr)
        self.assertEqual(stat.S_IMODE(self.destination.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.destination.stat().st_mode), 0o400)
        self.assertEqual(
            json.loads(self.destination.read_text(encoding="utf-8")),
            {"token_type": "account", "token": SYNTHETIC_TOKEN},
        )
        self.assertTrue(self.source.exists())

    def test_installs_strict_account_json(self) -> None:
        self.source.write_text(
            json.dumps({"token_type": "account", "token": SYNTHETIC_TOKEN}),
            encoding="utf-8",
        )
        result = self.installer()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_non_account_json_without_leaking_token(self) -> None:
        self.source.write_text(
            json.dumps({"token_type": "workspace", "token": SYNTHETIC_TOKEN}),
            encoding="utf-8",
        )
        result = self.installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only token_type account is supported", result.stderr)
        self.assertNotIn(SYNTHETIC_TOKEN, result.stdout + result.stderr)
        self.assertFalse(self.destination.exists())

    def test_rejects_wrong_confirmation(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                str(self.source),
                "--destination",
                str(self.destination),
                "--confirm-account-token",
                "wrong",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_rejects_source_symlink(self) -> None:
        link = self.root / "token-link"
        link.symlink_to(self.source)
        result = self.installer(source=link)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a symlink", result.stderr)

    def test_requires_replace_and_preserves_existing_credentials(self) -> None:
        self.install_valid_credentials()
        original = self.destination.read_bytes()
        replacement = self.root / "replacement.txt"
        replacement.write_text("replacement-synthetic-token\n", encoding="utf-8")
        refused = self.installer(source=replacement)
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(self.destination.read_bytes(), original)
        replaced = self.installer("--replace", source=replacement)
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        payload = json.loads(self.destination.read_text(encoding="utf-8"))
        self.assertEqual(payload["token"], "replacement-synthetic-token")

    def test_rejects_destination_inside_git_worktree(self) -> None:
        repository = self.root / "repo"
        (repository / ".git").mkdir(parents=True)
        result = subprocess.run(
            [
                sys.executable,
                str(INSTALLER),
                str(self.source),
                "--destination",
                str(repository / "credentials.json"),
                "--confirm-account-token",
                "I_CONFIRM_RAILWAY_ACCOUNT_TOKEN",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside a Git worktree", result.stderr)

    def test_launcher_sets_only_api_token_and_redacts_both_streams(self) -> None:
        self.install_valid_credentials()
        result = self.launcher(
            "--",
            "whoami",
            "--json",
            environment={
                "RAILWAY_TOKEN": "inherited-project-token",
                "RAILWAY_API_TOKEN": "inherited-api-token",
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        combined = result.stdout + result.stderr
        self.assertNotIn(SYNTHETIC_TOKEN, combined)
        self.assertNotIn("inherited-project-token", combined)
        self.assertNotIn("inherited-api-token", combined)
        self.assertIn("[REDACTED_RAILWAY_ACCOUNT_TOKEN]", combined)
        self.assertIn("project=unset", result.stdout)

    def test_launcher_refuses_write_without_approval(self) -> None:
        result = self.launcher("--", "up")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--target-class", result.stderr)

    def test_launcher_allows_exact_help_but_not_help_as_write_value(self) -> None:
        self.install_valid_credentials()
        help_result = self.launcher("--", "variable", "set", "--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        bypass_result = self.launcher("--", "up", "--message", "--help")
        self.assertNotEqual(bypass_result.returncode, 0)
        self.assertIn("--target-class", bypass_result.stderr)

    def test_launcher_requires_production_and_destructive_approvals(self) -> None:
        self.install_valid_credentials()
        production = self.launcher(
            "--target-class",
            "production",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--",
            "restart",
            "--service",
            "api",
        )
        self.assertNotEqual(production.returncode, 0)
        self.assertIn("--confirm-production", production.stderr)
        destructive = self.launcher(
            "--target-class",
            "non-production",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--",
            "down",
            "--service",
            "api",
        )
        self.assertNotEqual(destructive.returncode, 0)
        self.assertIn("--confirm-destructive", destructive.stderr)

    def test_launcher_allows_fully_approved_write(self) -> None:
        self.install_valid_credentials()
        result = self.launcher(
            "--target-class",
            "production",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--confirm-production",
            "I_APPROVE_RAILWAY_PRODUCTION",
            "--confirm-destructive",
            "I_APPROVE_RAILWAY_DESTRUCTIVE",
            "--",
            "down",
            "--service",
            "api",
            "--yes",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("args=down --service api --yes", result.stdout)

    def test_variable_names_emits_keys_only(self) -> None:
        self.install_valid_credentials()
        result = self.launcher(
            "--",
            "variable-names",
            "--service",
            "api",
            "--environment",
            "production",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"variable_names": ["DATABASE_URL", "PUBLIC_NAME"]},
        )
        self.assertNotIn("private-value", result.stdout + result.stderr)
        self.assertNotIn("visible-value", result.stdout + result.stderr)

    def test_launcher_blocks_direct_variable_list_and_interactive_commands(self) -> None:
        variable_result = self.launcher("--", "variable", "list")
        self.assertNotEqual(variable_result.returncode, 0)
        self.assertIn("variable-names", variable_result.stderr)
        shell_result = self.launcher("--", "shell")
        self.assertNotEqual(shell_result.returncode, 0)
        self.assertIn("not supported", shell_result.stderr)

    def test_launcher_refuses_secret_values_and_2fa_in_arguments(self) -> None:
        variable_result = self.launcher(
            "--target-class",
            "non-production",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--",
            "variable",
            "set",
            "SECRET=value",
        )
        self.assertNotEqual(variable_result.returncode, 0)
        self.assertIn("requires --stdin", variable_result.stderr)
        template_result = self.launcher(
            "--target-class",
            "non-production",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--",
            "deploy",
            "--variable",
            "SECRET=value",
        )
        self.assertNotEqual(template_result.returncode, 0)
        self.assertIn("not accepted", template_result.stderr)
        two_factor_result = self.launcher(
            "--target-class",
            "account",
            "--confirm-write",
            "I_APPROVE_RAILWAY_WRITE",
            "--confirm-destructive",
            "I_APPROVE_RAILWAY_DESTRUCTIVE",
            "--",
            "project",
            "delete",
            "--2fa-code",
            "123456",
        )
        self.assertNotEqual(two_factor_result.returncode, 0)
        self.assertIn("2FA codes", two_factor_result.stderr)
        self.assertNotIn("123456", two_factor_result.stdout + two_factor_result.stderr)

    def test_launcher_requires_acknowledged_bounded_logs(self) -> None:
        self.install_valid_credentials()
        unconfirmed = self.launcher("--", "logs", "--lines", "10")
        self.assertNotEqual(unconfirmed.returncode, 0)
        self.assertIn("--confirm-sensitive-output", unconfirmed.stderr)
        unbounded = self.launcher(
            "--confirm-sensitive-output",
            "I_APPROVE_RAILWAY_SENSITIVE_READ",
            "--",
            "logs",
        )
        self.assertNotEqual(unbounded.returncode, 0)
        self.assertIn("must be bounded", unbounded.stderr)
        bounded = self.launcher(
            "--confirm-sensitive-output",
            "I_APPROVE_RAILWAY_SENSITIVE_READ",
            "--",
            "logs",
            "--lines",
            "10",
        )
        self.assertEqual(bounded.returncode, 0, bounded.stderr)

    def test_launcher_rejects_bad_credential_mode_and_type(self) -> None:
        self.install_valid_credentials()
        self.destination.chmod(0o600)
        mode_result = self.launcher("--", "whoami")
        self.assertNotEqual(mode_result.returncode, 0)
        self.assertIn("mode 0400", mode_result.stderr)
        self.destination.chmod(0o400)
        self.destination.chmod(0o600)
        self.destination.write_text(
            json.dumps({"token_type": "workspace", "token": SYNTHETIC_TOKEN}),
            encoding="utf-8",
        )
        self.destination.chmod(0o400)
        type_result = self.launcher("--", "whoami")
        self.assertNotEqual(type_result.returncode, 0)
        self.assertIn("account credentials", type_result.stderr)
        self.assertNotIn(SYNTHETIC_TOKEN, type_result.stdout + type_result.stderr)

    def test_launcher_refuses_token_in_arguments(self) -> None:
        self.install_valid_credentials()
        result = self.launcher("--", "status", SYNTHETIC_TOKEN)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must never appear", result.stderr)
        self.assertNotIn(SYNTHETIC_TOKEN, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
