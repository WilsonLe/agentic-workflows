from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from contextlib import ExitStack
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


class NativeBrowserConfigurationTests(unittest.TestCase):
    CONTEXT = '["old-app-instance","synthetic-account","synthetic-user"]'
    VERSION = "26.1023.50603"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "codex-home"
        self.home.mkdir()
        self.target = self.home / "config.toml"
        self.target.write_bytes(EXISTING)
        self.app = self.root / "ChatGPT.app"
        self.cache = self.home / "plugins/cache/openai-bundled/unified-computer-use"
        self.resources = self.app / "Contents/Resources/cua_node"
        self.make_runtime(self.VERSION)
        self.mocks = ExitStack()
        self.addCleanup(self.mocks.close)
        self.mocks.enter_context(patch.object(config.sys, "platform", "darwin"))
        self.mocks.enter_context(patch.object(config, "_verify_native_binary"))
        self.discover_context = config._desktop_context
        self.context_patch = patch.object(
            config, "_desktop_context", return_value=self.CONTEXT
        )
        self.context = self.mocks.enter_context(self.context_patch)
        self.mocks.enter_context(
            patch.object(
                config,
                "_native_command",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout="usage", stderr=""
                ),
            )
        )

    def make_runtime(self, version):
        info = self.app / "Contents/Info.plist"
        info.parent.mkdir(parents=True, exist_ok=True)
        info.write_bytes(
            plistlib.dumps(
                {
                    "CFBundleIdentifier": "com.openai.codex",
                    "CFBundleShortVersionString": version,
                }
            )
        )
        manifest = self.cache / version / ".mcp.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        guard = manifest.with_name("require-browser-access.mjs")
        guard.write_text('process.env.BROWSER_USE_ACCESS_EXECUTOR_ID ??= "";')
        node = self.resources / "bin/node"
        module = self.resources / "lib/node_modules/@oai/cua-repl/bin/cua-repl.mjs"
        for path in (
            node,
            module,
            self.resources / "bin/node_repl",
            self.app / "Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex",
            self.app / "Contents/MacOS/ChatGPT",
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        self.native = {
            "command": str(node),
            "args": ["--import", guard.as_uri(), str(module)],
            "enabled": True,
            "enabled_tools": ["js", "js_reset", "turn_ended"],
            "omit_tools_from": ["code_mode", "deferred"],
            "startup_timeout_sec": 120,
            "env_vars": list(config.CONTEXT_FIELDS[:3]),
            "env": {
                "CODEX_HOME": str(self.home),
                "CUA_REPL_NODE_REPL_PATH": str(self.resources / "bin/node_repl"),
                "BROWSER_USE_CODEX_APP_VERSION": version,
            },
        }
        manifest.write_text(json.dumps({"mcpServers": {"cua_repl": self.native}}))
        return manifest

    def apply(self, preview=False):
        return config.apply(self.home, [], [], preview=preview, browser_app=self.app)

    def test_preview_activation_repeat_and_exact_restore_without_auth_reads(self):
        auth = self.home / "auth.json"
        auth.write_text('{"secret":"SYNTHETIC_LOGIN_TOKEN"}')
        read_bytes = Path.read_bytes

        def guarded_read(path):
            if path == auth:
                self.fail("browser setup must not read the login credential store")
            return read_bytes(path)

        with patch.object(Path, "read_bytes", guarded_read):
            preview = self.apply(preview=True)
            self.assertIn("mcp_servers.cua_repl", preview["changes"])
            self.assertNotIn("synthetic-account", json.dumps(preview))
            self.assertEqual(self.target.read_bytes(), EXISTING)
            self.assertFalse(list(self.home.glob("agentic-workflows-config-backup-*")))
            result = self.apply()
            table = tomllib.loads(self.target.read_text())["mcp_servers"]["cua_repl"]
            self.assertTrue(table["required"])
            self.assertEqual(table["omit_tools_from"], [])
            self.assertEqual(table["env"], {config.DESKTOP_CONTEXT: self.CONTEXT})
            self.assertIn("browser-mcp", table["args"])
            self.assertEqual(table["command"], os.path.abspath(sys.executable))
            self.assertEqual(table["args"][0], str(HELPER))
            self.assertNotIn("--script", table["args"])
            self.assertEqual(self.apply(), {"status": "unchanged"})
            config.restore(self.home, Path(result["backup"]))
            self.assertEqual(self.target.read_bytes(), EXISTING)

    def test_existing_native_transport_migrates_and_preserves_restrictions(self):
        doc = config.tomlkit.parse(EXISTING.decode())
        native = json.loads(json.dumps(self.native))
        native["env"]["BROWSER_USE_DISABLE_AMBIENT_NETWORK"] = "1"
        native["env"]["BROWSER_USE_ACCESS_EXECUTOR_ID"] = self.CONTEXT
        native["tools"] = {"js": {"approval_mode": "prompt"}}
        doc["mcp_servers"]["cua_repl"] = native
        self.target.write_text(config.tomlkit.dumps(doc))
        self.apply()
        table = tomllib.loads(self.target.read_text())["mcp_servers"]["cua_repl"]
        self.assertEqual(table["env"]["BROWSER_USE_DISABLE_AMBIENT_NETWORK"], "1")
        self.assertNotIn("BROWSER_USE_ACCESS_EXECUTOR_ID", table["env"])
        self.assertNotIn("BROWSER_USE_CODEX_APP_VERSION", table["env"])
        self.assertEqual(table["tools"]["js"]["approval_mode"], "prompt")
        self.assertEqual(self.apply(), {"status": "unchanged"})

    def test_reactivation_refreshes_context_and_keeps_custom_comments(self):
        self.apply()
        doc = config.tomlkit.parse(self.target.read_text())
        env = doc["mcp_servers"]["cua_repl"]["env"]
        env.add(config.tomlkit.comment("retain this browser restriction"))
        env["BROWSER_USE_DISABLE_AMBIENT_NETWORK"] = "1"
        self.target.write_text(config.tomlkit.dumps(doc))
        self.context.return_value = '["new-instance","new-account","new-user"]'
        self.apply()
        self.assertIn("# retain this browser restriction", self.target.read_text())
        table = tomllib.loads(self.target.read_text())["mcp_servers"]["cua_repl"]
        self.assertEqual(
            table["env"][config.DESKTOP_CONTEXT], self.context.return_value
        )
        self.assertEqual(table["env"]["BROWSER_USE_DISABLE_AMBIENT_NETWORK"], "1")

    def test_missing_ambiguous_or_invalid_sources_cannot_mutate_config(self):
        for failure in (
            config.ConfigError("native context unavailable"),
            config.ConfigError("ambiguous native contexts"),
        ):
            with self.subTest(failure=str(failure)):
                self.context.side_effect = failure
                with self.assertRaises(config.ConfigError):
                    self.apply()
                self.assertEqual(self.target.read_bytes(), EXISTING)
                self.assertFalse(
                    list(self.home.glob("agentic-workflows-config-backup-*"))
                )

    def test_custom_or_disabled_browser_definitions_are_not_overwritten(self):
        for extra in (
            '[mcp_servers.cua_repl]\nurl="https://custom.invalid/mcp"\n',
            '[plugins."unified-computer-use@openai-bundled"]\nenabled=false\n',
            '[plugins."unified-computer-use@openai-bundled".mcp_servers.cua_repl]\ndisabled_tools=["js"]\n',
        ):
            with self.subTest(extra=extra):
                original = EXISTING + extra.encode()
                self.target.write_bytes(original)
                with self.assertRaises(config.ConfigError):
                    self.apply()
                self.assertEqual(self.target.read_bytes(), original)

    def test_native_guard_and_binary_checks_fail_before_writing(self):
        manifest = self.cache / self.VERSION / ".mcp.json"
        native = json.loads(manifest.read_text())
        native["mcpServers"]["cua_repl"]["args"][1] = "file:///untrusted/guard.mjs"
        manifest.write_text(json.dumps(native))
        with self.assertRaises(config.ConfigError):
            self.apply()
        self.assertEqual(self.target.read_bytes(), EXISTING)
        self.make_runtime(self.VERSION)
        with patch.object(
            config,
            "_verify_native_binary",
            side_effect=config.ConfigError("invalid signature"),
        ):
            with self.assertRaises(config.ConfigError):
                self.apply()
        self.assertEqual(self.target.read_bytes(), EXISTING)

    def test_missing_native_runtime_files_reject_preview_and_apply_without_backup(self):
        for path in (
            self.cache / self.VERSION / "require-browser-access.mjs",
            self.resources / "lib/node_modules/@oai/cua-repl/bin/cua-repl.mjs",
            self.resources / "bin/node_repl",
        ):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.unlink()
                for preview in (True, False):
                    with self.assertRaisesRegex(config.ConfigError, "file is missing"):
                        self.apply(preview=preview)
                    self.assertEqual(self.target.read_bytes(), EXISTING)
                    self.assertFalse(
                        list(self.home.glob("agentic-workflows-config-backup-*"))
                    )
                path.write_bytes(original)

    def test_conflicting_policy_layers_fail_without_weakening_restrictions(self):
        for policy, existing in (
            ({"disabled_tools": ["js"]}, {"disabled_tools": []}),
            ({"disabled_tools": ["js_reset"]}, {"disabled_tools": []}),
            ({"enabled_tools": ["js_reset"]}, {"enabled_tools": ["js", "js_reset"]}),
            (
                {"default_tools_approval_mode": "prompt"},
                {"default_tools_approval_mode": "approve"},
            ),
            (
                {"tools": {"js": {"approval_mode": "prompt"}}},
                {"tools": {"js": {"approval_mode": "approve"}}},
            ),
        ):
            with self.subTest(policy=policy):
                document = config.tomlkit.parse(EXISTING.decode())
                document.setdefault("plugins", {})[config.BROWSER_PLUGIN] = {
                    "mcp_servers": {"cua_repl": policy}
                }
                document["mcp_servers"]["cua_repl"] = {**self.native, **existing}
                before = config.tomlkit.dumps(document).encode()
                self.target.write_bytes(before)
                for preview in (True, False):
                    with self.assertRaisesRegex(
                        config.ConfigError, "conflicting native browser policies"
                    ):
                        self.apply(preview=preview)
                    self.assertEqual(self.target.read_bytes(), before)
                    self.assertFalse(
                        list(self.home.glob("agentic-workflows-config-backup-*"))
                    )

    def test_disjoint_per_tool_policies_are_preserved_across_layers(self):
        document = config.tomlkit.parse(EXISTING.decode())
        document.setdefault("plugins", {})[config.BROWSER_PLUGIN] = {
            "mcp_servers": {"cua_repl": {"tools": {"js": {"approval_mode": "prompt"}}}}
        }
        document["mcp_servers"]["cua_repl"] = {
            **self.native,
            "tools": {"js_reset": {"approval_mode": "prompt"}},
        }
        self.target.write_text(config.tomlkit.dumps(document))
        self.apply()
        result = tomllib.loads(self.target.read_text())["mcp_servers"]["cua_repl"]
        self.assertEqual(
            result["tools"],
            {
                "js": {"approval_mode": "prompt"},
                "js_reset": {"approval_mode": "prompt"},
            },
        )
        self.assertEqual(self.apply(), {"status": "unchanged"})

    def test_unavailable_python_launcher_cannot_write_config(self):
        with patch.object(
            config, "_native_command", side_effect=config.ConfigError("missing runtime")
        ):
            with self.assertRaisesRegex(config.ConfigError, "Python environment"):
                self.apply()
        self.assertEqual(self.target.read_bytes(), EXISTING)
        self.assertFalse(list(self.home.glob("agentic-workflows-config-backup-*")))

    def test_runtime_requires_native_broker_metadata(self):
        self.apply()
        with patch.dict(config.os.environ, {}, clear=True), patch.object(
            config.os, "execve"
        ) as execute:
            with self.assertRaisesRegex(config.ConfigError, "connected desktop host"):
                config.browser_mcp(self.app, self.home)
        execute.assert_not_called()

    def test_runtime_refreshes_app_instance_without_desktop_process_or_login_reads(
        self
    ):
        self.apply()
        self.make_runtime("26.1027.51404")
        self.context.side_effect = AssertionError(
            "runtime must not require a desktop warm-up"
        )
        with patch.dict(
            config.os.environ,
            {
                "BROWSER_USE_ACCESS_EXECUTOR_ID": '["restarted-app","native-browser-plugin"]',
                "BROWSER_USE_ACCESS_PIPE_PATH": "synthetic-current-pipe",
                "BROWSER_USE_ACCESS_VERIFYING_IDENTITY": "synthetic-public-key",
            },
        ), patch.object(config.os, "execve") as execute:
            config.browser_mcp(self.app, self.home)
        command, arguments, env = execute.call_args.args
        self.assertEqual(command, self.native["command"])
        self.assertEqual(arguments[1:], self.native["args"])
        self.assertEqual(env["BROWSER_USE_CODEX_APP_VERSION"], "26.1027.51404")
        self.assertEqual(
            env["BROWSER_USE_ACCESS_EXECUTOR_ID"],
            '["restarted-app","synthetic-account","synthetic-user"]',
        )
        self.assertNotIn(config.DESKTOP_CONTEXT, env)
        self.assertIn("require-browser-access.mjs", arguments[2])

    def test_invalid_or_foreign_native_contexts_fail_closed(self):
        for incoming in (
            "",
            "not-json",
            '["host","wrong-marker"]',
            '["host","different-account","different-user"]',
        ):
            with self.subTest(incoming=incoming):
                with self.assertRaises(config.ConfigError):
                    config._rebind_browser_context(self.CONTEXT, incoming)
        native = '["current","synthetic-account","synthetic-user"]'
        self.assertEqual(config._rebind_browser_context(self.CONTEXT, native), native)

    def test_discovery_requires_current_signed_app_process_chain_and_unique_scope(self):
        resources = self.app / "Contents/Resources"
        paths = {
            100: resources / "cua_node/bin/node_repl",
            101: resources / "cua_node/bin/node_repl",
            200: resources / "codex-cli/CodexCLI.app/Contents/MacOS/codex",
            300: self.app / "Contents/MacOS/ChatGPT",
        }
        metadata = {
            "BROWSER_USE_ACCESS_EXECUTOR_ID": self.CONTEXT,
            "BROWSER_USE_ACCESS_PIPE_PATH": "synthetic-pipe",
            "BROWSER_USE_ACCESS_VERIFYING_IDENTITY": "synthetic-key",
            "BROWSER_USE_CODEX_APP_VERSION": self.VERSION,
            "CODEX_HOME": str(self.home),
        }
        environments = {
            100: dict(metadata),
            101: dict(metadata),
            200: {
                **metadata,
                "BROWSER_USE_ACCESS_EXECUTOR_ID": '["old-app-instance","native-browser-plugin"]',
            },
        }

        def command(args):
            value = (
                f"100 200 {os.getuid()}\n101 200 {os.getuid()}\n200 300 {os.getuid()}\n300 1 {os.getuid()}\n"
                if "-axo" in args
                else "codex app-server --analytics-default-enabled"
            )
            return subprocess.CompletedProcess(args, 0, stdout=value, stderr="")

        with patch.object(config, "_native_command", side_effect=command), patch.object(
            config, "_native_process_path", side_effect=lambda pid: paths.get(pid)
        ), patch.object(
            config, "_native_environment", side_effect=lambda pid: environments[pid]
        ):
            self.assertEqual(
                self.discover_context(self.app, self.home, self.VERSION), self.CONTEXT
            )
            environments[101][
                "BROWSER_USE_ACCESS_EXECUTOR_ID"
            ] = '["old-app-instance","other-account","other-user"]'
            with self.assertRaises(config.ConfigError):
                self.discover_context(self.app, self.home, self.VERSION)
            paths[300] = Path("/untrusted/ChatGPT")
            with self.assertRaises(config.ConfigError):
                self.discover_context(self.app, self.home, self.VERSION)

    def test_environment_inspection_returns_only_the_browser_allowlist(self):
        raw = (
            "node_repl SYNTHETIC_LOGIN_TOKEN=SYNTHETIC_TOKEN_VALUE_NOT_FORWARDED BROWSER_USE_ACCESS_EXECUTOR_ID="
            + self.CONTEXT
            + " CODEX_HOME="
            + str(self.home)
        )
        with patch.object(
            config,
            "_native_command",
            return_value=subprocess.CompletedProcess([], 0, stdout=raw),
        ):
            values = config._native_environment(100)
        self.assertEqual(values["BROWSER_USE_ACCESS_EXECUTOR_ID"], self.CONTEXT)
        self.assertNotIn("SYNTHETIC_LOGIN_TOKEN", values)
        self.assertNotIn("SYNTHETIC_TOKEN_VALUE_NOT_FORWARDED", json.dumps(values))


if __name__ == "__main__":
    unittest.main()
