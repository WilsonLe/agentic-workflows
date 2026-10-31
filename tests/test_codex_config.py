from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/agentic-workflows/skills/agentic-workflows-config-transfer"
HELPER = SKILL / "scripts/codex_config.py"
spec = importlib.util.spec_from_file_location("codex_config", HELPER)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

EXISTING = b"""# keep this comment\nmodel = "chosen-model"\ndefault_permissions = ":workspace"\n[permissions.custom.filesystem]\n":workspace_roots" = "write"\n[apps._default]\nenabled = false # explicit prior default\n[apps.example]\nenabled = false\n[apps.example.tools.send]\napproval_mode = "prompt"\n[computer_use.macos.bundle_ids]\n"example.blocked" = "deny"\n[mcp_servers.example]\nurl = "https://example.invalid/mcp"\nbearer_token_env_var = "SYNTHETIC_TOKEN"\n[mcp_servers.example.tools.write]\napproval_mode = "prompt"\n[plugins."example@local".mcp_servers.api]\nenabled = false\n"""


class CodexConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve() / "codex-home"
        self.home.mkdir()
        self.target = self.home / "config.toml"

    def activate(self, **kwargs):
        return config.apply(self.home, [], [], preview=False, **kwargs)

    def test_asset_is_portable_and_uses_one_permission_selector(self):
        preset = tomllib.loads(config.PRESET.read_text())
        self.assertEqual(preset["approval_policy"], "never")
        self.assertEqual(preset["sandbox_mode"], "danger-full-access")
        self.assertEqual(preset["web_search"], "live")
        self.assertEqual(
            preset["apps"]["_default"]["default_tools_approval_mode"], "approve"
        )
        self.assertNotIn("default_permissions", preset)
        self.assertNotIn("mcp_servers", preset)
        self.assertNotIn("plugins", preset)
        self.assertNotIn("/Users/", config.PRESET.read_text())

    def test_preview_does_not_write_or_leak_config(self):
        self.target.write_bytes(EXISTING)
        result = config.apply(self.home, [], [], preview=True)
        self.assertEqual(self.target.read_bytes(), EXISTING)
        self.assertEqual(list(self.home.iterdir()), [self.target])
        self.assertNotIn("chosen-model", json.dumps(result))
        self.assertTrue(result["removes_default_permissions"])

    def test_apply_preserves_comments_settings_auth_and_repeatability(self):
        self.target.write_bytes(EXISTING)
        auth = self.home / "auth.json"
        auth.write_bytes(b'{"synthetic":"do not touch"}')
        result = self.activate()
        applied = self.target.read_bytes()
        parsed = tomllib.loads(applied.decode())
        self.assertIn(b"# keep this comment", applied)
        self.assertIn(b"# explicit prior default", applied)
        self.assertEqual(parsed["model"], "chosen-model")
        self.assertNotIn("default_permissions", parsed)
        self.assertIn("custom", parsed["permissions"])
        self.assertFalse(parsed["apps"]["example"]["enabled"])
        self.assertEqual(
            parsed["apps"]["example"]["tools"]["send"]["approval_mode"], "prompt"
        )
        self.assertEqual(
            parsed["computer_use"]["macos"]["bundle_ids"]["example.blocked"], "deny"
        )
        self.assertEqual(auth.read_bytes(), b'{"synthetic":"do not touch"}')
        self.assertEqual(self.activate(), {"status": "unchanged"})
        self.assertEqual(
            len(list(self.home.glob("agentic-workflows-config-backup-*"))), 1
        )
        self.assertEqual(
            (Path(result["backup"]) / "config.toml").read_bytes(), EXISTING
        )

    def test_named_and_all_server_defaults_preserve_connections_and_overrides(self):
        for all_servers in (False, True):
            with self.subTest(all_servers=all_servers):
                data = config.merged(
                    EXISTING,
                    ["example"],
                    [["example@local", "api"]],
                    all_servers=all_servers,
                )
                parsed = tomllib.loads(data.decode())
                server = parsed["mcp_servers"]["example"]
                self.assertEqual(server["default_tools_approval_mode"], "approve")
                self.assertEqual(server["url"], "https://example.invalid/mcp")
                self.assertEqual(server["tools"]["write"]["approval_mode"], "prompt")
                plugin = parsed["plugins"]["example@local"]["mcp_servers"]["api"]
                self.assertFalse(plugin["enabled"])
                self.assertEqual(plugin["default_tools_approval_mode"], "approve")

    def test_missing_server_or_invalid_toml_does_not_write(self):
        for original, servers in (
            (EXISTING, ["missing"]),
            (b"broken = [", []),
            (b"apps = 3", []),
        ):
            self.target.write_bytes(original)
            with self.assertRaises(config.ConfigError):
                config.apply(self.home, servers, [], preview=False)
            self.assertEqual(self.target.read_bytes(), original)
            self.assertFalse(list(self.home.glob("agentic-workflows-config-backup-*")))

    def test_restore_exact_bytes_and_original_mode(self):
        self.target.write_bytes(EXISTING.replace(b"\n", b"\r\n"))
        self.target.chmod(0o640)
        original = self.target.read_bytes()
        backup = Path(self.activate()["backup"])
        config.restore(self.home, backup)
        self.assertEqual(self.target.read_bytes(), original)
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o640)
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o700)
            self.assertEqual(
                stat.S_IMODE((backup / "config.toml").stat().st_mode), 0o600
            )
        self.assertTrue(backup.exists())

    def test_restore_new_config_removes_only_created_config(self):
        backup = Path(self.activate()["backup"])
        config.restore(self.home, backup)
        self.assertFalse(self.target.exists())
        self.assertTrue(backup.exists())

    def test_restore_refuses_later_edit_or_corrupt_backup(self):
        self.target.write_bytes(EXISTING)
        backup = Path(self.activate()["backup"])
        self.target.write_bytes(self.target.read_bytes() + b"\n# later edit\n")
        changed = self.target.read_bytes()
        with self.assertRaises(config.ConfigError):
            config.restore(self.home, backup)
        self.assertEqual(self.target.read_bytes(), changed)
        (backup / "config.toml").write_bytes(b"model = 'corrupted'")
        with self.assertRaises(config.ConfigError):
            config.restore(self.home, backup)
        self.assertEqual(self.target.read_bytes(), changed)

    def test_symlink_and_git_destinations_are_rejected(self):
        other = Path(self.temporary.name) / "other"
        other.mkdir()
        (other / "config.toml").write_bytes(EXISTING)
        self.target.symlink_to(other / "config.toml")
        with self.assertRaises(config.ConfigError):
            self.activate()
        self.target.unlink()
        (self.home / ".git").write_text("gitdir: elsewhere")
        with self.assertRaises(config.ConfigError):
            self.activate()

    def test_lock_and_failed_replace_preserve_original(self):
        self.target.write_bytes(EXISTING)
        lock = self.home / ".agentic-workflows-config.lock"
        lock.touch()
        with self.assertRaises(config.ConfigError):
            self.activate()
        lock.unlink()
        with patch.object(
            config.os, "replace", side_effect=OSError("synthetic failure")
        ):
            with self.assertRaises(OSError):
                self.activate()
        self.assertEqual(self.target.read_bytes(), EXISTING)
        self.assertFalse(lock.exists())

    def test_failed_activation_write_retains_usable_backup(self):
        self.target.write_bytes(EXISTING)
        original_replace = config.os.replace

        def fail_target(source, destination):
            if destination == self.target:
                raise OSError("synthetic target write failure")
            original_replace(source, destination)

        with patch.object(config.os, "replace", side_effect=fail_target):
            with self.assertRaises(OSError):
                self.activate()
        self.assertEqual(self.target.read_bytes(), EXISTING)
        backups = list(self.home.glob("agentic-workflows-config-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "config.toml").read_bytes(), EXISTING)
        self.assertTrue((backups[0] / "receipt.json").is_file())

    def test_invalid_receipt_is_rejected_without_traceback_or_write(self):
        backup = Path(self.activate()["backup"])
        applied = self.target.read_bytes()
        receipt_path = backup / "receipt.json"
        receipt = json.loads(receipt_path.read_bytes())
        del receipt["after_sha256"]
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaises(config.ConfigError):
            config.restore(self.home, backup)
        self.assertEqual(self.target.read_bytes(), applied)

    def test_cli_roundtrip_respects_codex_home_and_sanitizes_errors(self):
        env = {**os.environ, "CODEX_HOME": str(self.home)}
        command = [sys.executable, str(HELPER)]
        applied = subprocess.run(
            command + ["apply", "--all-configured-servers"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        result = json.loads(applied.stdout)
        subprocess.run(
            command + ["restore", result["backup"]],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertFalse(self.target.exists())
        self.target.write_bytes(b"private_synthetic = secret is invalid")
        failed = subprocess.run(
            command + ["apply"], env=env, capture_output=True, text=True
        )
        self.assertEqual(failed.returncode, 1)
        self.assertNotIn("private_synthetic", failed.stderr)


if __name__ == "__main__":
    unittest.main()
