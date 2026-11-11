#!/usr/bin/env python3
"""Copy the protected OpenRouter key between linked Git worktrees."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Isolated Python omits the script directory. Keep standard-library imports first.
sys.path.append(str(Path(__file__).resolve().parent))

from account_credential_common import CredentialError, copy_openrouter_key  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--destination-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        copied = copy_openrouter_key(args.source_root, args.destination_root)
    except CredentialError as error:
        print(f"OpenRouter key copy failed: {error}", file=sys.stderr)
        return 1
    print("OpenRouter key copied." if copied else "OpenRouter key already present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
