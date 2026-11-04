#!/usr/bin/env python3
"""Generate or verify mirrored plugin package files from canonical sources."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from plugin_catalog import (
    CatalogError,
    ROOT,
    distribution_differences,
    distribution_files,
    load_catalog,
    marketplace_difference,
    claude_differences,
    mirror_differences,
    opencode_differences,
    skill_documentation_differences,
    write_claude_packages,
    write_materialized_files,
    write_marketplace,
    write_mirrors,
    write_opencode_package,
    write_skill_documentation,
)


def build_distribution(catalog: dict, output: Path) -> None:
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise CatalogError(f"distribution output must be a new or empty directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".plugin-build-", dir=output.parent) as scratch:
        staged = Path(scratch) / "distribution"
        write_materialized_files(distribution_files(catalog, staged))
        if output.exists():
            output.rmdir()  # Refuse to overwrite files that appeared during the build.
        staged.rename(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify committed mirrors")
    mode.add_argument("--write", action="store_true", help="materialize committed mirrors")
    mode.add_argument("--build", type=Path, metavar="DIR", help="build portable distribution")
    mode.add_argument("--check-build", type=Path, metavar="DIR", help="verify portable distribution")
    arguments = parser.parse_args()

    try:
        catalog = load_catalog()
        distribution = arguments.build or arguments.check_build
        if distribution is not None:
            if distribution.is_symlink():
                raise CatalogError("distribution directory must not be a symlink")
            distribution = distribution.resolve()
            if distribution.is_relative_to(ROOT):
                raise CatalogError("distribution directory must be outside the source checkout")
            if arguments.build is not None:
                build_distribution(catalog, distribution)
            differences = distribution_differences(catalog, distribution)
            if differences:
                for difference in differences:
                    print(difference)
                return 1
            print("Portable plugin distribution verified.")
            return 0
        if arguments.write:
            # Bootstrap newly declared bundled skills before writing their docs.
            write_mirrors(catalog)
            write_skill_documentation(catalog)
            write_mirrors(catalog)
            write_marketplace(catalog)
            write_claude_packages(catalog)
            write_opencode_package(catalog)
        differences = mirror_differences(catalog)
        differences.extend(skill_documentation_differences(catalog))
        differences.extend(claude_differences(catalog))
        differences.extend(opencode_differences(catalog))
        marketplace = marketplace_difference(catalog)
        if marketplace:
            differences.append(marketplace)
    except (CatalogError, OSError) as error:
        parser.error(str(error))

    if differences:
        for difference in differences:
            print(difference)
        print("Run `uv run python scripts/generate_plugin_packages.py --write` to synchronize.")
        return 1

    action = "generated and verified" if arguments.write else "verified"
    print(f"Plugin package mirrors {action}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
