#!/usr/bin/env python3
"""Run non-interactive Railway CLI commands with protected account credentials."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

CREDENTIALS = Path.home() / ".config" / "amsoft" / "railway" / "credentials.json"
WRITE_CONFIRMATION = "I_APPROVE_RAILWAY_WRITE"
PRODUCTION_CONFIRMATION = "I_APPROVE_RAILWAY_PRODUCTION"
DESTRUCTIVE_CONFIRMATION = "I_APPROVE_RAILWAY_DESTRUCTIVE"
SENSITIVE_CONFIRMATION = "I_APPROVE_RAILWAY_SENSITIVE_READ"
BLOCKED_COMMANDS = {"connect", "dev", "login", "logout", "run", "shell", "ssh"}
READ_ONLY_TOP_LEVEL = {"list", "logs", "status", "whoami"}
DESTRUCTIVE_TOP_LEVEL = {"delete", "down"}
HELP_FLAGS = {"--help", "-h", "--version", "-V"}


def fail(message: str, code: int = 1) -> NoReturn:
    print(f"Railway command refused: {message}", file=sys.stderr)
    raise SystemExit(code)


try:
    from typing import NoReturn
except ImportError:  # pragma: no cover
    NoReturn = Any  # type: ignore[misc,assignment]


def validate_token(value: Any) -> str:
    if not isinstance(value, str) or not value:
        fail("protected credentials are invalid")
    if any(character.isspace() for character in value):
        fail("protected credentials are invalid")
    return value


def load_credentials(path: Path) -> str:
    expanded = path.expanduser()
    try:
        parent_stat = expanded.parent.lstat()
        file_stat = expanded.lstat()
    except FileNotFoundError:
        fail("protected credentials are not configured")
    except OSError:
        fail("protected credentials cannot be inspected")
    if (
        stat.S_ISLNK(parent_stat.st_mode)
        or not stat.S_ISDIR(parent_stat.st_mode)
        or parent_stat.st_uid != os.getuid()
        or stat.S_IMODE(parent_stat.st_mode) != 0o700
    ):
        fail("credential directory must be owned by the current user with mode 0700")
    if (
        stat.S_ISLNK(file_stat.st_mode)
        or not stat.S_ISREG(file_stat.st_mode)
        or file_stat.st_uid != os.getuid()
        or stat.S_IMODE(file_stat.st_mode) != 0o400
    ):
        fail("credential file must be owned by the current user with mode 0400")
    try:
        payload = json.loads(expanded.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        fail("protected credentials are invalid")
    if (
        not isinstance(payload, dict)
        or set(payload) != {"token_type", "token"}
        or payload.get("token_type") != "account"
    ):
        fail("only protected Railway account credentials are supported")
    return validate_token(payload.get("token"))


def is_help_or_version(arguments: Sequence[str]) -> bool:
    if len(arguments) == 1:
        return arguments[0] in HELP_FLAGS
    return (
        len(arguments) <= 3
        and arguments[-1] in HELP_FLAGS
        and all(not argument.startswith("-") for argument in arguments[:-1])
    )


def command_kind(arguments: Sequence[str]) -> tuple[bool, bool]:
    if not arguments:
        fail("a Railway command is required after --")
    if is_help_or_version(arguments):
        return False, False
    command = arguments[0]
    if command in BLOCKED_COMMANDS:
        fail(
            f"{command} is interactive or can expose service secrets and is not supported "
            "by this launcher"
        )
    if command == "variable-names":
        return False, False
    if command == "variable":
        if len(arguments) < 2 or arguments[1] == "list":
            fail("use variable-names; railway variable list can expose secret values")
        return True, arguments[1] == "delete"
    if command in READ_ONLY_TOP_LEVEL:
        return False, False
    if command == "deployment" and len(arguments) > 1 and arguments[1] == "list":
        return False, False
    if command == "project" and len(arguments) > 1 and arguments[1] == "list":
        return False, False
    if command == "service" and len(arguments) > 1 and arguments[1] in {"logs", "status"}:
        return False, False
    if command == "environment" and len(arguments) > 1 and arguments[1] == "config":
        return False, False
    if command == "volume" and len(arguments) > 1 and arguments[1] == "list":
        return False, False
    destructive = command in DESTRUCTIVE_TOP_LEVEL or "delete" in arguments or "detach" in arguments
    return True, destructive


def validate_secret_channels(arguments: Sequence[str]) -> None:
    if is_help_or_version(arguments):
        return
    if any(
        argument == "--2fa-code" or argument.startswith("--2fa-code=")
        for argument in arguments
    ):
        fail("2FA codes are not accepted in command arguments")
    if arguments[:2] == ["variable", "set"]:
        if "--stdin" not in arguments:
            fail("variable set requires --stdin so the value is not placed in argv")
        if any("=" in argument for argument in arguments[2:]):
            fail("variable values must not appear in command arguments")
    if arguments[:1] == ["deploy"] and any(
        argument in {"-v", "--variable"} or argument.startswith("--variable=")
        for argument in arguments[1:]
    ):
        fail("template variable values are not accepted in command arguments")


def is_log_read(arguments: Sequence[str]) -> bool:
    return arguments[:1] == ["logs"] or arguments[:2] == ["service", "logs"]


def require_bounded_logs(args: argparse.Namespace, arguments: Sequence[str]) -> None:
    if not is_log_read(arguments) or is_help_or_version(arguments):
        return
    if args.confirm_sensitive_output != SENSITIVE_CONFIRMATION:
        fail(
            "logs may contain application secrets; pass "
            f"--confirm-sensitive-output {SENSITIVE_CONFIRMATION}"
        )
    bounded_flags = {"--lines", "-n", "--since", "-S", "--until", "-U"}
    if not any(argument in bounded_flags for argument in arguments):
        fail("logs must be bounded with --lines, --since, or --until")


def require_approvals(args: argparse.Namespace, railway_args: Sequence[str]) -> None:
    validate_secret_channels(railway_args)
    require_bounded_logs(args, railway_args)
    is_write, is_destructive = command_kind(railway_args)
    if not is_write:
        return
    if args.target_class is None:
        fail("writes require --target-class non-production, production, or account")
    if args.confirm_write != WRITE_CONFIRMATION:
        fail(f"writes require --confirm-write {WRITE_CONFIRMATION}")
    if args.target_class == "production" and args.confirm_production != PRODUCTION_CONFIRMATION:
        fail(
            "production writes require "
            f"--confirm-production {PRODUCTION_CONFIRMATION}"
        )
    if is_destructive and args.confirm_destructive != DESTRUCTIVE_CONFIRMATION:
        fail(
            "destructive writes require "
            f"--confirm-destructive {DESTRUCTIVE_CONFIRMATION}"
        )


def sanitized_environment(token: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("RAILWAY_TOKEN", None)
    environment.pop("RAILWAY_API_TOKEN", None)
    environment["RAILWAY_API_TOKEN"] = token
    return environment


def redact(value: str, token: str) -> str:
    return value.replace(token, "[REDACTED_RAILWAY_ACCOUNT_TOKEN]")


def run_process(
    executable: str,
    arguments: Sequence[str],
    token: str,
) -> subprocess.CompletedProcess[str]:
    if any(token in argument for argument in arguments):
        fail("the account token must never appear in command arguments")
    try:
        return subprocess.run(
            [executable, *arguments],
            env=sanitized_environment(token),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        fail("the Railway CLI could not be started", 2)


def emit_result(result: subprocess.CompletedProcess[str], token: str) -> int:
    if result.stdout:
        sys.stdout.write(redact(result.stdout, token))
    if result.stderr:
        sys.stderr.write(redact(result.stderr, token))
    return result.returncode


def variable_names(
    executable: str,
    arguments: Sequence[str],
    token: str,
) -> int:
    allowed_flags = {"--environment", "--service", "-e", "-s"}
    index = 0
    while index < len(arguments):
        if arguments[index] not in allowed_flags or index + 1 >= len(arguments):
            fail("variable-names accepts only --service and --environment")
        index += 2
    command = ["variable", "list", "--json", *arguments]
    result = run_process(executable, command, token)
    if result.returncode != 0:
        print(
            "Railway variable inventory failed; raw output was suppressed because it "
            "may contain variable values",
            file=sys.stderr,
        )
        return result.returncode
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        fail("Railway returned an unknown variable-list shape; no values were displayed", 2)
    if not isinstance(payload, dict) or not all(isinstance(key, str) for key in payload):
        fail("Railway returned an unknown variable-list shape; no values were displayed", 2)
    print(json.dumps({"variable_names": sorted(payload)}, indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--credentials-file",
        type=Path,
        default=CREDENTIALS,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--target-class",
        choices=("non-production", "production", "account"),
    )
    parser.add_argument("--confirm-write")
    parser.add_argument("--confirm-production")
    parser.add_argument("--confirm-destructive")
    parser.add_argument("--confirm-sensitive-output")
    parser.add_argument("railway_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    railway_args = list(args.railway_args)
    if railway_args[:1] == ["--"]:
        railway_args = railway_args[1:]
    require_approvals(args, railway_args)
    token = load_credentials(args.credentials_file)
    executable = shutil.which("railway")
    if executable is None:
        fail("railway is not installed or not available on PATH", 2)
    if railway_args[0] == "variable-names":
        code = variable_names(executable, railway_args[1:], token)
    else:
        result = run_process(executable, railway_args, token)
        code = emit_result(result, token)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
