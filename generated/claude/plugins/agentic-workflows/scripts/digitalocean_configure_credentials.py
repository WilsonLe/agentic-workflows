#!/usr/bin/env python3
"""Install and optionally verify a protected DigitalOcean access token."""

# /// script
# dependencies = ["PyYAML==6.0.3"]
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from account_credential_common import (
    CredentialError,
    archive_sources,
    atomic_private_write,
    encode_credential,
    read_private_text,
    validate_private_file,
    validate_token,
)
from digitalocean_cli import verify_token

DESTINATION = Path.home() / ".config" / "agentic-workflows" / "digitalocean" / "credentials.json"


def read_token(source: Path) -> str:
    text = read_private_text(source).strip()
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise CredentialError("the selected JSON credential file is invalid") from error
        if not isinstance(payload, dict) or set(payload) != {"token"}:
            raise CredentialError("DigitalOcean JSON sources must contain exactly token")
        return validate_token(payload.get("token"))
    return validate_token(text)


def yaml_token(config_source: Path) -> str:
    text = read_private_text(config_source, maximum_bytes=1_048_576)
    try:
        payload: Any = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise CredentialError("the selected doctl YAML is invalid") from error
    if not isinstance(payload, dict) or "access-token" not in payload:
        raise CredentialError("the selected doctl YAML has no access-token")
    return validate_token(payload.get("access-token"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--doctl-config", type=Path)
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--archive-source", action="store_true")
    args = parser.parse_args()
    if args.archive_source and not args.verify:
        print(
            "DigitalOcean credential setup failed: --archive-source requires --verify",
            file=sys.stderr,
        )
        raise SystemExit(1)
    previous = None
    installed = False
    try:
        if args.destination.exists() or args.destination.is_symlink():
            validate_private_file(args.destination)
            previous = args.destination.read_bytes()
        token = read_token(args.source)
        if args.doctl_config is not None and yaml_token(args.doctl_config) != token:
            raise CredentialError("the doctl YAML access-token does not match the selected token")
        atomic_private_write(
            args.destination,
            encode_credential("digitalocean", "personal_access_token", token),
            replace=args.replace,
        )
        installed = True
        verification = verify_token(token) if args.verify else None
        sources = [args.source]
        if args.doctl_config is not None:
            sources.append(args.doctl_config)
        archived = archive_sources("digitalocean", sources) if args.archive_source else []
        print(
            json.dumps(
                {
                    "provider": "digitalocean",
                    "token_type": "personal_access_token",
                    "installed": True,
                    "verified": verification is not None,
                    "source_archived": bool(archived),
                },
                sort_keys=True,
            )
        )
    except CredentialError as error:
        if previous is not None and args.destination.exists():
            try:
                atomic_private_write(args.destination, previous, replace=True)
            except CredentialError:
                pass
        elif installed:
            try:
                args.destination.unlink()
            except OSError:
                pass
        print(f"DigitalOcean credential setup failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
