#!/usr/bin/env python3
"""Read-only, secret-safe diagnostics for installed Codex plugins."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable, Sequence


Runner = Callable[..., subprocess.CompletedProcess[str]]
IGNORED_PARTS = {".git", "__pycache__", ".DS_Store"}
AUTHORING_FALLBACK = (
    "Use the repository catalog, deterministic generator, package validator, "
    "registry checks, and installed-state diagnostic."
)


def candidate_paths(explicit: Sequence[str]) -> list[str]:
    candidates = list(explicit)
    discovered = shutil.which("codex")
    if discovered:
        candidates.append(discovered)
    candidates.extend(
        [
            str(Path.home() / ".local" / "bin" / "codex"),
            "/Applications/ChatGPT.app/Contents/Resources/codex",
        ]
    )
    return list(dict.fromkeys(candidates))


def probe_codex_candidates(
    candidates: Sequence[str],
    runner: Runner = subprocess.run,
) -> tuple[str | None, list[dict[str, object]]]:
    probes: list[dict[str, object]] = []
    selected: str | None = None
    for candidate in candidates:
        result: dict[str, object] = {"path": candidate, "usable": False}
        try:
            completed = runner(
                [candidate, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            result["returncode"] = completed.returncode
            if completed.returncode == 0:
                result["usable"] = True
                result["version"] = completed.stdout.strip().splitlines()[0]
                if selected is None:
                    selected = candidate
            else:
                result["error"] = "launcher returned non-zero"
        except (OSError, subprocess.SubprocessError) as error:
            result["error"] = type(error).__name__
        probes.append(result)
    return selected, probes


def tree_hashes(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"package tree contains a symlink at {relative.as_posix()}")
        if (
            not path.is_file()
            or path.suffix == ".pyc"
            or any(part in IGNORED_PARTS for part in relative.parts)
        ):
            continue
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def parity_report(expected: Path, actual: Path) -> dict[str, object]:
    expected_hashes = tree_hashes(expected)
    actual_hashes = tree_hashes(actual)
    differences = sorted(
        name
        for name in expected_hashes.keys() | actual_hashes.keys()
        if expected_hashes.get(name) != actual_hashes.get(name)
    )
    return {
        "expected_path": str(expected),
        "actual_path": str(actual),
        "actual_exists": actual.is_dir(),
        "matches": bool(expected_hashes) and not differences,
        "difference_count": len(differences),
        "differences": differences[:50],
        "differences_truncated": len(differences) > 50,
    }


def expected_package_paths(specifications: Sequence[str]) -> dict[str, Path]:
    results: dict[str, Path] = {}
    for specification in specifications:
        name, separator, path_text = specification.partition("=")
        if not separator or not name or not path_text or name in results:
            raise ValueError("expected package must use unique NAME=PATH")
        results[name] = Path(path_text).expanduser().resolve()
    return results


def analyze_plugin_list(
    payload: object,
    cache_root: Path,
    authoritative_marketplace: str | None = None,
    expected_packages: dict[str, Path] | None = None,
) -> dict[str, object]:
    if not isinstance(payload, dict) or not isinstance(payload.get("installed"), list):
        raise ValueError("plugin list must contain an installed array")
    installed: list[dict[str, object]] = []
    enabled_by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    for raw in payload["installed"]:
        if not isinstance(raw, dict):
            raise ValueError("installed plugin entry must be an object")
        name = raw.get("name")
        marketplace = raw.get("marketplaceName")
        version = raw.get("version")
        if not all(isinstance(value, str) and value for value in (name, marketplace, version)):
            raise ValueError("installed plugin entry lacks name, marketplace, or version")
        source = raw.get("source")
        source_path = source.get("path") if isinstance(source, dict) else None
        cache_path = cache_root / marketplace / name / version
        record = {
            "plugin_id": raw.get("pluginId"),
            "name": name,
            "marketplace": marketplace,
            "version": version,
            "installed": raw.get("installed") is True,
            "enabled": raw.get("enabled") is True,
            "source_path": source_path,
            "source_exists": isinstance(source_path, str) and Path(source_path).exists(),
            "cache_path": str(cache_path),
            "cache_exists": cache_path.is_dir(),
        }
        installed.append(record)
        if record["installed"] and record["enabled"]:
            enabled_by_name[name].append(record)
    duplicates = {
        name: [record["plugin_id"] for record in records]
        for name, records in sorted(enabled_by_name.items())
        if len(records) > 1
    }
    provider_conflicts = {
        name: [
            {
                "plugin_id": record["plugin_id"],
                "version": record["version"],
                "source_path": record["source_path"],
                "source_exists": record["source_exists"],
                "cache_exists": record["cache_exists"],
            }
            for record in records
        ]
        for name, records in sorted(enabled_by_name.items())
        if len(records) > 1
    }
    authoritative: dict[str, object] = {}
    expected_packages = expected_packages or {}
    if authoritative_marketplace:
        for name, records in sorted(enabled_by_name.items()):
            selected = [
                record
                for record in records
                if record["marketplace"] == authoritative_marketplace
            ]
            if len(selected) != 1:
                authoritative[name] = {
                    "status": "missing" if not selected else "ambiguous",
                    "matching_provider_count": len(selected),
                }
                continue
            record = selected[0]
            verification: dict[str, object] = {
                "status": "selected",
                "plugin_id": record["plugin_id"],
                "version": record["version"],
                "source_exists": record["source_exists"],
                "cache_exists": record["cache_exists"],
                "conflicting_enabled_providers": [
                    other["plugin_id"] for other in records if other is not record
                ],
            }
            expected = expected_packages.get(name)
            if expected is not None:
                manifest = expected / ".codex-plugin" / "plugin.json"
                try:
                    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
                except (OSError, ValueError) as error:
                    raise ValueError(f"cannot read expected manifest for {name}: {error}") from error
                expected_version = manifest_payload.get("version")
                verification["expected_version"] = expected_version
                verification["version_matches"] = record["version"] == expected_version
                source_path = record["source_path"]
                if isinstance(source_path, str):
                    verification["source_parity"] = parity_report(
                        expected, Path(source_path)
                    )
                verification["cache_parity"] = parity_report(
                    expected, Path(record["cache_path"])
                )
            authoritative[name] = verification
    return {
        "installed_count": len(installed),
        "enabled_count": sum(record["enabled"] for record in installed),
        "plugins": installed,
        "duplicate_enabled_names": duplicates,
        "provider_conflicts": provider_conflicts,
        "authoritative_marketplace": authoritative_marketplace,
        "authoritative_providers": authoritative,
        "remediation_plan": [
            "Review duplicate enabled providers and choose one authority per normalized name.",
            "Change provider state only through a separately authorized plugin workflow.",
            "Refresh and reinstall the selected provider, then rerun this diagnostic.",
            "Start a fresh task and verify each affected skill is discovered exactly once.",
        ],
    }


def analyze_required_skills(specifications: Sequence[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for specification in specifications:
        name, separator, path_text = specification.partition("=")
        if not separator or not name or not path_text:
            raise ValueError("required skill must use NAME=PATH")
        path = Path(path_text).expanduser()
        available = path.is_file()
        results.append(
            {
                "name": name,
                "path": str(path),
                "available": available,
                "fallback": None if available else AUTHORING_FALLBACK,
            }
        )
    return results


def load_plugin_payload(path: Path | None, codex: str | None) -> object:
    if path is not None:
        return json.loads(path.read_text(encoding="utf-8"))
    if codex is None:
        raise RuntimeError("no usable Codex launcher")
    completed = subprocess.run(
        [codex, "plugin", "list", "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("Codex plugin list returned non-zero")
    return json.loads(completed.stdout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-list-file", type=Path)
    parser.add_argument("--codex-candidate", action="append", default=[])
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path.home() / ".codex" / "plugins" / "cache",
    )
    parser.add_argument("--required-skill", action="append", default=[])
    parser.add_argument("--authoritative-marketplace")
    parser.add_argument("--expected-package", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected, probes = probe_codex_candidates(candidate_paths(args.codex_candidate))
    report: dict[str, object] = {
        "schema_version": 1,
        "read_only": True,
        "selected_codex": selected,
        "launcher_probes": probes,
    }
    try:
        payload = load_plugin_payload(args.plugin_list_file, selected)
        report["installed_state"] = analyze_plugin_list(
            payload,
            args.cache_root,
            args.authoritative_marketplace,
            expected_package_paths(args.expected_package),
        )
        report["required_skills"] = analyze_required_skills(args.required_skill)
    except (OSError, ValueError, RuntimeError) as error:
        report["error"] = str(error)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    installed_state = report["installed_state"]
    missing_skills = any(not item["available"] for item in report["required_skills"])
    has_duplicates = bool(installed_state["duplicate_enabled_names"])
    return 3 if has_duplicates or missing_skills else 0


if __name__ == "__main__":
    sys.exit(main())
