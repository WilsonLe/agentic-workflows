#!/usr/bin/env python3
"""Catalog loading and deterministic mirror materialization."""

from __future__ import annotations

import hashlib
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
    known = set(catalog["harnesses"])
    for package in catalog["packages"]:
        if not set(package["harnesses"]).issubset(known):
            raise CatalogError(f"unknown package harness: {package['name']}")
        for skill in package["skills"]:
            if not set(skill["harnesses"]).issubset(package["harnesses"]):
                raise CatalogError(f"skill harness is not supported by package: {package['name']}/{skill['name']}")
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
    write_materialized_files(expected_mirror_files(catalog))


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



def capability_map(
    catalog: dict[str, Any], package: dict[str, Any], harness: str
) -> str:
    """Render discovery from existing metadata, without a second capability registry."""
    central = next(
        item for item in catalog["packages"] if item["name"] == "agentic-workflows"
    )
    local = {item["name"] for item in package["skills"] if harness in item["harnesses"]}
    guidance = (
        repository_path(
            f"{central['path']}/skills/agentic-workflows/references/capability-handoffs.md"
        )
        .read_text(encoding="utf-8")
        .strip()
    )
    lines = [
        "<!-- Generated by scripts/generate_plugin_packages.py; edit catalog/skill sources. -->",
        "# Suite capabilities",
        "",
        f"Package: `{package['name']}`. Harness: `{harness}`.",
        "",
        "Linked entries are included here. Unlinked entries are companion capabilities "
        "provided by the complete `agentic-workflows` bundle or an existing component "
        "installation; verify the installed skill list before invoking them. Unsupported "
        "harness entries are omitted. Prerequisites live in each skill.",
        "",
        guidance,
        "",
        "## Capability inventory",
        "",
        "| Skill | When to use | Source packages |",
        "| --- | --- | --- |",
    ]
    for skill in sorted(central["skills"], key=lambda item: item["name"]):
        if harness not in skill["harnesses"]:
            continue
        name = skill["name"]
        path = repository_path(f"{central['path']}/skills/{name}/SKILL.md")
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
        label = (
            f"[`{name}`](skills/{name}/SKILL.md)"
            if name in local
            else f"`{name}` (not included here)"
        )
        owners = ", ".join(
            f"`{item['name']}`"
            for item in catalog["packages"]
            if any(entry["name"] == name for entry in item["skills"])
        )
        lines.append(f"| {label} | {description} | {owners} |")
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
            catalog, package, "codex"
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
            capability_map(catalog, package, "codex"), encoding="utf-8"
        )


def claude_package_path(package: dict[str, Any], root: Path = ROOT) -> Path:
    return root / "generated" / "claude" / "plugins" / package["name"]


def claude_marketplace_payload(
    catalog: dict[str, Any], *, local_source: bool = False
) -> dict[str, Any]:
    packages = {package["name"]: package for package in catalog["packages"]}
    entries = []
    for name in catalog["marketplace"]["plugin_order"]:
        package = packages[name]
        if "claude-code" not in package["harnesses"]:
            continue
        path = claude_package_path(package).relative_to(ROOT).as_posix()
        source = f"./{path}" if local_source else {
            "source": "git-subdir",
            "url": "https://github.com/WilsonLe/agentic-workflows.git",
            "ref": "dist",
            "path": path,
        }
        entries.append({"name": name, "source": source})
    return {
        "name": catalog["marketplace"]["name"],
        "description": "Reusable workflows for Claude Code.",
        "owner": {"name": "Wilson Le"},
        "plugins": entries,
    }


def claude_marketplace_difference(catalog: dict[str, Any]) -> str | None:
    marketplace = repository_path(catalog["harnesses"]["claude-code"]["marketplace_path"])
    try:
        content = json.loads(marketplace.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        content = None
    if content != claude_marketplace_payload(catalog):
        return "Claude marketplace differs"
    return None


def write_claude_marketplace(catalog: dict[str, Any]) -> None:
    marketplace = repository_path(catalog["harnesses"]["claude-code"]["marketplace_path"])
    marketplace.parent.mkdir(parents=True, exist_ok=True)
    marketplace.write_text(
        json.dumps(claude_marketplace_payload(catalog), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def harness_excluded_mirror_files(
    catalog: dict[str, Any], package: dict[str, Any], harness: str
) -> set[str]:
    """Package-relative files mirrored from component packages that lack the harness."""
    root = repository_path(package["path"])
    owners = [(repository_path(item["path"]), item) for item in catalog["packages"]]
    excluded = set()
    for mirror in catalog["mirrors"]:
        source = repository_path(mirror["source"])
        owner = next(
            (item for path, item in owners if source == path or path in source.parents), None
        )
        if owner is None or harness in owner["harnesses"]:
            continue
        for materialized in materialize_mirror(mirror):
            if not materialized.destination.is_relative_to(root):
                continue
            relative = materialized.destination.relative_to(root)
            if relative.parts[0] != "skills":  # Skill trees follow skill harnesses.
                excluded.add(relative.as_posix())
    return excluded


def portable_package_files(
    catalog: dict[str, Any], package: dict[str, Any], harness: str, destination: Path
) -> list[MaterializedFile]:
    """Select portable assets from canonical sources, preserving package-relative paths.

    The catalog owns availability. Runtime hooks/metadata are not portable; callers
    supply harness-specific manifests separately. Unsupported skill trees are omitted.
    Claude SKILL.md bodies use Claude Code's documented path variables, which it
    substitutes at load time; files read later keep <plugin-root>/<skill-root>.
    """
    source = repository_path(package["path"])
    allowed = {skill["name"] for skill in package["skills"] if harness in skill["harnesses"]}
    excluded = harness_excluded_mirror_files(catalog, package, harness)
    files = []
    for path in source_files(source, {".codex-plugin", "hooks"}, reject_symlinks=True):
        relative = path.relative_to(source)
        if relative.as_posix() in excluded:
            continue
        if relative.parts[0] == "skills" and len(relative.parts) > 1 and relative.parts[1] not in allowed:
            continue
        if relative.as_posix() in PORTABLE_EXCLUDED_FILES:
            continue
        if relative.parts[0] == "skills" and relative.parts[2:] == ("agents", "openai.yaml"):
            continue  # Codex UI metadata with `$skill` prompts.
        content = path.read_bytes()
        if relative.as_posix() == "CAPABILITIES.md":
            content = capability_map(catalog, package, harness).encode("utf-8")
        elif relative.as_posix() == "skills/agentic-workflows/SKILL.md":
            content = re.sub(
                r"\nCodex automatic session naming.*?(?=\n\n|\Z)",
                "", content.decode("utf-8"), flags=re.DOTALL,
            ).encode("utf-8")
            lines = [
                line for line in content.decode("utf-8").splitlines()
                if not (line.startswith("- `") and line.split("`", 2)[1] not in allowed)
            ]
            content = ("\n".join(lines).rstrip() + "\n").encode("utf-8")
        if path.suffix == ".md":
            # Refer to excluded workflows without registering unavailable skills.
            def portable_link(match: re.Match[str]) -> str:
                target, separator, anchor = match[2].partition("#")
                if not target or "://" in target or target.startswith("mailto:"):
                    return match[0]
                resolved = (path.parent / target).resolve()
                if resolved.is_relative_to(source / "skills"):
                    parts = resolved.relative_to(source / "skills").parts
                    if parts and parts[0] not in allowed:
                        url = "https://github.com/wilsonle/agentic-workflows/blob/main/"
                        url += resolved.relative_to(ROOT).as_posix()
                        return f"[{match[1]}]({url}{separator}{anchor})"
                return match[0]

            content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", portable_link, content.decode("utf-8")).encode("utf-8")
        if harness == "claude-code" and len(relative.parts) == 3 and relative.parts[0] == "skills" and relative.name == "SKILL.md":
            content = claude_skill_entrypoint(content.decode("utf-8"), path.parent).encode("utf-8")
        files.append(MaterializedFile(path, destination / relative, content, stat.S_IMODE(path.stat().st_mode)))
    return files


PORTABLE_EXCLUDED_FILES = {"skills/agentic-workflows/references/session-title-policy.md"}
CLAUDE_PATH_VARIABLES = {
    "<plugin-root>": "${CLAUDE_PLUGIN_ROOT}",
    "<skill-root>": "${CLAUDE_SKILL_DIR}",
}


def claude_skill_entrypoint(text: str, skill_directory: Path) -> str:
    """Adapt a portable SKILL.md to Claude Code's load-time path substitution.

    Commands use the substituted variables directly. References keep the portable
    placeholders, so a note maps the ones this skill's references use to absolute
    paths, and adds Claude Code's shell-permission and browser-availability rules.
    """
    for placeholder, variable in CLAUDE_PATH_VARIABLES.items():
        text = text.replace(f"{placeholder}/", f"{variable}/")
    references = ""
    reference_root = skill_directory / "references"
    for path in source_files(reference_root, set()) if reference_root.is_dir() else []:
        relative = path.relative_to(skill_directory.parent.parent).as_posix()
        if relative in PORTABLE_EXCLUDED_FILES:
            continue
        try:
            references += path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    notes = []
    mapping = [
        f"`{placeholder}` for `{variable}`"
        for placeholder, variable in CLAUDE_PATH_VARIABLES.items()
        if placeholder in references
    ]
    if mapping:
        notes.append(
            f"This skill's references write {' and '.join(mapping)}. Use those absolute "
            "paths in commands you run or give to the user; never show the placeholders."
        )
    if "<project-root>" in references:
        notes.append(
            "`<project-root>` is the top-level directory of the checkout you are working in "
            "(`git rev-parse --show-toplevel`, or the working directory outside a Git checkout), "
            "which can differ from where Claude Code started."
        )
    if any(
        f"{root}/scripts/" in body
        for root in ("${CLAUDE_PLUGIN_ROOT}", "${CLAUDE_SKILL_DIR}", "<plugin-root>", "<skill-root>")
        for body in (text, references)
    ):
        notes.append(
            "Run each shell command on its own with absolute paths, without `cd`, chaining, "
            "or shell variables; run helpers with `python3` (or `uv run` where shown) and "
            "write input files with the file-writing tool. If a command is denied, run it "
            "again alone in that form before concluding that the shell is unavailable."
        )
    if "Claude in Chrome" in text:
        notes.append(
            "Claude in Chrome is available only when its browser tools are in this session's "
            "tool list. If they are absent, do not offer to open pages, create keys or tokens, "
            "or say you can use Claude in Chrome. Give the user the exact URL and steps to "
            "complete themselves; `claude --chrome` or `/chrome` enables browser help in a "
            "later session."
        )
    marker = "<!-- catalog-capabilities:end -->"
    if not notes or marker not in text:
        return text
    block = (
        "<!-- claude-code-notes:start -->\n## Claude Code\n\n"
        + "\n\n".join(notes)
        + "\n\n<!-- claude-code-notes:end -->"
    )
    return text.replace(marker, f"{marker}\n\n{block}", 1)


def write_materialized_files(files: Iterable[MaterializedFile]) -> None:
    for item in files:
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        item.destination.write_bytes(item.content)
        item.destination.chmod(item.mode)


def claude_manifest(
    package: dict[str, Any], files: list[MaterializedFile], root: Path = ROOT
) -> dict[str, Any]:
    """Build the Claude manifest; its version tracks the generated package content.

    Claude Code delivers a plugin update only when this version string changes, so
    the build metadata is a digest of the manifest fields and every packaged file.
    """
    manifest = json.loads(
        (repository_path(package["path"]) / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    metadata = {key: manifest[key] for key in ("description", "author", "license")}
    metadata["description"] = metadata["description"].replace("Codex", "agent")
    if package["name"] == "agentic-workflows":
        metadata[
            "description"
        ] = "Reusable workflows for research, writing, development, provider operations, media, and business tasks."
    destination = claude_package_path(package, root)
    digest = hashlib.sha256(
        json.dumps({"name": manifest["name"], **metadata}, sort_keys=True).encode("utf-8")
    )
    for item in sorted(files, key=lambda entry: entry.destination.as_posix()):
        relative = item.destination.relative_to(destination).as_posix().encode("utf-8")
        mode = git_file_mode(item.mode)
        digest.update(b"%d:%s:%o:%d:" % (len(relative), relative, mode, len(item.content)))
        digest.update(item.content)
    base = manifest["version"].split("+", 1)[0]
    return {
        "name": manifest["name"],
        "version": f"{base}+claude.{digest.hexdigest()[:12]}",
        **metadata,
    }


def claude_package_files(
    catalog: dict[str, Any], package: dict[str, Any], root: Path = ROOT
) -> list[MaterializedFile]:
    destination = claude_package_path(package, root)
    files = portable_package_files(catalog, package, "claude-code", destination)
    manifest = json.dumps(
        claude_manifest(package, files, root), indent=2, ensure_ascii=False
    ) + "\n"
    files.append(MaterializedFile(
        repository_path(package["path"]) / ".codex-plugin" / "plugin.json",
        destination / ".claude-plugin" / "plugin.json",
        manifest.encode("utf-8"),
        0o644,
    ))
    return files


def opencode_package_files(
    catalog: dict[str, Any], root: Path = ROOT
) -> list[MaterializedFile]:
    """OpenCode loads one complete skills bundle, not a marketplace/runtime plugin."""
    package = next(item for item in catalog["packages"] if item["name"] == "agentic-workflows")
    skills = repository_path(catalog["harnesses"]["opencode"]["skills_path"])
    if skills.name != "skills" or "opencode" not in package["harnesses"]:
        raise CatalogError("OpenCode skills_path must end in skills and the bundle must support opencode")
    if skills.parent != ROOT / "generated" / "opencode" / package["name"]:
        raise CatalogError("OpenCode skills_path must be generated/opencode/agentic-workflows/skills")
    return portable_package_files(
        catalog, package, "opencode", root / skills.parent.relative_to(ROOT)
    )


def git_file_mode(mode: int) -> int:
    return 0o755 if mode & stat.S_IXUSR else 0o644


def distribution_files(catalog: dict[str, Any], root: Path) -> list[MaterializedFile]:
    package = next(item for item in catalog["packages"] if item["name"] == "agentic-workflows")
    source = ROOT / package["path"]
    manifest = source / ".codex-plugin" / "plugin.json"
    if manifest.resolve() != manifest:
        raise CatalogError("distribution manifest path must not traverse symlinks")
    skills_path = catalog["harnesses"]["opencode"]["skills_path"]
    config = {
        "$schema": "https://opencode.ai/config.json",
        "skills": [f"./{skills_path}"],
    }
    files = [
        *claude_package_files(catalog, package, root),
        *opencode_package_files(catalog, root),
        MaterializedFile(
            CATALOG_PATH,
            root / "opencode.json",
            (json.dumps(config, indent=2) + "\n").encode("utf-8"),
            0o644,
        ),
    ]
    return [
        MaterializedFile(item.source, item.destination, item.content, git_file_mode(item.mode))
        for item in files
    ]


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
