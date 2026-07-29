#!/usr/bin/env python3
"""Validate repository plugin structure and central-integration invariants."""

from __future__ import annotations

import importlib.util
import json
import re
import stat
import sys
from pathlib import Path

import yaml

from plugin_catalog import CatalogError, load_catalog, mirror_differences

ROOT = Path(__file__).resolve().parents[1]
CENTRAL = ROOT / "plugins" / "amsoft-agentic-workflows"
IMAGE = ROOT / "plugins" / "image-editing"
IMAGE_SKILL = IMAGE / "skills" / "food-image-editing"
RESTAURANT_SKILL = (
    ROOT
    / "plugins"
    / "restaurant-marketing"
    / "skills"
    / "restaurant-marketing-management"
)
TRANSFER_SKILL = CENTRAL / "skills" / "amsoft-agentic-workflows-config-transfer"
STANDARD_SKILL = CENTRAL / "skills" / "standard-development-workflow"
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


def validate_agent_metadata(skill: Path, required: bool) -> None:
    metadata_path = skill / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        if required:
            fail(f"{metadata_path.relative_to(ROOT)} is required by the catalog")
        return
    try:
        payload = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
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
    policy = payload.get("policy")
    if policy is not None and (
        not isinstance(policy, dict)
        or not isinstance(policy.get("allow_implicit_invocation"), bool)
    ):
        fail(f"{metadata_path.relative_to(ROOT)} has an invalid policy")


def validate_package_skills(
    plugin: Path,
    package_contract: dict[str, object],
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
        validate_agent_metadata(skill, contract["agent_metadata"] == "required")


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
    package_names = {package["name"] for package in catalog["packages"]}
    expected_names = catalog["marketplace"]["plugin_order"]
    if set(expected_names) != package_names:
        fail("marketplace plugin order does not contain every catalog package exactly once")
    if names != expected_names:
        fail("marketplace plugin order or inventory differs from catalog")
    for package in catalog["packages"]:
        plugin_name = package["name"]
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
    text = REGISTRY.read_text(encoding="utf-8")
    for package in catalog["packages"]:
        name = package["registry_name"]
        rows = [line for line in text.splitlines() if line.startswith(f"| `{name}` |")]
        if len(rows) != 1:
            fail(f"registry must contain exactly one {name} row")
        manifest = manifests[package["name"]]
        version = manifest.get("version")
        if not isinstance(version, str) or f"`{version}`" not in rows[0]:
            fail(f"registry does not contain the current {name} version")


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
    count_marker = f"Explain the {documentation['central_component_count']} components"
    if count_marker not in onboarding:
        fail(f"{onboarding_path.relative_to(ROOT)} component count differs from catalog")
    readme_path = ROOT / documentation["readme"]
    readme = readme_path.read_text(encoding="utf-8")
    for path in documentation["repository_layout"]:
        if f"`{path}" not in readme:
            fail(f"{readme_path.relative_to(ROOT)} omits catalog path {path}")
    router_path = ROOT / documentation["central_router"]
    router = router_path.read_text(encoding="utf-8")
    central_package = next(
        package
        for package in catalog["packages"]
        if package["name"] == "amsoft-agentic-workflows"
    )
    for skill in central_package["skills"]:
        name = skill["name"]
        if name == "amsoft-agentic-workflows":
            continue
        if f"`{name}`" not in router and f"${name}" not in router:
            fail(f"{router_path.relative_to(ROOT)} omits catalog skill {name}")


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
        "excalidraw_api.py",
        "excalidraw_configure_credentials.py",
        "excalidraw_credential_common.py",
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
    image_reporting = (
        IMAGE_SKILL / "references" / "photo-curation-reporting.md"
    ).read_text(encoding="utf-8")
    image_adjustments = (
        IMAGE_SKILL / "references" / "adjustment-parameter-guide.md"
    ).read_text(encoding="utf-8")
    image_composition = (
        IMAGE_SKILL / "references" / "composition-and-geometric-editing.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "mask-preview",
        'type: "color_similarity"',
        "global_base",
        "CIEDE2000",
    ):
        if marker not in image_skill and marker not in image_research:
            fail(f"Food Image Editing is missing required marker: {marker}")
    for marker in (
        "Photo curation and reporting",
        "main HTML curation report",
        "detailed HTML report",
        "Rank every candidate",
        "photo-curation-main-report.html",
        "photo-curation-dish-report.html",
    ):
        if marker not in image_skill and marker not in image_reporting:
            fail(f"Food Image Editing is missing curation marker: {marker}")
    for marker in (
        '"adjustment_brief"',
        '"film_grain"',
        "Grain versus Film Grain",
        "Combination matrix",
        '"magenta": [0, 1, 0]',
        "unknown recipe key",
    ):
        if marker not in image_skill and marker not in image_adjustments:
            fail(f"Food Image Editing is missing adjustment marker: {marker}")
    for marker in (
        '"composition_brief"',
        '"perspective_crop"',
        "Rotation, perspective crop, and warp matrix",
        "Purpose and aspect-ratio matrix",
        "free-form warp",
        "top-left, top-right, bottom-right, bottom-left",
    ):
        if marker not in image_skill and marker not in image_composition:
            fail(f"Food Image Editing is missing composition marker: {marker}")
    report_templates = {
        "photo-curation-main-report.html": "const report =",
        "photo-curation-dish-report.html": "const review =",
    }
    for name, marker in report_templates.items():
        template = IMAGE_SKILL / "templates" / name
        if not template.is_file() or marker not in template.read_text(encoding="utf-8"):
            fail(f"Food Image Editing report template is invalid: {name}")
    if "per-dish HTML curation reports" not in router:
        fail("central router does not advertise per-dish HTML curation reports")
    for marker in (
        "`amsoft-excalidraw-api-operations`",
        "`amsoft-excalidraw-scene-operations`",
        "never MCP",
        "unknown-outcome",
    ):
        if marker not in router:
            fail(f"central router is missing Excalidraw marker: {marker}")


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


def validate_standard_workflow() -> None:
    if frontmatter_name(STANDARD_SKILL) != "standard-development-workflow":
        fail("Standard Development Workflow skill name is invalid")
    validate_links(STANDARD_SKILL)
    required = {
        "schemas/standard-workflow-v1.schema.json",
        "templates/repository-capability-profile.json",
        "templates/task-run.json",
        "examples/archetype-matrix.md",
        "references/workflow-record-model.md",
        "references/discovery-contract-and-scope.md",
        "references/validation-state-and-resume.md",
        "references/verification-evidence-and-release.md",
        "references/evaluation-matrix.md",
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
            STANDARD_SKILL / "references" / "workflow-record-model.md",
            STANDARD_SKILL / "references" / "discovery-contract-and-scope.md",
            STANDARD_SKILL / "references" / "validation-state-and-resume.md",
            STANDARD_SKILL / "references" / "verification-evidence-and-release.md",
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
        "codex plugin marketplace upgrade amsoft --json",
    ):
        if marker not in combined:
            fail(f"Standard Development Workflow is missing required marker: {marker}")
    for documentation in (
        ROOT / "README.md",
        CENTRAL
        / "skills"
        / "amsoft-agentic-workflows"
        / "references"
        / "onboarding.md",
        STANDARD_SKILL / "references" / "verification-evidence-and-release.md",
    ):
        text = documentation.read_text(encoding="utf-8")
        for marker in (
            "codex plugin marketplace add",
            "anhminhsoft/amsoft-agentic-workflow-codex-plugin",
            "--ref main",
            "codex plugin marketplace upgrade amsoft --json",
            "codex plugin add amsoft-agentic-workflows@amsoft --json",
        ):
            if marker not in text:
                fail(
                    f"{documentation.relative_to(ROOT)} is missing install marker: "
                    f"{marker}"
                )


def main() -> None:
    try:
        catalog = load_catalog()
    except CatalogError as error:
        fail(str(error))
    manifests: dict[str, dict[str, object]] = {}
    for package in catalog["packages"]:
        plugin = ROOT / package["path"]
        manifests[package["name"]] = validate_manifest(plugin, package)
        validate_package_skills(plugin, package)
        validate_executables(plugin, package)
        validate_links(plugin)
    validate_marketplace(catalog)
    differences = mirror_differences(catalog)
    if differences:
        fail(differences[0])
    validate_registry(catalog, manifests)
    validate_central_extensions()
    validate_restaurant_marketing()
    validate_standard_workflow()
    validate_no_placeholders(catalog)
    validate_documentation_contract(catalog)
    print("Repository plugin package validation passed.")


if __name__ == "__main__":
    main()
