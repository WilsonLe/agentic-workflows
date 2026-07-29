#!/usr/bin/env python3
"""Generate or verify mirrored plugin package files from canonical sources."""

from __future__ import annotations

import argparse

from plugin_catalog import (
    CatalogError,
    load_catalog,
    marketplace_difference,
    mirror_differences,
    write_marketplace,
    write_mirrors,
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
            write_mirrors(catalog)
            write_marketplace(catalog)
        differences = mirror_differences(catalog)
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
