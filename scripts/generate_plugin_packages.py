#!/usr/bin/env python3
"""Generate or verify mirrored plugin package files from canonical sources."""

from __future__ import annotations

import argparse

from plugin_catalog import (
    CatalogError,
    load_catalog,
    marketplace_difference,
    claude_differences,
    mirror_differences,
    skill_documentation_differences,
    write_claude_packages,
    write_marketplace,
    write_mirrors,
    write_skill_documentation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify committed mirrors")
    mode.add_argument("--write", action="store_true", help="materialize committed mirrors")
    arguments = parser.parse_args()

    try:
        catalog = load_catalog()
        if arguments.write:
            # Bootstrap newly declared bundled skills before writing their docs.
            write_mirrors(catalog)
            write_skill_documentation(catalog)
            write_mirrors(catalog)
            write_marketplace(catalog)
            write_claude_packages(catalog)
        differences = mirror_differences(catalog)
        differences.extend(skill_documentation_differences(catalog))
        differences.extend(claude_differences(catalog))
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
