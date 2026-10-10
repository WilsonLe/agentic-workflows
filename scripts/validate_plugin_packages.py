#!/usr/bin/env python3
"""Validate repository plugin structure and central-integration invariants."""

from __future__ import annotations

import importlib.util
import json
import re
import stat
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from plugin_catalog import (
    CatalogError,
    UniqueKeyLoader,
    claude_differences,
    load_catalog,
    mirror_differences,
    skill_documentation_differences,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_LICENSE = ROOT / "LICENSE"
PACKAGE_LICENSE_ID = "MIT"
CENTRAL = ROOT / "plugins" / "agentic-workflows"
ORCHESTRATION = ROOT / "plugins" / "agent-orchestration"
ORCHESTRATION_SKILL = ORCHESTRATION / "skills" / "orchestration"
IMAGE = ROOT / "plugins" / "image-editing"
IMAGE_SKILL = IMAGE / "skills" / "food-image-editing"
CALORIE = ROOT / "plugins" / "calorie-tracker"
CALORIE_SKILL = CALORIE / "skills" / "calorie-tracker"
QR = ROOT / "plugins" / "qr-code-generator"
QR_SKILL = QR / "skills" / "qr-code-generation"
RESTAURANT_SKILL = (
    ROOT
    / "plugins"
    / "restaurant-marketing"
    / "skills"
    / "restaurant-marketing-management"
)
LITERATURE_SKILL = (
    ROOT
    / "plugins"
    / "literature-review"
    / "skills"
    / "literature-review-workflow"
)
SYSTEMATIC_SKILL = (
    ROOT
    / "plugins"
    / "systematic-literature-review"
    / "skills"
    / "systematic-literature-review-workflow"
)
TRANSFER_SKILL = CENTRAL / "skills" / "agentic-workflows-config-transfer"
STANDARD_SKILL = CENTRAL / "skills" / "standard-development-workflow"
REGISTRY = (
    CENTRAL
    / "skills"
    / "agentic-workflows"
    / "references"
    / "plugin-registry.md"
)
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
ROOTED_REFERENCE_PATTERN = re.compile(
    r"<(plugin-root|skill-root)>/"
    r"((?:references|scripts|schemas|examples|templates)/"
    r"[A-Za-z0-9_.@+/-]+)"
)
AMBIGUOUS_COMMAND_PATTERN = re.compile(
    r"\b(?:(?:python3?|bash|node|npx)\s+|uv\s+run(?:\s+python3?)?\s+)"
    r"((?:plugins|scripts|\.\./)[A-Za-z0-9_.@+/-]+)"
)
UNROOTED_INLINE_ASSET_PATTERN = re.compile(
    r"`((?:references|scripts|schemas|examples|templates)/"
    r"[A-Za-z0-9_.@+/-]+)`"
)
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)\s*#*$", re.MULTILINE)


def fail(message: str) -> None:
    print(f"Validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeError, ValueError) as error:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {error}")


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def validate_manifest(
    plugin: Path,
    package_contract: dict[str, object],
) -> dict[str, object]:
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    payload = load_json(manifest_path)
    if not isinstance(payload, dict):
        fail(f"{manifest_path.relative_to(ROOT)} must contain an object")
    if payload.get("name") != plugin.name:
        fail(f"{manifest_path.relative_to(ROOT)} name must match its directory")
    version = payload.get("version")
    if not isinstance(version, str) or not version:
        fail(f"{manifest_path.relative_to(ROOT)} is missing a version")
    if payload.get("skills") != "./skills/":
        fail(f"{manifest_path.relative_to(ROOT)} skills path must be ./skills/")
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
    if interface.get("displayName") != package_contract["display_name"]:
        fail(f"{manifest_path.relative_to(ROOT)} display name differs from catalog")
    if interface.get("category") != package_contract["category"]:
        fail(f"{manifest_path.relative_to(ROOT)} category differs from catalog")
    return payload


def validate_package_license(
    plugin: Path,
    manifest: dict[str, object],
) -> None:
    if manifest.get("license") != PACKAGE_LICENSE_ID:
        fail(
            f"{plugin.relative_to(ROOT)} manifest license must be "
            f"{PACKAGE_LICENSE_ID}"
        )
    license_path = plugin / "LICENSE"
    if not license_path.is_file():
        fail(f"{license_path.relative_to(ROOT)} is missing")
    canonical = PACKAGE_LICENSE.read_bytes()
    if license_path.read_bytes() != canonical:
        fail(
            f"{license_path.relative_to(ROOT)} differs from the canonical "
            "MIT License"
        )


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


def heading_slug(heading: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", heading).strip().lower()
    normalized = re.sub(r"[^\w\- ]", "", without_tags)
    return re.sub(r"[ _]+", "-", normalized)


def skill_root_for(markdown: Path, plugin: Path) -> Path | None:
    skills_root = plugin / "skills"
    try:
        relative = markdown.relative_to(skills_root)
    except ValueError:
        return None
    if len(relative.parts) < 2:
        return None
    candidate = skills_root / relative.parts[0]
    return candidate if (candidate / "SKILL.md").is_file() else None


def validate_links(directory: Path) -> None:
    for markdown in directory.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            if (
                target.startswith(("http://", "https://", "mailto:"))
                or "://" in target
            ):
                continue
            path_text = target.split("#", 1)[0]
            resolved = (markdown.parent / path_text).resolve() if path_text else markdown
            if path_text and not resolved.exists():
                fail(
                    f"{markdown.relative_to(ROOT)} links to missing path {path_text}"
                )
            _, separator, anchor = target.partition("#")
            if separator and resolved.suffix.lower() == ".md" and resolved.is_file():
                slugs = {
                    heading_slug(match.group(1))
                    for match in HEADING_PATTERN.finditer(
                        resolved.read_text(encoding="utf-8")
                    )
                }
                if anchor.lower() not in slugs:
                    fail(
                        f"{markdown.relative_to(ROOT)} links to missing anchor "
                        f"#{anchor} in {resolved.relative_to(ROOT)}"
                    )


def validate_packaged_references(plugin: Path) -> None:
    for markdown in (plugin / "skills").rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        skill_root = skill_root_for(markdown, plugin)
        for root_name, reference in ROOTED_REFERENCE_PATTERN.findall(text):
            base = plugin if root_name == "plugin-root" else skill_root
            if base is None:
                fail(
                    f"{markdown.relative_to(ROOT)} references missing "
                    f"<{root_name}>/{reference}"
                )
            resolved = (base / reference).resolve()
            try:
                resolved.relative_to(base.resolve())
            except ValueError:
                fail(
                    f"{markdown.relative_to(ROOT)} reference escapes "
                    f"<{root_name}>: {reference}"
                )
            if not resolved.is_file():
                fail(
                    f"{markdown.relative_to(ROOT)} references missing "
                    f"<{root_name}>/{reference}"
                )
        for match in UNROOTED_INLINE_ASSET_PATTERN.finditer(text):
            fail(
                f"{markdown.relative_to(ROOT)} uses unrooted inline asset path "
                f"{match.group(1)}; use <plugin-root> or <skill-root>"
            )
        for match in AMBIGUOUS_COMMAND_PATTERN.finditer(text):
            fail(
                f"{markdown.relative_to(ROOT)} uses ambiguous executable path "
                f"{match.group(1)}; use <plugin-root> or <skill-root>"
            )


def validate_agent_metadata(
    skill: Path,
    required: bool,
    require_skill_invocation: bool,
) -> None:
    metadata_path = skill / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        if required:
            fail(f"{metadata_path.relative_to(ROOT)} is required by the catalog")
        return
    try:
        payload = yaml.load(
            metadata_path.read_text(encoding="utf-8"),
            Loader=UniqueKeyLoader,
        )
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        fail(f"{metadata_path.relative_to(ROOT)} is invalid YAML: {error}")
    if not isinstance(payload, dict) or not isinstance(payload.get("interface"), dict):
        fail(f"{metadata_path.relative_to(ROOT)} is missing interface metadata")
    interface = payload["interface"]
    required_fields = {"display_name", "short_description", "default_prompt"}
    if not required_fields.issubset(interface):
        fail(f"{metadata_path.relative_to(ROOT)} is missing interface fields")
    if not all(isinstance(interface[field], str) and interface[field] for field in required_fields):
        fail(f"{metadata_path.relative_to(ROOT)} has an invalid interface field")
    if (
        require_skill_invocation
        and f"${skill.name}" not in interface["default_prompt"]
    ):
        fail(
            f"{metadata_path.relative_to(ROOT)} default prompt must invoke "
            f"${skill.name}"
        )
    policy = payload.get("policy")
    if policy is not None and (
        not isinstance(policy, dict)
        or not isinstance(policy.get("allow_implicit_invocation"), bool)
    ):
        fail(f"{metadata_path.relative_to(ROOT)} has an invalid policy")


def validate_package_skills(
    plugin: Path,
    package_contract: dict[str, object],
    reference_contract: dict[str, object],
) -> None:
    skill_contracts = package_contract["skills"]
    expected = {contract["name"] for contract in skill_contracts}
    skills_root = plugin / "skills"
    actual = {
        path.parent.name
        for path in skills_root.glob("*/SKILL.md")
        if path.is_file()
    }
    if actual != expected:
        fail(
            f"{skills_root.relative_to(ROOT)} skill inventory differs from catalog: "
            f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    for contract in skill_contracts:
        skill = skills_root / contract["name"]
        frontmatter_name(skill)
        validate_agent_metadata(
            skill,
            contract["agent_metadata"] == "required",
            bool(reference_contract["metadata_prompt_requires_skill_invocation"]),
        )


def validate_executables(
    plugin: Path,
    package_contract: dict[str, object],
) -> None:
    expected = {Path(relative) for relative in package_contract["executables"]}
    for relative in expected:
        path = plugin / relative
        if not path.is_file():
            fail(f"{path.relative_to(ROOT)} is a missing catalog executable")
        if stat.S_IMODE(path.stat().st_mode) & 0o111 == 0:
            fail(f"{path.relative_to(ROOT)} must be executable")
    actual = {
        path.relative_to(plugin)
        for path in plugin.rglob("*.py")
        if stat.S_IMODE(path.stat().st_mode) & 0o111
    }
    if actual != expected:
        fail(
            f"{plugin.relative_to(ROOT)} executable inventory differs from catalog: "
            f"missing={sorted(str(path) for path in expected - actual)}, "
            f"unexpected={sorted(str(path) for path in actual - expected)}"
        )


def validate_marketplace(catalog: dict[str, object]) -> None:
    marketplace_path = ROOT / catalog["marketplace"]["path"]
    payload = load_json(marketplace_path)
    if not isinstance(payload, dict) or not isinstance(payload.get("plugins"), list):
        fail("marketplace plugins must be a list")
    if payload.get("name") != catalog["marketplace"]["name"]:
        fail("marketplace name differs from catalog")
    if payload.get("interface", {}).get("displayName") != catalog["marketplace"]["display_name"]:
        fail("marketplace display name differs from catalog")
    entries = payload["plugins"]
    names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
    if len(names) != len(entries) or len(names) != len(set(names)):
        fail("marketplace plugin names must be unique")
    packages = {package["name"]: package for package in catalog["packages"]}
    expected_names = catalog["marketplace"]["plugin_order"]
    if not set(expected_names).issubset(packages):
        fail("marketplace plugin order contains an unknown catalog package")
    if expected_names != ["agentic-workflows"]:
        fail("marketplace must publish only agentic-workflows")
    if names != expected_names:
        fail("marketplace plugin order or inventory differs from catalog")
    central_skills = {
        skill["name"]: skill for skill in packages["agentic-workflows"]["skills"]
    }
    for package in catalog["packages"]:
        for skill in package["skills"]:
            if central_skills.get(skill["name"]) != skill:
                fail(
                    f"central bundle must preserve {package['name']}/{skill['name']} "
                    "and its harnesses, prerequisites, and metadata contract"
                )
    for plugin_name in expected_names:
        package = packages[plugin_name]
        if names.count(plugin_name) != 1:
            fail(f"marketplace must contain exactly one {plugin_name} entry")
        entry = next(entry for entry in entries if entry["name"] == plugin_name)
        if entry.get("source") != {
            "source": "local",
            "path": f"./{package['path']}",
        }:
            fail(f"{plugin_name} marketplace source is invalid")
        if entry.get("policy") != package["policy"]:
            fail(f"{plugin_name} marketplace policy is invalid")
        if entry.get("category") != package["category"]:
            fail(f"{plugin_name} marketplace category is invalid")


def validate_registry(
    catalog: dict[str, object],
    manifests: dict[str, dict[str, object]],
) -> None:
    rows: dict[str, tuple[int, list[str]]] = {}
    for line_number, line in enumerate(
        REGISTRY.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.startswith("| `"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 8:
            fail(f"registry row {line_number} must contain eight columns")
        name = columns[0].strip("`")
        if name in rows:
            fail(f"registry contains duplicate row for {name}")
        rows[name] = (line_number, columns)

    for package in catalog["packages"]:
        name = package["registry_name"]
        if name not in rows:
            fail(f"registry must contain exactly one {name} row")
        _, columns = rows[name]
        manifest = manifests[package["name"]]
        version = manifest.get("version")
        if not isinstance(version, str) or columns[2].strip("`") != version:
            fail(f"registry does not contain the current {name} version")
        expected_source = package["path"]
        if columns[3].strip("`") != expected_source:
            fail(
                f"registry source for {name} must be catalog path {expected_source}"
            )
        expected_marketplace = catalog["marketplace"]["name"]
        if columns[4].strip("`") != expected_marketplace:
            fail(
                f"registry marketplace for {name} must be {expected_marketplace}"
            )

    catalog_names = {package["registry_name"] for package in catalog["packages"]}
    unavailable_prefix = catalog["registry_contract"]["unavailable_source_prefix"]
    unverified_marker = catalog["registry_contract"]["unverified_marker"]
    for name, (line_number, columns) in rows.items():
        source_text = columns[3].strip("`")
        verified = columns[7].strip("`")
        if name not in catalog_names:
            expected_unavailable = (
                f"{unavailable_prefix}{name}@{columns[4].strip('`')}"
            )
            if source_text == expected_unavailable:
                if verified != unverified_marker:
                    fail(
                        f"unavailable registry source for {name} must use "
                        f"{unverified_marker}"
                    )
                continue
            if not Path(source_text).is_absolute():
                fail(
                    f"external registry source for {name} must be an absolute "
                    f"verified path or {expected_unavailable}"
                )
            if verified == unverified_marker:
                fail(f"live registry source for {name} cannot be marked unverified")
        source = Path(source_text)
        if not source.is_absolute():
            source = (ROOT / source).resolve()
            try:
                source.relative_to(ROOT.resolve())
            except ValueError:
                fail(f"registry source for {name} escapes repository root")
        if not source.is_dir():
            fail(f"registry source for {name} does not exist: {source_text}")
        manifest_path = source / ".codex-plugin" / "plugin.json"
        if not manifest_path.is_file():
            fail(
                f"registry source for {name} has no plugin manifest at row "
                f"{line_number}"
            )
        source_manifest = load_json(manifest_path)
        if not isinstance(source_manifest, dict):
            fail(f"registry source manifest for {name} must be an object")
        recorded_version = columns[2].strip("`")
        if source_manifest.get("name") != name:
            fail(f"registry source manifest name differs for {name}")
        if source_manifest.get("version") != recorded_version:
            fail(f"registry source manifest version differs for {name}")


def validate_central_skill_references(catalog: dict[str, object]) -> None:
    central_names = {
        skill["name"]
        for package in catalog["packages"]
        if package["name"] == "agentic-workflows"
        for skill in package["skills"]
    }
    standalone_names = {
        skill["name"]
        for package in catalog["packages"]
        if package["name"] != "agentic-workflows"
        for skill in package["skills"]
    }
    registry = REGISTRY.resolve()
    for markdown in (CENTRAL / "skills").rglob("*.md"):
        if markdown.resolve() == registry:
            continue
        text = markdown.read_text(encoding="utf-8")
        for referenced in re.findall(r"`([a-z][a-z0-9-]{2,})`", text):
            if referenced in standalone_names and referenced not in central_names:
                fail(
                    f"{markdown.relative_to(ROOT)} references standalone skill "
                    f"{referenced} from the central package"
                )


def validate_no_placeholders(catalog: dict[str, object]) -> None:
    for package in catalog["packages"]:
        plugin = ROOT / package["path"]
        for path in plugin.rglob("*"):
            if not path.is_file() or path.suffix not in {
                ".html",
                ".json",
                ".md",
                ".py",
                ".yaml",
                ".yml",
            }:
                continue
            text = path.read_text(encoding="utf-8")
            if "[TODO:" in text:
                fail(f"{path.relative_to(ROOT)} contains a TODO placeholder")
            if re.search(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b", text):
                fail(f"{path.relative_to(ROOT)} appears to contain a GitHub token")


def validate_documentation_contract(catalog: dict[str, object]) -> None:
    documentation = catalog["documentation"]
    onboarding_path = ROOT / documentation["central_onboarding"]
    onboarding = onboarding_path.read_text(encoding="utf-8")
    if "Prerequisites" not in onboarding:
        fail(f"{onboarding_path.relative_to(ROOT)} omits setup guidance")
    readme_path = ROOT / documentation["readme"]
    readme = readme_path.read_text(encoding="utf-8")
    if "Claude Code" not in readme or "Codex" not in readme:
        fail(f"{readme_path.relative_to(ROOT)} omits harness installation")
    router_path = ROOT / documentation["central_router"]
    router = router_path.read_text(encoding="utf-8")
    central_package = next(
        package
        for package in catalog["packages"]
        if package["name"] == "agentic-workflows"
    )
    for skill in central_package["skills"]:
        name = skill["name"]
        if name == "agentic-workflows":
            continue
        if f"`{name}`" not in router and f"${name}" not in router:
            fail(f"{router_path.relative_to(ROOT)} omits catalog skill {name}")


def validate_central_extensions() -> None:
    if frontmatter_name(TRANSFER_SKILL) != "agentic-workflows-config-transfer":
        fail("central config-transfer skill name is invalid")
    validate_links(CENTRAL / "skills")
    required_scripts = {
        "account_credential_common.py",
        "agentic_workflow_config_transfer.py",
        "cloudflare_api.py",
        "cloudflare_configure_credentials.py",
        "digitalocean_cli.py",
        "digitalocean_configure_credentials.py",
        "excalidraw_api.py",
        "excalidraw_configure_credentials.py",
        "excalidraw_credential_common.py",
        "excalidraw_render.py",
    }
    for name in required_scripts:
        path = CENTRAL / "scripts" / name
        if not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o111 == 0:
            fail(f"central helper {name} is missing or not executable")
    transfer_text = (TRANSFER_SKILL / "SKILL.md").read_text(encoding="utf-8")
    for marker in (
        ".agenticx",
        "portable-passphrase",
        "local-session",
        "passphrase in chat.",
    ):
        if marker not in transfer_text:
            fail(f"config-transfer skill is missing required contract marker: {marker}")
    router = (
        CENTRAL / "skills" / "agentic-workflows" / "SKILL.md"
    ).read_text(encoding="utf-8")
    if "`agentic-workflows-config-transfer`" not in router:
        fail("central router omits config transfer")
    image_skill = (IMAGE_SKILL / "SKILL.md").read_text(encoding="utf-8")
    image_prompting = (
        IMAGE_SKILL / "references" / "openai-image-editing-prompt-workflow.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "instructions only",
        "OpenAI/Codex image-editing tool",
        "Prompt framework",
        "Change:",
        "Preserve:",
        "semantic object map",
        "Reference-object integration gate",
        "A search thumbnail",
        "Small corrective iterations",
        "Review gate",
    ):
        if marker not in image_skill:
            fail(f"Food Image Editing is missing required marker: {marker}")
    for marker in (
        "Template 1 — Restrained global polish",
        "Template 2 — Composition-preserving reframe",
        "Template 3 — Local light and focal emphasis",
        "Template 4 — Colour and material correction",
        "Template 5 — Match a visual set",
        "Template 6 — One-change corrective iteration",
        "Template 7 — Reference-object integration",
        "Object decomposition and online reference workflow",
        "appropriately licensed",
        "Multi-turn review loop",
    ):
        if marker not in image_prompting:
            fail(f"Food Image Editing is missing prompt template marker: {marker}")
    prohibited_image_paths = (
        "examples",
        "schemas",
        "scripts",
        "templates",
    )
    for relative in prohibited_image_paths:
        path = IMAGE_SKILL / relative
        if path.exists() and any(path.rglob("*")):
            fail(f"instruction-only Food Image Editing contains prohibited path: {relative}")
    for marker in ("`excalidraw-api-operations`", "`excalidraw-scene-operations`"):
        if marker not in router:
            fail(f"central router is missing Excalidraw marker: {marker}")


def validate_agent_orchestration() -> None:
    required = {
        "references/activation-and-goal-mode.md",
        "references/project-scope-and-trust.md",
        "references/portfolio-triage.md",
        "references/delegated-session-launch-settings.md",
        "references/issue-session-lifecycle.md",
        "references/review-session-lifecycle.md",
        "references/verification-session-lifecycle.md",
        "references/titles-and-status.md",
        "references/coordination-and-waiting.md",
        "references/closeout-archive-recovery.md",
        "references/coordination-register.md",
    }
    for relative in required:
        if not (ORCHESTRATION_SKILL / relative).is_file():
            fail(f"Agent Orchestration is missing {relative}")
    schema_v3 = load_json(
        ORCHESTRATION / "schemas" / "orchestration-state-v3.schema.json"
    )
    if (
        not isinstance(schema_v3, dict)
        or schema_v3.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or schema_v3.get("properties", {})
        .get("schema_version", {})
        .get("const")
        != 3
        or "task" not in schema_v3.get("$defs", {})
    ):
        fail("Agent Orchestration schema v3 metadata is invalid")
    schema = load_json(
        ORCHESTRATION / "schemas" / "orchestration-state-v4.schema.json"
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 4
        or "launch" not in schema.get("$defs", {})
        or "task" not in schema.get("$defs", {})
    ):
        fail("Agent Orchestration schema v4 metadata is invalid")
    schema_v5 = load_json(
        ORCHESTRATION / "schemas" / "orchestration-state-v5.schema.json"
    )
    schema_v6 = load_json(
        ORCHESTRATION / "schemas" / "orchestration-state-v6.schema.json"
    )
    claim_schema = load_json(
        ORCHESTRATION / "schemas" / "worktree-claim-v1.schema.json"
    )
    if (
        not isinstance(schema_v5, dict)
        or schema_v5.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema_v5.get("properties", {}).get("schema_version", {}).get("const") != 5
        or "state_revision" not in schema_v5.get("properties", {})
        or "remediationTurn" not in schema_v5.get("$defs", {})
    ):
        fail("Agent Orchestration schema v5 metadata is invalid")
    if (
        not isinstance(schema_v6, dict)
        or schema_v6.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema_v6.get("properties", {}).get("schema_version", {}).get("const") != 6
        or "sdlc_scope" not in schema_v6.get("properties", {})
        or "routing_decisions" not in schema_v6.get("properties", {})
    ):
        fail("Agent Orchestration schema v6 metadata is invalid")
    if (
        not isinstance(claim_schema, dict)
        or claim_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or claim_schema.get("properties", {}).get("schema_version", {}).get("const") != 1
    ):
        fail("Agent Orchestration worktree claim schema metadata is invalid")
    schema = load_json(
        ORCHESTRATION / "schemas" / "orchestration-state-v7.schema.json"
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 7
        or schema.get("properties", {}).get("decision_policy", {}).get("const")
        != "autopilot"
        or "gateDecision" not in schema.get("$defs", {})
        or "launch" not in schema.get("$defs", {})
        or "task" not in schema.get("$defs", {})
        or "sdlcScope" not in schema.get("$defs", {})
        or "routingDecision" not in schema.get("$defs", {})
    ):
        fail("Agent Orchestration schema v7 metadata is invalid")
    helper = ORCHESTRATION / "scripts" / "orchestration_state.py"
    helper_spec = importlib.util.spec_from_file_location(
        "agent_orchestration_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("Agent Orchestration helper cannot be imported")
    helper_module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper_module)
    example = load_json(ORCHESTRATION / "examples" / "register.json")
    claim_example = load_json(ORCHESTRATION / "examples" / "worktree-claim.json")
    Draft202012Validator.check_schema(schema_v3)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(schema_v5)
    Draft202012Validator.check_schema(schema_v6)
    Draft202012Validator.check_schema(claim_schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(example),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        fail(f"Agent Orchestration example violates schema v7: {errors[0].message}")
    claim_errors = sorted(
        Draft202012Validator(claim_schema).iter_errors(claim_example),
        key=lambda error: list(error.absolute_path),
    )
    if claim_errors:
        fail(
            "Agent Orchestration worktree claim example violates schema v1: "
            f"{claim_errors[0].message}"
        )
    helper_module.validate_register(example)
    helper_module._validate_claim(claim_example)
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ORCHESTRATION_SKILL / "SKILL.md",
            *sorted((ORCHESTRATION_SKILL / "references").glob("*.md")),
        ]
    )
    for marker in (
        "explicit operator designation",
        "Inspect current goal state",
        "explicit delegated goal contract",
        "Goal is clear. I have no further questions.",
        "Goal Mode increases persistence, not authority",
        "ordinary delivery authority envelope",
        "Control-plane mode always runs in autopilot",
        "decision_policy=autopilot",
        "Never\nforward or relay a routine decision request to the operator",
        "`proceed`, `revise`, `retry`, `skip`, `stop`, or `blocked`",
        "Issue #<number>",
        "PR #<number>",
        "<short status>",
        "at most eight",
        "archive intent",
        "exact task ID",
        "Never store prompts",
        "message bodies",
        "untrusted",
        "Never create subagents",
        "identify safe local equivalents",
        "full-suite coverage deferred",
        "then rerun affected checks and the full suite",
        "patiently waits, observes, and steers only",
        "Goal: <concrete terminal outcome>",
        "never labels that inspection independent review",
        "Start asynchronously at a stable review point",
        "exact implementation worktree",
        "gpt-5.6-luna",
        "reasoning effort `max`",
        "Never create a separate verifier worktree",
        "terminal outcome: `passed`, `failed`, or",
        "terminal `clear` result reconciled",
        "passed verification",
        "same unchanged exact",
        "independently matching review",
        "authoritatively archived",
        "claim-sidecar writes",
        "realpath-normalized path identity",
        "no-source-work state",
        "preserves the v4 conflict",
        "owner-restricted",
        "compare-and-swap",
        "v4_detached_review",
        "new worktree",
        "refreshed `main`",
        "minor dependency",
        "cleanup `preserved`",
        "full_access",
        "Goal mode only",
        "host_capability",
        "readback_unavailable",
        "permission_mismatch",
        "mode_mismatch",
        "Never emulate a host setting with\nprompt text",
        "Do not record per-command",
        "Production must be directly named",
    ):
        if marker not in combined:
            fail(f"Agent Orchestration is missing required marker: {marker}")


def validate_calorie_tracker() -> None:
    required = {
        "references/image-analysis-and-accuracy.md",
        "references/nutrition-providers.md",
        "references/onboarding.md",
        "references/google-storage.md",
        "references/privacy-and-safety.md",
        "references/research-basis.md",
        "schemas/calorie-tracker-v1.schema.json",
        "examples/synthetic-meal-analysis.json",
        "examples/synthetic-provider-plan.json",
    }
    for relative in required:
        if not (CALORIE_SKILL / relative).is_file():
            fail(f"Calorie Tracker is missing {relative}")
    schema = load_json(CALORIE_SKILL / "schemas" / "calorie-tracker-v1.schema.json")
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or not {"meal_analysis", "meal_record", "storage_contract", "provider_plan", "operation_journal"}.issubset(
            schema.get("$defs", {})
        )
    ):
        fail("Calorie Tracker schema v1 metadata is invalid")
    helper = CALORIE / "scripts" / "calorie_tracker.py"
    helper_spec = importlib.util.spec_from_file_location("calorie_tracker_package_validation", helper)
    if helper_spec is None or helper_spec.loader is None:
        fail("Calorie Tracker helper cannot be imported")
    module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(module)
    analysis = load_json(CALORIE_SKILL / "examples" / "synthetic-meal-analysis.json")
    record = module.build_meal_record(
        analysis,
        entry_id="00000000-0000-4000-8000-000000000001",
        timestamp="2026-01-01T00:00:00Z",
    )
    record = module.bind_drive_image(
        record,
        "SYNTHETIC_FILE_ID",
        "https://drive.google.com/file/d/SYNTHETIC_FILE_ID/view",
    )
    contract = {
        "schema_version": 1,
        "contract_revision": 1,
        "google_provider": "google-drive-connector",
        "spreadsheet_id": "SYNTHETIC_SHEET_ID",
        "meals_tab": "Meals",
        "meals_sheet_id": 101,
        "items_tab": "Meal Items",
        "items_sheet_id": 102,
        "drive_folder_id": "SYNTHETIC_FOLDER_ID",
        "timezone": "Australia/Brisbane",
        "column_schema_version": 1,
        "write_mode": "append-only",
        "image_link_policy": "private-drive-url",
        "verified_at": "2026-01-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    batch = module.build_sheet_batch(record, contract)
    if len(batch.get("requests", [])) != 2 or "formulaValue" in json.dumps(batch):
        fail("Calorie Tracker typed two-tab batch contract is invalid")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [CALORIE_SKILL / "SKILL.md", *sorted((CALORIE_SKILL / "references").glob("*.md"))]
    )
    for marker in (
        "visible`, `user`, `provider`, and `inference",
        "Never blindly repeat upload",
        "20 provider requests",
        "private-drive-url",
        "flag a material discrepancy",
        "not medical advice",
    ):
        if marker not in combined:
            fail(f"Calorie Tracker is missing required marker: {marker}")


def validate_qr_code_generator() -> None:
    required = {
        "references/payload-and-privacy.md",
        "references/style-and-theme-contract.md",
        "references/image-generation-and-compositing.md",
        "references/verification-and-recovery.md",
        "references/dependencies-and-licensing.md",
        "schemas/qr-code-v1.schema.json",
        "examples/plain-url.json",
        "examples/styled-restaurant-menu.json",
        "examples/image-generation-assisted.json",
        "examples/rejected-variant-result.json",
    }
    for relative in required:
        if not (QR_SKILL / relative).is_file():
            fail(f"QR Code Generator is missing {relative}")
    schema = load_json(QR_SKILL / "schemas" / "qr-code-v1.schema.json")
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 1
        or set(schema.get("$defs", {})) != {"output", "style", "logo", "background", "privacy"}
    ):
        fail("QR Code Generator schema v1 metadata is invalid")
    validator = Draft202012Validator(schema)
    helper = QR / "scripts" / "qr_code_generator.py"
    if stat.S_IMODE(helper.stat().st_mode) & 0o111 == 0:
        fail("QR Code Generator helper must be executable")
    helper_spec = importlib.util.spec_from_file_location(
        "qr_code_generator_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("QR Code Generator helper cannot be imported")
    module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(module)
    examples = []
    for name in ("plain-url", "styled-restaurant-menu", "image-generation-assisted"):
        example = load_json(QR_SKILL / "examples" / f"{name}.json")
        if not isinstance(example, dict):
            fail(f"QR Code Generator example is not an object: {name}")
        errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))
        if errors:
            fail(f"QR Code Generator example does not match schema: {name}: {errors[0].message}")
        try:
            validated = module.validate_request(example)
        except module.QRCodeError as error:
            fail(f"QR Code Generator example failed helper validation: {name}: {error.message}")
        prompt = module.build_image_generation_prompt(validated)
        if "[QR SAFE AREA]" not in prompt or example["payload"] in prompt:
            fail(f"QR Code Generator image prompt is not payload-safe: {name}")
        examples.append(validated)
    rejected = load_json(QR_SKILL / "examples" / "rejected-variant-result.json")
    if (
        not isinstance(rejected, dict)
        or rejected.get("state") != "decode_mismatch"
        or rejected.get("baseline_preserved") is not True
        or "payload" in rejected
    ):
        fail("QR Code Generator rejected-variant fixture is unsafe or incomplete")
    with tempfile.TemporaryDirectory() as directory:
        for index, example in enumerate(examples):
            output_dir = Path(directory) / str(index)
            output_dir.mkdir()
            try:
                manifest = module.render_request(example, output_dir)
            except module.QRCodeError as error:
                fail(f"QR Code Generator example could not render: {example['qr_id']}: {error.message}")
            if manifest.get("state") != "verified":
                fail(f"QR Code Generator example is not decoder-verified: {example['qr_id']}")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [QR_SKILL / "SKILL.md", *sorted((QR_SKILL / "references").glob("*.md"))]
    )
    for marker in (
        "exact user payload",
        "four-module quiet zone",
        "[QR SAFE AREA]",
        "ZXing-C++",
        "The image model never owns",
        "verification_unavailable",
        "decode_mismatch",
        "BSD 3-Clause",
        "MIT-CMU License",
        "Apache License 2.0",
        "uv sync --locked",
    ):
        if marker not in combined:
            fail(f"QR Code Generator is missing required marker: {marker}")


def validate_restaurant_marketing() -> None:
    required = {
        "references/onboarding.md",
        "references/campaign-operating-system.md",
        "references/campaign-archetypes.md",
        "references/offer-economics.md",
        "references/channels-and-creative.md",
        "references/compliance-and-approvals.md",
        "references/measurement-and-learning.md",
        "references/research-basis.md",
        "templates/restaurant-profile.json",
        "templates/campaign-plan.json",
        "templates/campaign-result.json",
        "examples/new-dish-campaign.json",
        "examples/offer-campaign.json",
        "examples/seasonal-dish-campaign.json",
        "schemas/restaurant-marketing-v1.schema.json",
        "scripts/restaurant_marketing.py",
    }
    for relative in required:
        if not (RESTAURANT_SKILL / relative).is_file():
            fail(f"Restaurant Marketing is missing {relative}")
    schema = load_json(
        RESTAURANT_SKILL / "schemas" / "restaurant-marketing-v1.schema.json"
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or set(schema.get("$defs", {}))
        < {"restaurant_profile", "campaign_plan", "campaign_result"}
    ):
        fail("Restaurant Marketing schema v1 metadata is invalid")
    helper = RESTAURANT_SKILL / "scripts" / "restaurant_marketing.py"
    helper_spec = importlib.util.spec_from_file_location(
        "restaurant_marketing_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("Restaurant Marketing helper cannot be imported")
    helper_module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper_module)
    for directory in ("templates", "examples"):
        for path in sorted((RESTAURANT_SKILL / directory).glob("*.json")):
            helper_module.validate_record(load_json(path))
    offer = load_json(RESTAURANT_SKILL / "examples" / "offer-campaign.json")
    economics = helper_module.economics_summary(offer)
    if (
        economics.get("promoted_contribution_per_incremental_unit") != "19.00"
        or economics.get("incremental_units_to_cover_fixed_cost") != 13
    ):
        fail("Restaurant Marketing offer economics fixture is incorrect")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            RESTAURANT_SKILL / "SKILL.md",
            *sorted((RESTAURANT_SKILL / "references").glob("*.md")),
        ]
    ).lower()
    for marker in (
        "exact-target approval",
        "review gating",
        "contribution",
        "expiry verification",
        "business outcome",
        "observation",
        "inference",
    ):
        if marker not in combined:
            fail(f"Restaurant Marketing is missing required marker: {marker}")


def validate_literature_review() -> None:
    required = {
        "references/review-method-selection.md",
        "references/search-and-source-selection.md",
        "references/critical-reading-and-appraisal.md",
        "references/concept-centric-synthesis.md",
        "references/writing-reporting-and-integrity.md",
        "references/research-basis.md",
        "templates/review-brief.md",
        "templates/method-and-boundaries.md",
        "templates/search-journal.csv",
        "templates/source-decisions.csv",
        "templates/concept-matrix.csv",
        "templates/synthesis-map.md",
        "templates/counterevidence-and-gaps.md",
        "templates/review-state.json",
        "templates/citations.bib",
        "schemas/literature-review-v1.schema.json",
        "scripts/literature_review.py",
        "examples/narrative-review/review-state.json",
        "examples/integrative-review/review-state.json",
        "examples/invalid-pseudo-systematic-review/review-state.json",
    }
    for relative in required:
        if not (LITERATURE_SKILL / relative).is_file():
            fail(f"Literature Review is missing {relative}")
    schema = load_json(
        LITERATURE_SKILL / "schemas" / "literature-review-v1.schema.json"
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 1
        or set(schema.get("$defs", {})) != {"source", "claim"}
    ):
        fail("Literature Review schema v1 metadata is invalid")
    helper = LITERATURE_SKILL / "scripts" / "literature_review.py"
    if stat.S_IMODE(helper.stat().st_mode) & 0o111 == 0:
        fail("Literature Review helper must be executable")
    helper_spec = importlib.util.spec_from_file_location(
        "literature_review_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("Literature Review helper cannot be imported")
    helper_module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper_module)
    for name in ("narrative-review", "integrative-review"):
        result = helper_module.validate_project(
            LITERATURE_SKILL / "examples" / name,
            require_final=True,
        )
        if result.get("status") != "complete":
            fail(f"Literature Review fixture is not complete: {name}")
    try:
        helper_module.validate_project(
            LITERATURE_SKILL / "examples" / "invalid-pseudo-systematic-review"
        )
    except helper_module.ValidationError as error:
        if "systematic intent must route" not in str(error):
            fail("Literature Review systematic route fixture failed incorrectly")
    else:
        fail("Literature Review systematic route fixture unexpectedly passed")
    for pdf in sorted((LITERATURE_SKILL / "examples").glob("*/papers/*.pdf")):
        if pdf.stat().st_size > 1024 or b"Synthetic Agentic Workflows" not in pdf.read_bytes():
            fail(f"Literature Review contains a non-synthetic PDF fixture: {pdf.name}")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            LITERATURE_SKILL / "SKILL.md",
            *sorted((LITERATURE_SKILL / "references").glob("*.md")),
        ]
    ).lower()
    for marker in (
        "narrative",
        "integrative",
        "critical",
        "conceptual/theoretical",
        "state-of-the-art",
        "systematic literature review plugin",
        "search-journal.csv",
        "source-decisions.csv",
        "concept-matrix.csv",
        "counterevidence",
        "coverage limitations",
        "untrusted research material",
        "humanizer",
    ):
        if marker not in combined:
            fail(f"Literature Review is missing required marker: {marker}")


def validate_systematic_literature_review() -> None:
    required = {
        "references/feasibility-and-method-selection.md",
        "references/protocol-and-registration.md",
        "references/search-design-and-reporting.md",
        "references/record-identity-and-deduplication.md",
        "references/screening-and-full-text.md",
        "references/extraction-and-appraisal.md",
        "references/synthesis-and-certainty.md",
        "references/reporting-update-and-audit.md",
        "references/automation-and-human-oversight.md",
        "references/standards-and-licences.md",
        "schemas/systematic-review-v1.schema.json",
        "scripts/systematic_review.py",
    }
    required.update(
        f"examples/{name}/scenario.json"
        for name in (
            "complete-two-reviewer",
            "blocked-single-reviewer",
            "multiple-reports-one-study",
            "ambiguous-dedup",
            "protocol-amendment",
            "synthesis-without-meta-analysis",
            "external-statistics-provenance",
        )
    )
    required.update(
        f"templates/project/{relative}"
        for relative in (
            "review-charter.md",
            "protocol/protocol.md",
            "protocol/protocol-state.json",
            "protocol/amendments.csv",
            "searches/search-run-ledger.csv",
            "searches/raw-exports/manifest.csv",
            "records/records.csv",
            "records/reports.csv",
            "records/studies.csv",
            "records/identity-links.csv",
            "dedup/dedup-decisions.csv",
            "screening/title-abstract-decisions.csv",
            "screening/full-text-decisions.csv",
            "screening/conflicts.csv",
            "screening/excluded-full-text.csv",
            "extraction/extraction-form.json",
            "extraction/extraction-values.csv",
            "extraction/conflicts.csv",
            "extraction/transformations.csv",
            "appraisal/appraisal-plan.md",
            "appraisal/appraisal-decisions.csv",
            "synthesis/synthesis-plan.md",
            "synthesis/synthesis-data.csv",
            "synthesis/synthesis-report.md",
            "certainty/certainty-decisions.csv",
            "reporting/flow-counts.json",
            "reporting/applicable-checklist.md",
            "reporting/review-report.md",
            "reporting/limitations-and-deviations.md",
            "citations.bib",
            "audit/review-state.json",
            "audit/contributor-actions.csv",
            "audit/automation-log.csv",
            "audit/validation-report.txt",
        )
    )
    for relative in sorted(required):
        if not (SYSTEMATIC_SKILL / relative).is_file():
            fail(f"Systematic Literature Review is missing {relative}")
    schema = load_json(
        SYSTEMATIC_SKILL / "schemas" / "systematic-review-v1.schema.json"
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 1
        or set(schema.get("$defs", {}))
        < {"stable_id", "review_state", "contributor_type", "transition"}
    ):
        fail("Systematic Literature Review schema v1 metadata is invalid")
    helper = SYSTEMATIC_SKILL / "scripts" / "systematic_review.py"
    if stat.S_IMODE(helper.stat().st_mode) & 0o111 == 0:
        fail("Systematic Literature Review helper must be executable")
    helper_spec = importlib.util.spec_from_file_location(
        "systematic_review_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("Systematic Literature Review helper cannot be imported")
    helper_module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper_module)
    templates = {
        path.relative_to(SYSTEMATIC_SKILL / "templates" / "project").as_posix()
        for path in (SYSTEMATIC_SKILL / "templates" / "project").rglob("*")
        if path.is_file()
    }
    if not helper_module.REQUIRED_PATHS.issubset(templates):
        fail("Systematic Literature Review required artifacts differ from templates")
    for path in sorted((SYSTEMATIC_SKILL / "examples").glob("*/scenario.json")):
        fixture = load_json(path)
        if (
            not isinstance(fixture, dict)
            or fixture.get("schema_version") != 1
            or fixture.get("synthetic") is not True
            or fixture.get("contains_real_research") is not False
        ):
            fail(f"Systematic Literature Review fixture is unsafe: {path.name}")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            SYSTEMATIC_SKILL / "SKILL.md",
            *sorted((SYSTEMATIC_SKILL / "references").glob("*.md")),
        ]
    ).lower()
    for marker in (
        "prisma is reporting guidance",
        "record/report/study",
        "raw exports are immutable",
        "human reviewer",
        "never a second independent human",
        "universal quality score",
        "does not itself choose the synthesis method",
        "plugin never",
        "current terms",
        "literature-review-workflow",
        "only when that skill is actually installed",
    ):
        if marker not in combined:
            fail(f"Systematic Literature Review is missing required marker: {marker}")


def validate_standard_workflow() -> None:
    if frontmatter_name(STANDARD_SKILL) != "standard-development-workflow":
        fail("Standard Development Workflow skill name is invalid")
    validate_links(STANDARD_SKILL)
    required = {
        "schemas/standard-workflow-v1.schema.json",
        "templates/repository-capability-profile.json",
        "templates/task-run.json",
        "examples/archetype-matrix.md",
        "examples/efficiency-scenarios.md",
        "references/workflow-record-model.md",
        "references/discovery-contract-and-scope.md",
        "references/validation-state-and-resume.md",
        "references/verification-evidence-and-release.md",
        "references/evaluation-matrix.md",
        "references/efficient-delivery-and-external-work.md",
        "references/impact-inventory.md",
        "references/runtime-diagnosis.md",
        "references/release-readback.md",
        "scripts/standard_workflow_record.py",
    }
    for relative in required:
        if not (STANDARD_SKILL / relative).is_file():
            fail(f"Standard Development Workflow is missing {relative}")
    schema = load_json(STANDARD_SKILL / "schemas" / "standard-workflow-v1.schema.json")
    if (
        not isinstance(schema, dict)
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {}).get("schema_version", {}).get("const") != 1
    ):
        fail("Standard Development Workflow schema v1 metadata is invalid")
    for name in ("repository-capability-profile.json", "task-run.json"):
        template = load_json(STANDARD_SKILL / "templates" / name)
        if not isinstance(template, dict) or template.get("schema_version") != 1:
            fail(f"Standard Development Workflow template is invalid: {name}")
    helper = STANDARD_SKILL / "scripts" / "standard_workflow_record.py"
    if stat.S_IMODE(helper.stat().st_mode) & 0o111 == 0:
        fail("Standard Development Workflow helper must be executable")
    helper_spec = importlib.util.spec_from_file_location(
        "standard_workflow_record_package_validation", helper
    )
    if helper_spec is None or helper_spec.loader is None:
        fail("Standard Development Workflow helper cannot be imported")
    helper_module = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper_module)
    for name in ("repository-capability-profile.json", "task-run.json"):
        helper_module.validate_record(
            load_json(STANDARD_SKILL / "templates" / name)
        )
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            STANDARD_SKILL / "SKILL.md",
            STANDARD_SKILL / "references" / "spec-ready.md",
            STANDARD_SKILL / "references" / "stage-contracts.md",
            STANDARD_SKILL / "references" / "workflow-record-model.md",
            STANDARD_SKILL / "references" / "discovery-contract-and-scope.md",
            STANDARD_SKILL / "references" / "validation-state-and-resume.md",
            STANDARD_SKILL / "references" / "verification-evidence-and-release.md",
            STANDARD_SKILL / "references" / "worktree-bootstrap.md",
        )
    ).lower()
    for marker in (
        "repository_profile",
        "task_run",
        "minimal correct path",
        "shared cache",
        "diagnose before patching",
        "completed-unverified",
        "equivalent fallback",
        "rehearsal evidence",
        "codex plugin marketplace upgrade agentic-workflows --json",
        ".worktrees",
        "canonical pinned plan",
        "<!-- standard-development-plan -->",
        "reapproval_required",
        "every image supplied by the user",
        "upload each image to github so it is embedded in the issue body",
        "request images: none",
        "exported png sketches",
        "tool-neutral issue text",
        "no silent omission",
    ):
        if marker not in combined:
            fail(f"Standard Development Workflow is missing required marker: {marker}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in ("codex plugin marketplace add", "claude plugin marketplace add"):
        if marker not in readme:
            fail(f"README.md is missing install marker: {marker}")


def main() -> None:
    try:
        catalog = load_catalog()
    except CatalogError as error:
        fail(str(error))
    manifests: dict[str, dict[str, object]] = {}
    canonical_license = PACKAGE_LICENSE.read_text(encoding="utf-8")
    for marker in (
        "MIT License",
        "Copyright (c) 2026 Wilson Le",
        "Permission is hereby granted, free of charge",
        "The above copyright notice and this permission notice",
    ):
        if marker not in canonical_license:
            fail(f"canonical MIT license is missing marker: {marker}")
    for package in catalog["packages"]:
        plugin = ROOT / package["path"]
        manifests[package["name"]] = validate_manifest(plugin, package)
        validate_package_license(plugin, manifests[package["name"]])
        validate_package_skills(plugin, package, catalog["reference_contract"])
        validate_executables(plugin, package)
        validate_links(plugin)
        validate_packaged_references(plugin)
    validate_marketplace(catalog)
    differences = mirror_differences(catalog)
    differences.extend(skill_documentation_differences(catalog))
    differences.extend(claude_differences(catalog))
    if differences:
        fail(differences[0])
    validate_registry(catalog, manifests)
    validate_central_skill_references(catalog)
    validate_central_extensions()
    validate_agent_orchestration()
    validate_calorie_tracker()
    validate_qr_code_generator()
    validate_literature_review()
    validate_systematic_literature_review()
    validate_restaurant_marketing()
    validate_standard_workflow()
    validate_no_placeholders(catalog)
    validate_documentation_contract(catalog)
    print("Repository plugin package validation passed.")


if __name__ == "__main__":
    main()
