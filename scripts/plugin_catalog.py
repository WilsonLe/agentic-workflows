#!/usr/bin/env python3
"""Catalog loading and deterministic mirror materialization."""

from __future__ import annotations

import json
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "plugins-v1.yaml"
CATALOG_SCHEMA_PATH = ROOT / "catalog" / "plugins-v1.schema.json"


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
