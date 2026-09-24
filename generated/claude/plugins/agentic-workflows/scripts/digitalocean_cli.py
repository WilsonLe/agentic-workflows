#!/usr/bin/env python3
"""Run DigitalOcean CLI commands with protected API-token credentials."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from account_credential_common import CredentialError, load_credential, redact_exact

CREDENTIALS = Path.home() / ".config" / "agentic-workflows" / "digitalocean" / "credentials.json"
WRITE_CONFIRMATION = "I_APPROVE_DIGITALOCEAN_WRITE"
BLOCKED = {"auth", "completion"}


def is_read_only(arguments: Sequence[str]) -> bool:
    if not arguments:
        raise CredentialError("a doctl command is required after --")
    if arguments[0] in BLOCKED:
        raise CredentialError(f"doctl {arguments[0]} is not supported by this launcher")
    if any(
        argument == "--access-token" or argument.startswith("--access-token=")
        for argument in arguments
    ):
        raise CredentialError("access tokens are not accepted in command arguments")
    if any(item in {"--help", "-h", "--version"} for item in arguments):
        return True
    positionals: list[str] = []
    value_flags = {"--context", "--output", "--format", "--timeout"}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in value_flags:
            if index + 1 >= len(arguments):
                raise CredentialError(f"{argument} requires a value")
            index += 2
            continue
        if argument.startswith("-"):
            index += 1
            continue
        positionals.append(argument)
        index += 1
    return (
        "get" in positionals[:3]
        or "list" in positionals[:3]
        or positionals[:1] == ["version"]
    )


def run_doctl(
    token: str,
    arguments: Sequence[str],
    *,
    executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if any(token in argument for argument in arguments):
        raise CredentialError("the access token must never appear in command arguments")
    selected = executable or shutil.which("doctl")
    if selected is None:
        raise CredentialError("doctl is not installed or not available on PATH")
    environment = os.environ.copy()
    for name in ("DIGITALOCEAN_ACCESS_TOKEN", "DIGITALOCEAN_TOKEN"):
        environment.pop(name, None)
    environment["DIGITALOCEAN_ACCESS_TOKEN"] = token
    try:
        return subprocess.run(
            [selected, *arguments],
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise CredentialError("doctl could not be started") from error


def verify_token(token: str, *, executable: str | None = None) -> dict[str, object]:
    result = run_doctl(
        token,
        ["--context", "default", "account", "get", "--output", "json"],
        executable=executable,
    )
    if result.returncode != 0:
        raise CredentialError("DigitalOcean read-only account verification failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise CredentialError("DigitalOcean returned invalid account JSON") from error
    if not isinstance(payload, (dict, list)):
        raise CredentialError("DigitalOcean returned an unknown account shape")
    return {"provider": "digitalocean", "token_type": "personal_access_token", "status": "active"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file", type=Path, default=CREDENTIALS)
    parser.add_argument("--confirm-write")
    parser.add_argument("doctl_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = list(args.doctl_args)
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    try:
        read_only = is_read_only(arguments)
        if not read_only and args.confirm_write != WRITE_CONFIRMATION:
            raise CredentialError(
                f"writes require --confirm-write {WRITE_CONFIRMATION}"
            )
        record = load_credential(
            args.credentials_file,
            provider="digitalocean",
            token_types={"personal_access_token"},
        )
        token = str(record["token"])
        result = run_doctl(token, arguments)
        if result.stdout:
            sys.stdout.write(
                redact_exact(result.stdout, [token], "[REDACTED_DIGITALOCEAN_TOKEN]")
            )
        if result.stderr:
            sys.stderr.write(
                redact_exact(result.stderr, [token], "[REDACTED_DIGITALOCEAN_TOKEN]")
            )
        raise SystemExit(result.returncode)
    except CredentialError as error:
        print(f"DigitalOcean command refused: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
