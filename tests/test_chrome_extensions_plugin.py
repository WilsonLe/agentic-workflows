from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "chrome-extensions"
HELPER = PLUGIN / "skills" / "chrome-extensions" / "scripts" / "audit_extension.py"
spec = importlib.util.spec_from_file_location("audit_extension", HELPER)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExtensionAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("worker.js", "popup.html", "content.js", "content.css", "icon.png"):
            (self.root / name).write_text("fixture", encoding="utf-8")
        self.manifest = {
            "manifest_version": 3,
            "name": "Quick notes",
            "version": "1.0.0",
            "permissions": ["storage"],
            "background": {"service_worker": "worker.js", "type": "module"},
            "action": {"default_popup": "popup.html", "default_icon": {"16": "icon.png"}},
            "content_scripts": [{"matches": ["https://example.com/*"], "js": ["content.js"], "css": ["content.css"]}],
        }

    def audit(self, **updates: object) -> dict[str, object]:
        (self.root / "manifest.json").write_text(
            json.dumps(dict(self.manifest, **updates)), encoding="utf-8"
        )
        return module.audit(self.root)

    def test_valid_manifest_inventory_and_runtime_boundary(self) -> None:
        result = self.audit()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["permissions"]["permissions"], ["storage"])
        self.assertFalse(result["runtime_verified"])
        self.assertTrue(result["warnings"])

    def test_versions_match_chrome_numeric_constraints(self) -> None:
        for version in ("1", "0.0.1", "65535.0.0.1"):
            with self.subTest(version=version):
                self.assertEqual(self.audit(version=version)["errors"], [])
        for version in ("0", "0.0.0", "01", "1.65536", "1.0.0.0.1", "1.0-beta", None, True):
            with self.subTest(version=version):
                self.assertTrue(self.audit(version=version)["errors"])

    def test_malformed_json_and_duplicate_keys_are_rejected(self) -> None:
        for payload in ("{", '[]', '{"name":"a","name":"b"}', '{"value":NaN}', '{"value":Infinity}'):
            with self.subTest(payload=payload):
                (self.root / "manifest.json").write_text(payload, encoding="utf-8")
                self.assertTrue(module.audit(self.root)["errors"])
        (self.root / "manifest.json").unlink()
        self.assertTrue(module.audit(self.root)["errors"])

    def test_mv2_and_legacy_background_are_rejected(self) -> None:
        self.assertTrue(self.audit(manifest_version=2)["errors"])
        self.assertTrue(self.audit(manifest_version=3.0)["errors"])
        self.assertTrue(self.audit(background={"scripts": ["worker.js"]})["errors"])

    def test_missing_assets_are_rejected_across_surfaces(self) -> None:
        for updates in (
            {"background": {"service_worker": "missing.js"}},
            {"action": {"default_popup": "missing.html"}},
            {"side_panel": {"default_path": "missing.html"}},
            {"options_ui": {"page": "missing.html"}},
            {"options_page": "missing.html"},
            {"devtools_page": "missing.html"},
            {"icons": {"16": "missing.png"}},
            {"content_scripts": [{"js": ["missing.js"]}]},
        ):
            with self.subTest(updates=updates):
                self.assertTrue(self.audit(**updates)["errors"])

    def test_root_relative_assets_are_supported_but_escapes_are_rejected(self) -> None:
        self.assertEqual(self.audit(action={"default_popup": "/popup.html"})["errors"], [])
        for path in ("../outside.html", "https://example.com/popup.html", "C:\\popup.html", "bad\x00path"):
            with self.subTest(path=path):
                self.assertTrue(self.audit(action={"default_popup": path})["errors"])
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "external.html"
            external.write_text("outside", encoding="utf-8")
            (self.root / "escape.html").symlink_to(external)
            self.assertTrue(self.audit(action={"default_popup": "escape.html"})["errors"])
            (self.root / "manifest.json").unlink()
            (self.root / "manifest.json").symlink_to(external)
            self.assertTrue(module.audit(self.root)["errors"])

    def test_symlink_loops_return_structured_errors(self) -> None:
        (self.root / "loop.html").symlink_to("loop.html")
        self.assertTrue(self.audit(action={"default_popup": "loop.html"})["errors"])
        (self.root / "manifest.json").unlink()
        (self.root / "manifest.json").symlink_to("manifest.json")
        self.assertTrue(module.audit(self.root)["errors"])

    def test_malformed_sections_return_errors_without_crashing(self) -> None:
        for key in ("background", "action", "side_panel", "options_ui", "content_security_policy", "icons"):
            with self.subTest(key=key):
                self.assertTrue(self.audit(**{key: None})["errors"])
        for scripts in (None, [None], [{"js": "content.js"}], [{"css": [None]}]):
            self.assertTrue(self.audit(content_scripts=scripts)["errors"])

    def test_all_permission_fields_are_inventoried_and_shape_checked(self) -> None:
        for key in module.PERMISSION_FIELDS:
            for value in (None, "storage", [None], [""], ["storage", "storage"]):
                with self.subTest(key=key, value=value):
                    self.assertTrue(self.audit(**{key: value})["errors"])
        result = self.audit(
            optional_permissions=["scripting"], host_permissions=["<all_urls>"],
            optional_host_permissions=["https://example.com/*"],
        )
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["permissions"]["optional_permissions"], ["scripting"])
        self.assertTrue(any("broad host" in warning for warning in result["warnings"]))
        self.assertTrue(self.audit(permissions=["https://example.com/*"])["errors"])

    def test_csp_flags_only_selected_script_risks(self) -> None:
        for policy in (
            "script-src 'self' 'unsafe-eval'", "script-src 'self' 'unsafe-inline'",
            "script-src https://example.com", "default-src https:",
        ):
            with self.subTest(policy=policy):
                self.assertTrue(self.audit(content_security_policy={"extension_pages": policy})["errors"])
        result = self.audit(content_security_policy={
            "extension_pages": "default-src https:; script-src 'self' 'wasm-unsafe-eval'; object-src 'self'; connect-src https://example.com"
        })
        self.assertEqual(result["errors"], [])

    def test_cli_exit_codes_json_and_read_only_behavior(self) -> None:
        for version, expected_code in (("1.0", 0), ("1.0-beta", 1)):
            self.audit(version=version)
            before = {path.name: path.read_bytes() for path in self.root.iterdir()}
            result = subprocess.run(
                [sys.executable, str(HELPER), str(self.root)], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, expected_code)
            self.assertFalse(json.loads(result.stdout)["runtime_verified"])
            self.assertEqual(result.stderr, "")
            self.assertEqual(before, {path.name: path.read_bytes() for path in self.root.iterdir()})

    def test_claude_package_contains_identical_helper_and_assets(self) -> None:
        generated = ROOT / "generated" / "claude" / "plugins" / "chrome-extensions"
        for path in PLUGIN.rglob("*"):
            if path.is_file() and path.suffix != ".pyc" and ".codex-plugin" not in path.parts:
                with self.subTest(path=path.relative_to(PLUGIN)):
                    self.assertEqual(path.read_bytes(), (generated / path.relative_to(PLUGIN)).read_bytes())


if __name__ == "__main__":
    unittest.main()
