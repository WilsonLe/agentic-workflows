#!/usr/bin/env python3
"""Validate repository plugin structure and Railway central-integration invariants."""

from __future__ import annotations

import json
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
STANDALONE = ROOT / "plugins" / "railway-account"
CENTRAL = ROOT / "plugins" / "amsoft-agentic-workflows"
IMAGE = ROOT / "plugins" / "image-editing"
STANDALONE_SKILL = STANDALONE / "skills" / "railway-account-operations"
CENTRAL_SKILL = CENTRAL / "skills" / "amsoft-railway-account-operations"
IMAGE_SKILL = IMAGE / "skills" / "food-image-editing"
CENTRAL_IMAGE_SKILL = CENTRAL / "skills" / "food-image-editing"
TRANSFER_SKILL = CENTRAL / "skills" / "amsoft-agentic-workflows-config-transfer"
REGISTRY = (
    CENTRAL
    / "skills"
    / "amsoft-agentic-workflows"
    / "references"
    / "plugin-registry.md"
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def fail(message: str) -> None:
    print(f"Validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {error}")


def validate_manifest(plugin: Path) -> dict[str, object]:
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    payload = load_json(manifest_path)
    if not isinstance(payload, dict):
        fail(f"{manifest_path.relative_to(ROOT)} must contain an object")
    if payload.get("name") != plugin.name:
        fail(f"{manifest_path.relative_to(ROOT)} name must match its directory")
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        fail(f"{manifest_path.relative_to(ROOT)} is missing interface metadata")
    prompts = interface.get("defaultPrompt")
    if isinstance(prompts, str):
        prompts = [prompts]
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        fail(f"{manifest_path.relative_to(ROOT)} must provide one to three prompts")
    if not all(isinstance(prompt, str) and len(prompt) <= 128 for prompt in prompts):
        fail(f"{manifest_path.relative_to(ROOT)} has an invalid default prompt")
    return payload


def frontmatter_name(skill: Path) -> str:
    skill_file = skill / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        fail(f"{skill_file.relative_to(ROOT)} has invalid frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"}:
        fail(f"{skill_file.relative_to(ROOT)} frontmatter must contain only name and description")
    if fields["name"] != skill.name:
        fail(f"{skill_file.relative_to(ROOT)} name must match its directory")
    return fields["name"]


def validate_links(directory: Path) -> None:
    for markdown in directory.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            if (
                target.startswith(("http://", "https://", "#", "mailto:"))
                or "://" in target
            ):
                continue
            path_text = target.split("#", 1)[0]
            if path_text and not (markdown.parent / path_text).resolve().exists():
                fail(
                    f"{markdown.relative_to(ROOT)} links to missing path {path_text}"
                )


def validate_marketplace() -> None:
    payload = load_json(MARKETPLACE)
    if not isinstance(payload, dict) or not isinstance(payload.get("plugins"), list):
        fail("marketplace plugins must be a list")
    entries = payload["plugins"]
    names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
    if len(names) != len(entries) or len(names) != len(set(names)):
        fail("marketplace plugin names must be unique")
    for plugin_name in ("railway-account", "image-editing"):
        if names.count(plugin_name) != 1:
            fail(f"marketplace must contain exactly one {plugin_name} entry")
        entry = next(entry for entry in entries if entry["name"] == plugin_name)
        if entry.get("source") != {
            "source": "local",
            "path": f"./plugins/{plugin_name}",
        }:
            fail(f"{plugin_name} marketplace source is invalid")
        if entry.get("policy") != {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        }:
            fail(f"{plugin_name} marketplace policy is invalid")


def validate_parity() -> None:
    for script_name in ("railway_configure_credentials.py", "railway_cli.py"):
        standalone = (STANDALONE / "scripts" / script_name).read_bytes()
        central = (CENTRAL / "scripts" / script_name).read_bytes()
        if standalone != central:
            fail(f"central {script_name} differs from the standalone helper")
        mode = stat.S_IMODE((STANDALONE / "scripts" / script_name).stat().st_mode)
        central_mode = stat.S_IMODE((CENTRAL / "scripts" / script_name).stat().st_mode)
        if mode & 0o111 == 0 or central_mode & 0o111 == 0:
            fail(f"{script_name} must be executable in both plugins")
    standalone_references = {
        path.name: path.read_bytes()
        for path in (STANDALONE_SKILL / "references").glob("*.md")
    }
    central_references = {
        path.name: path.read_bytes()
        for path in (CENTRAL_SKILL / "references").glob("*.md")
    }
    if standalone_references != central_references:
        fail("central Railway references differ from the standalone skill")
    standalone_image = {
        path.relative_to(IMAGE_SKILL): path.read_bytes()
        for path in IMAGE_SKILL.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    central_image = {
        path.relative_to(CENTRAL_IMAGE_SKILL): path.read_bytes()
        for path in CENTRAL_IMAGE_SKILL.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    if standalone_image != central_image:
        fail("central Food Image Editing skill differs from the standalone skill")
    for script in (
        IMAGE_SKILL / "scripts" / "food_image.py",
        CENTRAL_IMAGE_SKILL / "scripts" / "food_image.py",
    ):
        if stat.S_IMODE(script.stat().st_mode) & 0o111 == 0:
            fail(f"{script.relative_to(ROOT)} must be executable")


def validate_registry(
    standalone_manifest: dict[str, object],
    central_manifest: dict[str, object],
    image_manifest: dict[str, object],
) -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    for name in ("railway-account", "image-editing", "amsoft-agentic-workflows"):
        if text.count(f"| `{name}` |") != 1:
            fail(f"registry must contain exactly one {name} row")
    for name, manifest in (
        ("railway-account", standalone_manifest),
        ("image-editing", image_manifest),
        ("amsoft-agentic-workflows", central_manifest),
    ):
        version = manifest.get("version")
        if not isinstance(version, str) or f"`{version}`" not in text:
            fail(f"registry does not contain the current {name} version")


def validate_no_placeholders() -> None:
    for plugin in (STANDALONE, IMAGE, CENTRAL):
        for path in plugin.rglob("*"):
            if not path.is_file() or path.suffix not in {".json", ".md", ".yaml", ".py"}:
                continue
            text = path.read_text(encoding="utf-8")
            if "[TODO:" in text:
                fail(f"{path.relative_to(ROOT)} contains a TODO placeholder")
            if re.search(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b", text):
                fail(f"{path.relative_to(ROOT)} appears to contain a GitHub token")


def validate_central_extensions() -> None:
    if frontmatter_name(TRANSFER_SKILL) != "amsoft-agentic-workflows-config-transfer":
        fail("central config-transfer skill name is invalid")
    validate_links(CENTRAL / "skills")
    required_scripts = {
        "account_credential_common.py",
        "agentic_workflow_config_transfer.py",
        "cloudflare_api.py",
        "cloudflare_configure_credentials.py",
        "digitalocean_cli.py",
        "digitalocean_configure_credentials.py",
    }
    for name in required_scripts:
        path = CENTRAL / "scripts" / name
        if not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o111 == 0:
            fail(f"central helper {name} is missing or not executable")
    transfer_text = (TRANSFER_SKILL / "SKILL.md").read_text(encoding="utf-8")
    for marker in (
        ".amsoftx",
        "portable-passphrase",
        "local-session",
        "passphrase in chat.",
    ):
        if marker not in transfer_text:
            fail(f"config-transfer skill is missing required contract marker: {marker}")
    router = (
        CENTRAL / "skills" / "amsoft-agentic-workflows" / "SKILL.md"
    ).read_text(encoding="utf-8")
    if router.count("`amsoft-agentic-workflows-config-transfer`") < 2:
        fail("central router does not route and catalog config transfer")
    for marker in (
        "color-similarity",
        "mask preview",
        "`food-image-editing`",
    ):
        if marker not in router:
            fail(f"central router is missing Food Image Editing marker: {marker}")
    image_skill = (IMAGE_SKILL / "SKILL.md").read_text(encoding="utf-8")
    image_research = (
        IMAGE_SKILL / "references" / "research-and-guardrails.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "mask-preview",
        'type: "color_similarity"',
        "global_base",
        "CIEDE2000",
    ):
        if marker not in image_skill and marker not in image_research:
            fail(f"Food Image Editing is missing required marker: {marker}")


def main() -> None:
    standalone_manifest = validate_manifest(STANDALONE)
    central_manifest = validate_manifest(CENTRAL)
    image_manifest = validate_manifest(IMAGE)
    if frontmatter_name(STANDALONE_SKILL) != "railway-account-operations":
        fail("standalone Railway skill name is invalid")
    if frontmatter_name(CENTRAL_SKILL) != "amsoft-railway-account-operations":
        fail("central Railway skill name is invalid")
    if frontmatter_name(IMAGE_SKILL) != "food-image-editing":
        fail("standalone Food Image Editing skill name is invalid")
    if frontmatter_name(CENTRAL_IMAGE_SKILL) != "food-image-editing":
        fail("central Food Image Editing skill name is invalid")
    validate_links(STANDALONE_SKILL)
    validate_links(CENTRAL_SKILL)
    validate_links(IMAGE_SKILL)
    validate_links(CENTRAL_IMAGE_SKILL)
    validate_links(CENTRAL / "skills" / "amsoft-agentic-workflows")
    validate_marketplace()
    validate_parity()
    validate_registry(standalone_manifest, central_manifest, image_manifest)
    validate_central_extensions()
    validate_no_placeholders()
    print("Repository plugin package validation passed.")


if __name__ == "__main__":
    main()
