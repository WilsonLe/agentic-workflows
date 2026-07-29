#!/usr/bin/env python3
"""Install and verify a protected Excalidraw personal API key."""

from __future__ import annotations

import argparse
import json
import stat
import sys
from pathlib import Path

from excalidraw_credential_common import (
    CredentialError,
    archive_source,
    atomic_private_write,
    encode_credential,
    inspect_source,
    read_private_text,
    validate_private_file,
    validate_token,
)
from excalidraw_api import request_json

DESTINATION = Path.home() / ".config" / "amsoft" / "excalidraw" / "credentials.json"
PERSONAL_CONFIRMATION = "I_CONFIRM_EXCALIDRAW_PERSONAL_KEY"
SECURE_SOURCE_CONFIRMATION = "I_AUTHORIZE_SECURING_EXCALIDRAW_SOURCE"


def read_token(source: Path) -> str:
    text = read_private_text(source).strip()
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise CredentialError("the selected JSON key file is invalid") from error
        if not isinstance(payload, dict) or set(payload) != {"token_type", "token"}:
            raise CredentialError(
                "Excalidraw JSON sources must contain exactly token_type and token"
            )
        if payload.get("token_type") != "personal":
            raise CredentialError(
                "only a declared personal Excalidraw key is supported"
            )
        return validate_token(payload.get("token"))
    return validate_token(text)


def secure_source(source: Path, confirmation: str | None) -> Path:
    expanded = inspect_source(source, allow_broad_mode=True)
    current_mode = stat.S_IMODE(expanded.stat().st_mode)
    if current_mode & 0o077:
        if confirmation != SECURE_SOURCE_CONFIRMATION:
            raise CredentialError(
                "the source is broadly readable; explicit secure-source confirmation is required"
            )
        try:
            expanded.chmod(0o600)
        except OSError as error:
            raise CredentialError(
                "the source permissions could not be secured"
            ) from error
    return inspect_source(expanded)


def verify(token: str) -> dict[str, object]:
    payload, _ = request_json(
        token,
        "GET",
        "/collections",
        query={"limit": "1", "offset": "0"},
    )
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise CredentialError("Excalidraw returned an unknown collections response")
    return {"route": "GET /collections?limit=1&offset=0", "authenticated": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    parser.add_argument("--token-type", choices=("personal",), required=True)
    parser.add_argument("--confirm-personal-key", required=True)
    parser.add_argument("--secure-source", action="store_true")
    parser.add_argument("--confirm-secure-source")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--archive-source", action="store_true")
    args = parser.parse_args()
    if args.confirm_personal_key != PERSONAL_CONFIRMATION:
        print(
            "Excalidraw credential setup failed: personal-key confirmation is invalid",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if args.archive_source and not args.verify:
        print(
            "Excalidraw credential setup failed: --archive-source requires --verify",
            file=sys.stderr,
        )
        raise SystemExit(1)
    previous = None
    installed = False
    try:
        if args.destination.exists() or args.destination.is_symlink():
            validate_private_file(args.destination)
            previous = args.destination.read_bytes()
        source = secure_source(
            args.source,
            args.confirm_secure_source if args.secure_source else None,
        )
        token = read_token(source)
        atomic_private_write(
            args.destination, encode_credential(token), replace=args.replace
        )
        installed = True
        verification = verify(token) if args.verify else None
        archived = archive_source(source) if args.archive_source else None
        print(
            json.dumps(
                {
                    "provider": "excalidraw",
                    "token_type": "personal",
                    "installed": True,
                    "verified": verification is not None,
                    "verification_route": verification["route"]
                    if verification
                    else None,
                    "source_archived": archived is not None,
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
        print(f"Excalidraw credential setup failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
