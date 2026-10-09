#!/usr/bin/env python3
"""Install a Railway account token without displaying secret material."""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

from account_credential_common import (
    CredentialError,
    atomic_private_write,
    git_container,
    validate_credential_location,
)

DESTINATION = Path.home() / ".config" / "agentic-workflows" / "railway" / "credentials.json"
CONFIRMATION = "I_CONFIRM_RAILWAY_ACCOUNT_TOKEN"
MAX_SOURCE_BYTES = 65536


def fail(message: str) -> NoReturn:
    print(f"Credential setup failed: {message}", file=sys.stderr)
    raise SystemExit(1)


try:
    from typing import NoReturn
except ImportError:  # pragma: no cover - Python 3.10 provides NoReturn
    NoReturn = Any  # type: ignore[misc,assignment]


def validate_token(value: Any) -> str:
    if not isinstance(value, str) or not value:
        fail("the selected file does not contain a non-empty token")
    if any(character.isspace() for character in value):
        fail("the selected token must be a single value without whitespace")
    if len(value.encode("utf-8")) > MAX_SOURCE_BYTES:
        fail("the selected token is unexpectedly large")
    return value


def read_source(path: Path) -> str:
    expanded = path.expanduser()
    try:
        file_stat = expanded.lstat()
    except FileNotFoundError:
        fail("the selected path does not exist")
    except OSError:
        fail("the selected path cannot be inspected")
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        fail("the selected path must be a regular file, not a symlink")
    if git_container(expanded) is not None:
        fail("the selected credential file must be outside a Git worktree")
    if file_stat.st_size > MAX_SOURCE_BYTES:
        fail("the selected credential file is unexpectedly large")
    try:
        raw = expanded.read_bytes()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeError):
        fail("the selected credential file is not readable UTF-8")
    stripped = text.strip()
    if not stripped:
        fail("the selected credential file is empty")
    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            fail("the selected JSON credential file is invalid")
        if not isinstance(payload, dict) or set(payload) != {"token_type", "token"}:
            fail("JSON credentials must contain exactly token_type and token")
        if payload.get("token_type") != "account":
            fail("only token_type account is supported")
        return validate_token(payload.get("token"))
    return validate_token(stripped)


def validate_existing_destination(path: Path, replace: bool) -> None:
    try:
        file_stat = path.lstat()
    except FileNotFoundError:
        return
    except OSError:
        fail("the credential destination cannot be inspected")
    if not replace:
        fail("protected credentials already exist; use --replace after confirming the source")
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        fail("the existing credential destination is not a regular file")
    if file_stat.st_uid != os.getuid() or stat.S_IMODE(file_stat.st_mode) != 0o400:
        fail("existing credentials must be owned by the current user with mode 0400")


def prepare_directory(path: Path) -> None:
    try:
        path.mkdir(parents=True, mode=0o700, exist_ok=True)
        directory_stat = path.lstat()
    except OSError:
        fail("the protected credential directory cannot be created")
    if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(directory_stat.st_mode):
        fail("the protected credential directory is not a regular directory")
    if directory_stat.st_uid != os.getuid():
        fail("the protected credential directory is not owned by the current user")
    try:
        path.chmod(0o700)
    except OSError:
        fail("the protected credential directory cannot be secured")


def install(token: str, destination: Path, replace: bool) -> None:
    expanded = Path(os.path.abspath(destination.expanduser()))
    payload = json.dumps(
        {"token_type": "account", "token": token},
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    try:
        atomic_private_write(expanded, payload, replace=replace, project_provider="railway")
    except CredentialError as error:
        fail(str(error))
    print(f"Railway account credentials installed at {expanded}")
    print("Credential type: account")
    print("Source file preserved.")


def verify(destination: Path) -> None:
    launcher = Path(__file__).with_name("railway_cli.py")
    result = subprocess.run(
        [
            sys.executable,
            str(launcher),
            "--credentials-file",
            str(destination),
            "--",
            "whoami",
            "--json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail("Railway read-only account verification failed")


def archive_source(source: Path) -> Path:
    expanded = source.expanduser().resolve(strict=True)
    archive = Path.home() / ".config" / "agentic-workflows" / "railway" / "imported-sources"
    prepare_directory(archive)
    destination = archive / expanded.name
    if destination.exists() or destination.is_symlink():
        fail("the selected source name already exists in the protected archive")
    try:
        os.replace(expanded, destination)
        destination.chmod(0o400)
    except OSError:
        fail("the verified source could not be archived safely")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to a plaintext or JSON account-token file")
    parser.add_argument(
        "--destination",
        type=Path,
        default=DESTINATION,
        help="Protected destination; use the project .cli/railway/credentials.json path",
    )
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--archive-source", action="store_true")
    parser.add_argument("--confirm-account-token", required=True)
    args = parser.parse_args()
    if args.archive_source and not args.verify:
        fail("--archive-source requires --verify")
    if args.confirm_account_token != CONFIRMATION:
        fail(
            "confirm that the token was created with No workspace by passing "
            f"--confirm-account-token {CONFIRMATION}"
        )
    try:
        validate_credential_location(args.destination, project_provider="railway")
    except CredentialError as error:
        fail(str(error))
    token = read_source(args.source)
    previous = None
    if args.destination.exists() or args.destination.is_symlink():
        validate_existing_destination(args.destination, True)
        previous = args.destination.read_bytes()
    try:
        install(token, args.destination, args.replace)
        if args.verify:
            verify(args.destination)
        if args.archive_source:
            archive_source(args.source)
        if args.verify:
            print("Read-only account verification: passed")
        if args.archive_source:
            print("Source archived in the protected Railway imported-sources directory.")
    except SystemExit:
        try:
            if previous is None:
                args.destination.unlink(missing_ok=True)
            else:
                install(
                    validate_token(json.loads(previous)["token"]),
                    args.destination,
                    True,
                )
        except (OSError, KeyError, json.JSONDecodeError, SystemExit):
            pass
        raise


if __name__ == "__main__":
    main()
