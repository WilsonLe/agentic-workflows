#!/usr/bin/env python3
"""Bounded, offline checks of an unpacked MV3 extension; never executes its code."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PERMISSION_FIELDS = (
    "permissions", "optional_permissions", "host_permissions", "optional_host_permissions"
)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number")


def audit(root: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    permissions: dict[str, list[str]] = {}
    result: dict[str, object] = {
        "scope": "offline-static-subset",
        "errors": errors,
        "warnings": warnings,
        "permissions": permissions,
        "runtime_verified": False,
    }
    try:
        root = root.resolve()
        manifest_path = root / "manifest.json"
        if not manifest_path.resolve().is_relative_to(root):
            raise ValueError("manifest outside extension")
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
            parse_constant=reject_nonfinite,
        )
    except (OSError, UnicodeError, ValueError, RuntimeError):
        errors.append("manifest.json must be readable, unique-key UTF-8 JSON inside the extension")
        return result
    if not isinstance(manifest, dict):
        errors.append("manifest.json must be an object")
        return result
    if not isinstance(manifest.get("manifest_version"), int) or manifest["manifest_version"] != 3:
        errors.append("manifest_version must be 3")
    if not isinstance(manifest.get("name"), str) or not manifest["name"].strip():
        errors.append("name must be a nonempty string")
    version = manifest.get("version")
    if (
        not isinstance(version, str)
        or re.fullmatch(r"(?:0|[1-9][0-9]{0,4})(?:\.(?:0|[1-9][0-9]{0,4})){0,3}", version) is None
        or any(int(part) > 65535 for part in version.split("."))
        or not any(int(part) for part in version.split("."))
    ):
        errors.append("version must have 1-4 components in 0..65535, no leading zeros, and not all zero")

    def asset(value: object, label: str) -> None:
        if not isinstance(value, str) or not value or ":" in value or "\\" in value:
            errors.append(f"{label} must reference a packaged file")
            return
        # Chrome permits a leading slash relative to the extension root.
        relative = Path(value.lstrip("/"))
        try:
            target = (root / relative).resolve()
        except (OSError, ValueError, RuntimeError):
            errors.append(f"{label} cannot resolve to a packaged file")
            return
        if ".." in relative.parts or not target.is_relative_to(root):
            errors.append(f"{label} must stay inside the unpacked extension")
        elif not target.is_file():
            errors.append(f"{label} references a missing packaged file")

    def section(key: str) -> dict[str, object]:
        value = manifest.get(key, {})
        if not isinstance(value, dict):
            errors.append(f"{key} must be an object")
            return {}
        return value

    def icons(value: object, label: str) -> None:
        if isinstance(value, str):
            asset(value, label)
        elif isinstance(value, dict):
            for size, path in value.items():
                asset(path, f"{label}.{size}")
        else:
            errors.append(f"{label} must be a file path or icon map")

    for field in PERMISSION_FIELDS:
        value = manifest.get(field, [])
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            errors.append(f"{field} must be an array of nonempty strings")
            continue
        permissions[field] = value
        if len(value) != len(set(value)):
            errors.append(f"{field} contains duplicates")
        if field in ("permissions", "optional_permissions"):
            if any("://" in item or item == "<all_urls>" for item in value):
                errors.append(f"{field} contains hosts; use the corresponding host_permissions field")
        if field in ("host_permissions", "optional_host_permissions"):
            if any(item in ("<all_urls>", "*://*/*", "https://*/*", "http://*/*") for item in value):
                warnings.append(f"{field} requests broad host access; justify or narrow it")

    background = section("background")
    if any(key in background for key in ("scripts", "page", "persistent")):
        errors.append("background has legacy MV2 fields; use service_worker")
    if "service_worker" in background:
        asset(background["service_worker"], "background.service_worker")
    for key, field in (
        ("action", "default_popup"), ("side_panel", "default_path"),
        ("options_ui", "page"),
    ):
        value = section(key)
        if field in value:
            asset(value[field], f"{key}.{field}")
        if key == "action" and "default_icon" in value:
            icons(value["default_icon"], "action.default_icon")
    for key in ("options_page", "devtools_page"):
        if key in manifest:
            asset(manifest[key], key)
    if "icons" in manifest:
        if not isinstance(manifest["icons"], dict):
            errors.append("icons must be an object")
        else:
            icons(manifest["icons"], "icons")
    scripts = manifest.get("content_scripts", [])
    if not isinstance(scripts, list):
        errors.append("content_scripts must be an array")
    else:
        for index, script in enumerate(scripts):
            if not isinstance(script, dict):
                errors.append(f"content_scripts[{index}] must be an object")
                continue
            for key in ("js", "css"):
                paths = script.get(key, [])
                if not isinstance(paths, list):
                    errors.append(f"content_scripts[{index}].{key} must be an array")
                    continue
                for position, path in enumerate(paths):
                    asset(path, f"content_scripts[{index}].{key}[{position}]")
    csp = section("content_security_policy")
    if "extension_pages" in csp:
        policy = csp["extension_pages"]
        if not isinstance(policy, str):
            errors.append("content_security_policy.extension_pages must be a string")
        else:
            directives: dict[str, list[str]] = {}
            for directive in policy.split(";"):
                tokens = directive.split()
                if tokens:
                    directives.setdefault(tokens[0].lower(), tokens[1:])
            # An explicit script-src overrides default-src for scripts.
            script_policies = [directives.get("script-src", directives.get("default-src", []))]
            if "script-src-elem" in directives:
                script_policies.append(directives["script-src-elem"])
            for sources in script_policies:
                if any(token in ("'unsafe-eval'", "'unsafe-inline'") for token in sources):
                    errors.append("extension-page CSP permits unsafe script execution")
                if any("://" in token or token in ("http:", "https:", "*") for token in sources):
                    errors.append("extension-page CSP permits remote script sources")
    if not (root / "CHROMEWEBSTORE.md").is_file():
        warnings.append("No CHROMEWEBSTORE.md in unpacked directory; reconcile the project-root record separately")
    warnings.append("Static subset only: load in Chrome, review code/permissions/privacy, and test runtime behavior")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extension_directory", type=Path)
    arguments = parser.parse_args()
    result = audit(arguments.extension_directory)
    print(json.dumps(result, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
