#!/usr/bin/env python3
"""Install and optionally verify a protected Cloudflare API token."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from account_credential_common import (
    CredentialError,
    archive_sources,
    atomic_private_write,
    encode_credential,
    read_private_text,
    validate_private_file,
    validate_token,
)
from cloudflare_api import verify_token

DESTINATION = Path.home() / ".config" / "agentic-workflows" / "cloudflare" / "credentials.json"
TOKEN_TYPES = {"user_api_token", "account_api_token"}


def classify_token(token: str, requested: str) -> str:
    if token.startswith("cfk_"):
        raise CredentialError("Cloudflare Global API Keys are not supported")
    detected = None
    if token.startswith("cfut_"):
        detected = "user_api_token"
    elif token.startswith("cfat_"):
        detected = "account_api_token"
    if requested == "auto":
        if detected is None:
            raise CredentialError(
                "the token type is unknown; select user_api_token or account_api_token"
            )
        return detected
    if requested not in TOKEN_TYPES:
        raise CredentialError("the selected Cloudflare token type is unsupported")
    if detected is not None and detected != requested:
        raise CredentialError("the selected token type conflicts with its supported prefix")
    return requested


def read_token(source: Path) -> str:
    text = read_private_text(source).strip()
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise CredentialError("the selected JSON credential file is invalid") from error
        if not isinstance(payload, dict) or set(payload) != {"token"}:
            raise CredentialError("Cloudflare JSON sources must contain exactly token")
        return validate_token(payload.get("token"))
    return validate_token(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--token-type",
        choices=("auto", "user_api_token", "account_api_token"),
        default="auto",
    )
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    parser.add_argument("--account-id", help=argparse.SUPPRESS)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--archive-source", action="store_true")
    args = parser.parse_args()
    if args.archive_source and not args.verify:
        print(
            "Cloudflare credential setup failed: --archive-source requires --verify",
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
        token_type = classify_token(token, args.token_type)
        atomic_private_write(
            args.destination,
            encode_credential("cloudflare", token_type, token),
            replace=args.replace,
        )
        installed = True
        verification = None
        if args.verify:
            verification = verify_token(token, token_type, args.account_id)
        archived = []
        if args.archive_source:
            archived = archive_sources("cloudflare", [args.source])
        output = {
            "provider": "cloudflare",
            "token_type": token_type,
            "installed": True,
            "verified": verification is not None,
            "source_archived": bool(archived),
        }
        print(json.dumps(output, sort_keys=True))
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
        print(f"Cloudflare credential setup failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
