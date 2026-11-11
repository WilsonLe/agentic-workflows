#!/usr/bin/env python3
"""Catalog loading and deterministic package materialization."""

from __future__ import annotations

import json
import re
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
    """Raised when a plugin catalog or package is invalid."""


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


def source_files(
    directory: Path, excluded: set[str], *, reject_symlinks: bool = False
) -> list[Path]:
    excluded = {"__pycache__", ".DS_Store"} | excluded
    files = []
    for path in directory.rglob("*"):
        if path.suffix == ".pyc" or any(part in excluded for part in path.parts):
            continue
        if reject_symlinks and path.is_symlink():
            raise CatalogError(f"package source contains a symlink: {path.relative_to(ROOT)}")
        if path.is_file():
            files.append(path)
    return sorted(files)


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


def capability_block() -> str:
    return (
        "<!-- catalog-capabilities:start -->\n"
        "## Companion capabilities\n\n"
        "Reuse complete skill and reference instructions already available in the current "
        "context for the same source/version, including host-loaded content. A name, "
        "description, path, summary, or prior-session read alone is not loaded instructions. "
        "Read missing instructions when needed; reread only for a known source/version "
        "change, unavailable or truncated content (including after compaction), or an explicit "
        "request. A stage transition or repeated link does not require reloading.\n\n"
        "When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) "
        "for discovery as needed. Apply the selected skill using that reuse rule and check "
        "availability and prerequisites; "
        "carry the user's brief, accepted decisions, artifacts, and verification limits into "
        "the handoff. Keep one owner for shared state and timing. A capability listing "
        "does not authorize publishing, paid calls, messaging, or delegation.\n\n"
        "<!-- catalog-capabilities:end -->"
    )



def capability_map(package: dict[str, Any]) -> str:
    """Render the suite's skill discovery from its catalog entries."""
    guidance = (
        repository_path(
            f"{package['path']}/skills/agentic-workflows/references/capability-handoffs.md"
        )
        .read_text(encoding="utf-8")
        .strip()
    )
    lines = [
        "<!-- Generated by scripts/generate_plugin_packages.py; edit catalog/skill sources. -->",
        "# Suite capabilities",
        "",
        f"Package: `{package['name']}`. Harness: `codex`.",
        "",
        "Each entry links to its installed skill. The inventory includes skills "
        "available in Codex. Prerequisites live in each skill.",
        "",
        guidance,
        "",
        "## Capability inventory",
        "",
        "| Skill | When to use |",
        "| --- | --- |",
    ]
    for skill in sorted(package["skills"], key=lambda item: item["name"]):
        name = skill["name"]
        path = repository_path(f"{package['path']}/skills/{name}/SKILL.md")
        content = path.read_text(encoding="utf-8")
        end = content.find("\n---\n", 4) if content.startswith("---\n") else -1
        if end < 0:
            raise CatalogError(f"invalid skill frontmatter: {path.relative_to(ROOT)}")
        try:
            metadata = yaml.load(content[4:end], Loader=UniqueKeyLoader)
        except yaml.YAMLError as error:
            raise CatalogError(f"invalid skill frontmatter: {path.relative_to(ROOT)}") from error
        if not isinstance(metadata, dict) or not isinstance(metadata.get("description"), str):
            raise CatalogError(f"missing skill description: {path.relative_to(ROOT)}")
        description = " ".join(metadata["description"].split()).replace("|", "\\|")
        label = f"[`{name}`](skills/{name}/SKILL.md)"
        lines.append(f"| {label} | {description} |")
    return "\n".join(lines) + "\n"



def skill_documentation_differences(catalog: dict[str, Any]) -> list[str]:
    differences = []
    for package in catalog["packages"]:
        for skill in package["skills"]:
            path = repository_path(f"{package['path']}/skills/{skill['name']}/SKILL.md")
            if not path.is_file() or prerequisite_block(skill) not in path.read_text(
                encoding="utf-8"
            ):
                differences.append(f"prerequisites differ: {path.relative_to(ROOT)}")
            if not path.is_file() or capability_block() not in path.read_text(
                encoding="utf-8"
            ):
                differences.append(
                    f"capability handoff differs: {path.relative_to(ROOT)}"
                )
        path = repository_path(f"{package['path']}/CAPABILITIES.md")
        if not path.is_file() or path.read_text(encoding="utf-8") != capability_map(
            package
        ):
            differences.append(f"capability map differs: {path.relative_to(ROOT)}")
    return differences


def write_skill_documentation(catalog: dict[str, Any]) -> None:
    for package in catalog["packages"]:
        for skill in package["skills"]:
            path = repository_path(f"{package['path']}/skills/{skill['name']}/SKILL.md")
            content = path.read_text(encoding="utf-8")
            for marker in ("prerequisites", "capabilities"):
                start = content.find(f"<!-- catalog-{marker}:start -->")
                end = content.find(f"<!-- catalog-{marker}:end -->")
                if start >= 0 and end >= start:
                    end += len(f"<!-- catalog-{marker}:end -->")
                    content = content[:start] + content[end:].lstrip("\n")
            block = prerequisite_block(skill) + "\n\n" + capability_block()
            if content.startswith("---\n"):
                frontmatter_end = content.find("\n---\n", 4)
                if frontmatter_end < 0:
                    raise CatalogError(
                        f"invalid skill frontmatter: {path.relative_to(ROOT)}"
                    )
                split = frontmatter_end + 5
                content = (
                    content[:split]
                    + "\n"
                    + block
                    + "\n\n"
                    + content[split:].lstrip("\n")
                )
            else:
                content = block + "\n\n" + content
            if skill["name"] == "agentic-workflows":
                labels = {
                    item["name"]: f"- `{item['name']}` ({', '.join(item['harnesses'])})"
                    for item in package["skills"]
                }
                content = re.sub(
                    r"^- `([a-z0-9-]+)` \([^\n]+\)$",
                    lambda match: labels.get(match[1], match[0]),
                    content,
                    flags=re.MULTILINE,
                )
            path.write_text(content, encoding="utf-8")
    for package in catalog["packages"]:
        repository_path(f"{package['path']}/CAPABILITIES.md").write_text(
            capability_map(package), encoding="utf-8"
        )


def write_materialized_files(files: Iterable[MaterializedFile]) -> None:
    for item in files:
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        item.destination.write_bytes(item.content)
        item.destination.chmod(item.mode)


def git_file_mode(mode: int) -> int:
    return 0o755 if mode & stat.S_IXUSR else 0o644


def distribution_files(catalog: dict[str, Any], root: Path) -> list[MaterializedFile]:
    """Copy the complete Codex suite and marketplace without host transformations."""
    files = []
    for package in catalog["packages"]:
        source = ROOT / package["path"]
        repository_path(package["path"])  # Validate containment before reading assets.
        if source.resolve() != source:
            raise CatalogError("distribution package path must not traverse symlinks")
        for path in source_files(source, set(), reject_symlinks=True):
            files.append(MaterializedFile(
                path, root / package["path"] / path.relative_to(source),
                path.read_bytes(), git_file_mode(path.stat().st_mode),
            ))
    marketplace = repository_path(catalog["marketplace"]["path"])
    files.append(MaterializedFile(
        marketplace, root / catalog["marketplace"]["path"],
        (json.dumps(marketplace_payload(catalog), indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        0o644,
    ))
    return files


def distribution_differences(catalog: dict[str, Any], root: Path) -> list[str]:
    if root.is_symlink():
        return [f"distribution directory must not be a symlink: {root}"]
    if not root.is_dir():
        return [f"distribution directory missing: {root}"]
    expected = {item.destination: item for item in distribution_files(catalog, root)}
    directories = {
        parent
        for path in expected
        for parent in path.parents
        if parent.is_relative_to(root)
    }
    actual = set()
    differences = []
    for path in sorted(root.rglob("*")):
        label = path.relative_to(root)
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode) and path in directories:
            continue
        if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            differences.append(f"distribution unsafe entry: {label}")
            continue
        item = expected.get(path)
        if item is None or not stat.S_ISREG(mode):
            differences.append(f"distribution unexpected entry: {label}")
            continue
        actual.add(path)
        if path.read_bytes() != item.content:
            differences.append(f"distribution content differs: {label}")
        if git_file_mode(mode) != item.mode:
            differences.append(f"distribution executable mode differs: {label}")
    for path in sorted(expected.keys() - actual):
        differences.append(f"distribution file missing: {path.relative_to(root)}")
    return differences
