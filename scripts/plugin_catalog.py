#!/usr/bin/env python3
"""Catalog loading and deterministic mirror materialization."""

from __future__ import annotations

import json
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "plugins-v2.yaml"
CATALOG_SCHEMA_PATH = ROOT / "catalog" / "plugins-v2.schema.json"


class CatalogError(RuntimeError):
    """Raised when the plugin catalog or a declared mirror is invalid."""


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


@dataclass(frozen=True)
class MaterializedFile:
    source: Path
    destination: Path
    content: bytes
    mode: int


def repository_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise CatalogError(f"catalog path escapes repository root: {relative}") from error
    return path


def load_catalog() -> dict[str, Any]:
    try:
        catalog = yaml.load(
            CATALOG_PATH.read_text(encoding="utf-8"),
            Loader=UniqueKeyLoader,
        )
        schema = json.loads(
            CATALOG_SCHEMA_PATH.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
        jsonschema.validate(catalog, schema)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as error:
        raise CatalogError(f"cannot load plugin catalog: {error}") from error
    except jsonschema.ValidationError as error:
        raise CatalogError(f"plugin catalog schema violation: {error.message}") from error
    if not isinstance(catalog, dict):
        raise CatalogError("plugin catalog must contain an object")
    return catalog


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def apply_replacements(
    content: bytes,
    replacements: Iterable[dict[str, str]],
    *,
    require_all: bool = False,
    allow_binary_passthrough: bool = False,
) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        if allow_binary_passthrough:
            return content
        raise CatalogError("transformed mirrors must be UTF-8 text") from error
    for replacement in replacements:
        source = replacement["from"]
        if require_all and source not in text:
            raise CatalogError(f"mirror replacement source is absent: {source!r}")
        text = text.replace(source, replacement["to"])
    return text.encode("utf-8")


def source_files(directory: Path, excluded: set[str]) -> list[Path]:
    excluded = {"__pycache__", ".DS_Store"} | excluded
    return sorted(
        path
        for path in directory.rglob("*")
        if (
            path.is_file()
            and path.suffix != ".pyc"
            and not any(part in excluded for part in path.parts)
        )
    )


def materialize_mirror(mirror: dict[str, Any]) -> list[MaterializedFile]:
    kind = mirror["kind"]
    source = repository_path(mirror["source"])
    destination = repository_path(mirror["destination"])
    excluded = set(mirror.get("exclude", []))
    replacements = mirror.get("replacements", [])

    if kind in {"exact_file", "transformed_file"}:
        content = source.read_bytes()
        if kind == "transformed_file":
            content = apply_replacements(content, replacements, require_all=True)
        return [
            MaterializedFile(
                source=source,
                destination=destination,
                content=content,
                mode=stat.S_IMODE(source.stat().st_mode),
            )
        ]

    if kind == "exact_tree":
        return [
            MaterializedFile(
                source=path,
                destination=destination / path.relative_to(source),
                content=path.read_bytes(),
                mode=stat.S_IMODE(path.stat().st_mode),
            )
            for path in source_files(source, excluded)
        ]

    if kind == "prefixed_skill_set":
        source_prefix = mirror["source_prefix"]
        destination_prefix = mirror["destination_prefix"]
        materialized: list[MaterializedFile] = []
        skill_directories = [
            directory
            for directory in sorted(source.iterdir())
            if directory.is_dir() and directory.name.startswith(source_prefix)
        ]
        text_parts: list[str] = []
        for directory in skill_directories:
            for path in source_files(directory, excluded):
                try:
                    text_parts.append(path.read_bytes().decode("utf-8"))
                except UnicodeDecodeError:
                    # Binary assets such as PPTX, PNG, or PDF are copied byte-for-byte;
                    # namespace replacements apply only to UTF-8 skill text.
                    continue
        all_content = "\n".join(text_parts)
        for replacement in replacements:
            if replacement["from"] not in all_content:
                raise CatalogError(
                    f"mirror replacement source is absent: {replacement['from']!r}"
                )
        for skill_directory in skill_directories:
            suffix = skill_directory.name.removeprefix(source_prefix)
            destination_skill = destination / f"{destination_prefix}{suffix}"
            for path in source_files(skill_directory, excluded):
                materialized.append(
                    MaterializedFile(
                        source=path,
                        destination=destination_skill / path.relative_to(skill_directory),
                        content=apply_replacements(
                            path.read_bytes(),
                            replacements,
                            allow_binary_passthrough=True,
                        ),
                        mode=stat.S_IMODE(path.stat().st_mode),
                    )
                )
        return materialized

    raise CatalogError(f"unsupported mirror kind: {kind}")


def expected_mirror_files(catalog: dict[str, Any]) -> list[MaterializedFile]:
    files: list[MaterializedFile] = []
    destinations: set[Path] = set()
    for mirror in catalog["mirrors"]:
        for materialized in materialize_mirror(mirror):
            if materialized.destination in destinations:
                raise CatalogError(
                    f"multiple mirrors target {materialized.destination.relative_to(ROOT)}"
                )
            destinations.add(materialized.destination)
            files.append(materialized)
    return files


def mirror_differences(catalog: dict[str, Any]) -> list[str]:
    differences: list[str] = []
    for materialized in expected_mirror_files(catalog):
        relative = materialized.destination.relative_to(ROOT)
        if not materialized.destination.is_file():
            differences.append(f"missing generated mirror: {relative}")
            continue
        if materialized.destination.read_bytes() != materialized.content:
            differences.append(f"generated mirror content differs: {relative}")
        destination_mode = stat.S_IMODE(materialized.destination.stat().st_mode)
        if destination_mode != materialized.mode:
            differences.append(
                f"generated mirror mode differs: {relative} "
                f"({destination_mode:04o} != {materialized.mode:04o})"
            )
    return differences


def write_mirrors(catalog: dict[str, Any]) -> None:
    for materialized in expected_mirror_files(catalog):
        materialized.destination.parent.mkdir(parents=True, exist_ok=True)
        materialized.destination.write_bytes(materialized.content)
        materialized.destination.chmod(materialized.mode)


def marketplace_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    packages = {package["name"]: package for package in catalog["packages"]}
    entries = []
    for name in catalog["marketplace"]["plugin_order"]:
        package = packages[name]
        entries.append(
            {
                "name": name,
                "source": {
                    "source": "local",
                    "path": f"./{package['path']}",
                },
                "policy": package["policy"],
                "category": package["category"],
            }
        )
    return {
        "name": catalog["marketplace"]["name"],
        "interface": {"displayName": catalog["marketplace"]["display_name"]},
        "plugins": entries,
    }


def marketplace_difference(catalog: dict[str, Any]) -> str | None:
    path = repository_path(catalog["marketplace"]["path"])
    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return f"generated marketplace is missing or invalid: {path.relative_to(ROOT)}"
    if current != marketplace_payload(catalog):
        return f"generated marketplace content differs: {path.relative_to(ROOT)}"
    return None


def write_marketplace(catalog: dict[str, Any]) -> None:
    path = repository_path(catalog["marketplace"]["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(marketplace_payload(catalog), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def prerequisite_block(skill: dict[str, Any]) -> str:
    lines = ["<!-- catalog-prerequisites:start -->", "## Prerequisites", ""]
    if skill["prerequisites"]:
        for item in skill["prerequisites"]:
            status = "Required" if item["required"] else "Optional"
            lines.append(f"- **{status}: {item['name']}** — {item['setup']}")
    else:
        lines.append("- No additional setup beyond installing this plugin.")
    lines += ["", "<!-- catalog-prerequisites:end -->"]
    return "\n".join(lines)


def skill_documentation_differences(catalog: dict[str, Any]) -> list[str]:
    differences = []
    for package in catalog["packages"]:
        for skill in package["skills"]:
            path = repository_path(f"{package['path']}/skills/{skill['name']}/SKILL.md")
            if not path.is_file() or prerequisite_block(skill) not in path.read_text(encoding="utf-8"):
                differences.append(f"prerequisites differ: {path.relative_to(ROOT)}")
    return differences


def write_skill_documentation(catalog: dict[str, Any]) -> None:
    for package in catalog["packages"]:
        for skill in package["skills"]:
            path = repository_path(f"{package['path']}/skills/{skill['name']}/SKILL.md")
            content = path.read_text(encoding="utf-8")
            start = content.find("<!-- catalog-prerequisites:start -->")
            end = content.find("<!-- catalog-prerequisites:end -->")
            if start >= 0 and end >= start:
                end += len("<!-- catalog-prerequisites:end -->")
                content = content[:start] + content[end:].lstrip("\n")
            block = prerequisite_block(skill)
            if content.startswith("---\n"):
                frontmatter_end = content.find("\n---\n", 4)
                if frontmatter_end < 0:
                    raise CatalogError(f"invalid skill frontmatter: {path.relative_to(ROOT)}")
                split = frontmatter_end + 5
                content = content[:split] + "\n" + block + "\n\n" + content[split:].lstrip("\n")
            else:
                content = block + "\n\n" + content
            path.write_text(content, encoding="utf-8")


def claude_package_path(package: dict[str, Any]) -> Path:
    return ROOT / "generated" / "claude" / "plugins" / package["name"]


def claude_marketplace_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    packages = {package["name"]: package for package in catalog["packages"]}
    return {
        "name": catalog["marketplace"]["name"],
        "description": "Private reusable agent workflows for Claude Code.",
        "owner": {"name": "Wilson Le"},
        "plugins": [
            {"name": name, "source": f"./generated/claude/plugins/{name}"}
            for name in catalog["marketplace"]["plugin_order"]
            if "claude-code" in packages[name]["harnesses"]
        ],
    }


def write_claude_packages(catalog: dict[str, Any]) -> None:
    root = ROOT / "generated" / "claude" / "plugins"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    for package in catalog["packages"]:
        if "claude-code" not in package["harnesses"]:
            continue
        source = repository_path(package["path"])
        destination = claude_package_path(package)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".codex-plugin", "__pycache__", ".DS_Store"))
        allowed = {skill["name"] for skill in package["skills"] if "claude-code" in skill["harnesses"]}
        for directory in (destination / "skills").iterdir():
            if directory.is_dir() and directory.name not in allowed:
                shutil.rmtree(directory)
        if package["name"] == "agentic-workflows":
            router = destination / "skills" / "agentic-workflows" / "SKILL.md"
            lines = router.read_text(encoding="utf-8").splitlines()
            lines = [line for line in lines if not (line.startswith("- `") and line.split("`", 2)[1] not in allowed)]
            router.write_text("\n".join(lines) + "\n", encoding="utf-8")
        manifest = json.loads((source / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = {key: manifest[key] for key in ("name", "version", "description", "author", "license")}
        claude_manifest["description"] = claude_manifest["description"].replace("Codex", "agent")
        if package["name"] == "agentic-workflows":
            claude_manifest["description"] = "Reusable workflows for research, writing, development, provider operations, media, and business tasks."
        metadata = destination / ".claude-plugin"
        metadata.mkdir()
        (metadata / "plugin.json").write_text(json.dumps(claude_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    marketplace.parent.mkdir(exist_ok=True)
    marketplace.write_text(json.dumps(claude_marketplace_payload(catalog), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def claude_differences(catalog: dict[str, Any]) -> list[str]:
    differences = []
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    if not marketplace.is_file() or json.loads(marketplace.read_text(encoding="utf-8")) != claude_marketplace_payload(catalog):
        differences.append("Claude marketplace differs")
    for package in catalog["packages"]:
        if "claude-code" not in package["harnesses"]:
            continue
        destination = claude_package_path(package)
        if not (destination / ".claude-plugin" / "plugin.json").is_file():
            differences.append(f"Claude package missing: {package['name']}")
            continue
        expected = {skill["name"] for skill in package["skills"] if "claude-code" in skill["harnesses"]}
        actual = {path.name for path in (destination / "skills").iterdir() if path.is_dir()}
        if actual != expected:
            differences.append(f"Claude skills differ: {package['name']}")
        for name in expected:
            if package["name"] == "agentic-workflows" and name == "agentic-workflows":
                continue
            canonical = repository_path(f"{package['path']}/skills/{name}/SKILL.md")
            generated = destination / "skills" / name / "SKILL.md"
            if not generated.is_file() or generated.read_bytes() != canonical.read_bytes():
                differences.append(f"Claude skill content differs: {package['name']}/{name}")
    return differences
