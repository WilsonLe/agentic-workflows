#!/usr/bin/env python3
"""Install the consolidated Claude package into isolated temporary configuration."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from plugin_catalog import claude_marketplace_payload, claude_package_path, load_catalog

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-root", type=Path, help="smoke test a staged portable distribution")
    args = parser.parse_args()
    catalog = load_catalog()
    package = next(package for package in catalog["packages"] if package["name"] == "agentic-workflows")
    expected_skills = {skill["name"] for skill in package["skills"] if "claude-code" in skill["harnesses"]}
    generated = claude_package_path(package, args.build_root or ROOT).resolve()
    expected_version = json.loads((generated / ".claude-plugin" / "plugin.json").read_text())["version"]
    with tempfile.TemporaryDirectory(prefix="agentic-claude-smoke-") as scratch:
        config = Path(scratch) / "config"
        marketplace_root = ROOT
        if args.build_root is not None:
            marketplace_root = Path(scratch) / "marketplace"
            shutil.copytree(generated, claude_package_path(package, marketplace_root))
            manifest = marketplace_root / ".claude-plugin" / "marketplace.json"
            manifest.parent.mkdir()
            manifest.write_text(json.dumps(claude_marketplace_payload(catalog)), encoding="utf-8")
        environment = dict(
            os.environ,
            CLAUDE_CONFIG_DIR=str(config),
            CLAUDE_CODE_PLUGIN_CACHE_DIR=str(config / "plugins"),
            CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
        )
        commands = (
            ["claude", "plugin", "marketplace", "add", "./"],
            ["claude", "plugin", "install", "agentic-workflows@agentic-workflows"],
            ["claude", "plugin", "list", "--json"],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=marketplace_root,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            if command[-1] != "--json":
                continue
            plugins = json.loads(result.stdout)
            if len(plugins) != 1 or plugins[0]["id"] != "agentic-workflows@agentic-workflows":
                raise RuntimeError("only the consolidated plugin should be installed")
            plugin = plugins[0]
            if not plugin["enabled"] or plugin["version"] != expected_version:
                raise RuntimeError("consolidated plugin is disabled or has an unexpected version")
            installed = Path(plugin["installPath"])
            installed.resolve().relative_to(config.resolve())
            for root in {installed, Path(plugin.get("readFromFolder", installed))}:
                actual_skills = {path.name for path in (root / "skills").iterdir() if path.is_dir()}
                if actual_skills != expected_skills:
                    raise RuntimeError("installed consolidated skill inventory differs from catalog")
                for name in expected_skills:
                    if (root / "skills" / name / "SKILL.md").read_bytes() != (generated / "skills" / name / "SKILL.md").read_bytes():
                        raise RuntimeError(f"installed skill differs: {name}")
                for relative in (
                    "CAPABILITIES.md",
                    "skills/chrome-extensions/scripts/audit_extension.py",
                    "skills/music-composition/scripts/synthesize_score.py",
                ):
                    asset = Path(relative)
                    if (root / asset).read_bytes() != (generated / asset).read_bytes():
                        raise RuntimeError(f"installed capability asset differs: {relative}")
        details = subprocess.run(
            ["claude", "plugin", "details", "agentic-workflows@agentic-workflows"],
            cwd=marketplace_root,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if not details.startswith(f"agentic-workflows {expected_version}\n"):
            raise RuntimeError("Claude Code reports an unexpected plugin version")
        inventory = next(line for line in details.splitlines() if line.strip().startswith("Skills ("))
        listed = {name.strip() for name in inventory.split(")", 1)[1].split(",")}
        if listed != expected_skills:
            raise RuntimeError("Claude Code skill inventory differs from catalog")
    print("Claude package install and discovery passed.")


if __name__ == "__main__":
    main()
