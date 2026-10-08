#!/usr/bin/env python3
"""Install the consolidated Claude package into isolated temporary configuration."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from plugin_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    package = next(package for package in load_catalog()["packages"] if package["name"] == "agentic-workflows")
    expected_skills = {skill["name"] for skill in package["skills"] if "claude-code" in skill["harnesses"]}
    generated = ROOT / "generated" / "claude" / "plugins" / package["name"]
    expected_version = json.loads((generated / ".claude-plugin" / "plugin.json").read_text())["version"]
    with tempfile.TemporaryDirectory(prefix="agentic-claude-smoke-") as config:
        environment = dict(os.environ, CLAUDE_CONFIG_DIR=config)
        commands = (
            ["claude", "plugin", "marketplace", "add", "./"],
            ["claude", "plugin", "install", "agentic-workflows@agentic-workflows"],
            ["claude", "plugin", "list", "--json"],
        )
        for command in commands:
            result = subprocess.run(
                command,
                cwd=ROOT,
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
            installed.resolve().relative_to(Path(config).resolve())
            for root in {installed, Path(plugin.get("readFromFolder", installed))}:
                actual_skills = {path.name for path in (root / "skills").iterdir() if path.is_dir()}
                if actual_skills != expected_skills:
                    raise RuntimeError("installed consolidated skill inventory differs from catalog")
                for name in expected_skills:
                    if (root / "skills" / name / "SKILL.md").read_bytes() != (generated / "skills" / name / "SKILL.md").read_bytes():
                        raise RuntimeError(f"installed skill differs: {name}")
                helper = Path("skills/chrome-extensions/scripts/audit_extension.py")
                if (root / helper).read_bytes() != (generated / helper).read_bytes():
                    raise RuntimeError("installed Chrome extension audit helper differs")
    print("Claude package install and discovery passed.")


if __name__ == "__main__":
    main()
