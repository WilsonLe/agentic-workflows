#!/usr/bin/env python3
"""Shared protected-file primitives for Agentic Workflows account credentials."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any

MAX_CREDENTIAL_BYTES = 65_536
MAX_ARCHIVE_BYTES = 1_048_576
PROJECT_CLI_PROVIDERS = {"railway", "cloudflare", "digitalocean"}


class CredentialError(RuntimeError):
    """A sanitized credential lifecycle failure."""


def _current_uid() -> int | None:
    return os.getuid() if hasattr(os, "getuid") else None


def _owned_by_current_user(file_stat: os.stat_result) -> bool:
    uid = _current_uid()
    return uid is None or file_stat.st_uid == uid


def git_container(path: Path) -> Path | None:
    """Return the enclosing Git worktree, if any."""
    resolved = path.expanduser().resolve(strict=False)
    start = resolved if resolved.is_dir() else resolved.parent
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def validate_credential_location(path: Path, *, project_provider: str | None = None) -> Path | None:
    """Allow legacy non-Git paths or an opted-in provider's ignored .cli store.

    Return the enclosing project root for a permitted project store. Check the
    lexical path before resolving symlinks so a .cli symlink cannot escape the
    worktree and be mistaken for a legacy path. Git failures fail closed.
    """
    expanded = Path(os.path.abspath(path.expanduser()))
    root = next(
        (parent for parent in expanded.parents if (parent / ".git").exists()),
        None,
    )
    if root is None:
        if git_container(expanded) is not None:
            raise CredentialError("credential paths must not alias a Git worktree")
        return None
    relative = expanded.relative_to(root)
    if (
        project_provider not in PROJECT_CLI_PROVIDERS
        or len(relative.parts) < 3
        or relative.parts[:2] != (".cli", project_provider)
    ):
        raise CredentialError(
            "credentials must be outside a Git worktree or in the provider's ignored .cli directory"
        )
    for candidate in (expanded, *expanded.parents):
        if candidate == root:
            break
        try:
            file_stat = candidate.lstat()
        except FileNotFoundError:
            continue
        except OSError as error:
            raise CredentialError("the project credential path cannot be inspected") from error
        if stat.S_ISLNK(file_stat.st_mode) or not _owned_by_current_user(file_stat):
            raise CredentialError("project credential paths must be owned and free of symlinks")
    git_environment = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_PREFIX"):
        git_environment.pop(name, None)
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--", ".cli"],
            capture_output=True, check=False, timeout=10, env=git_environment,
        )
        ignored = [
            subprocess.run(
                ["git", "-C", str(root), "check-ignore", "--quiet", "--no-index", "--", name],
                capture_output=True, check=False, timeout=10, env=git_environment,
            )
            for name in (".cli/", relative.as_posix())
        ]
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CredentialError("project credential Git checks could not complete") from error
    if tracked.returncode != 0 or tracked.stdout or any(item.returncode != 0 for item in ignored):
        raise CredentialError("project .cli credentials must be ignored and untracked")
    return root


def inspect_regular_source(
    path: Path,
    *,
    maximum_bytes: int = MAX_CREDENTIAL_BYTES,
    allow_broad_mode: bool = False,
) -> Path:
    """Validate a current-user-owned regular non-Git source file."""
    expanded = Path(os.path.abspath(path.expanduser()))
    try:
        file_stat = expanded.lstat()
    except FileNotFoundError as error:
        raise CredentialError("the selected source does not exist") from error
    except OSError as error:
        raise CredentialError("the selected source cannot be inspected") from error
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        raise CredentialError("the selected source must be a regular file, not a symlink")
    if not _owned_by_current_user(file_stat):
        raise CredentialError("the selected source is not owned by the current user")
    if not allow_broad_mode and stat.S_IMODE(file_stat.st_mode) & 0o077:
        raise CredentialError("the selected source permissions must be no broader than 0600")
    if file_stat.st_size == 0:
        raise CredentialError("the selected source is empty")
    if file_stat.st_size > maximum_bytes:
        raise CredentialError("the selected source is unexpectedly large")
    if git_container(expanded) is not None:
        raise CredentialError("the selected source must be outside a Git worktree")
    return expanded


def read_private_text(
    path: Path,
    *,
    maximum_bytes: int = MAX_CREDENTIAL_BYTES,
) -> str:
    """Read a validated private UTF-8 source without returning diagnostic content."""
    expanded = inspect_regular_source(path, maximum_bytes=maximum_bytes)
    try:
        raw = expanded.read_bytes()
        return raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise CredentialError("the selected source is not readable UTF-8") from error


def validate_token(value: Any) -> str:
    """Validate a single opaque token without inferring its permissions."""
    if not isinstance(value, str) or not value:
        raise CredentialError("the selected source does not contain a non-empty token")
    if value != value.strip() or any(character.isspace() for character in value):
        raise CredentialError("the selected token must be one value without whitespace")
    if len(value.encode("utf-8")) > MAX_CREDENTIAL_BYTES:
        raise CredentialError("the selected token is unexpectedly large")
    return value


def prepare_private_directory(path: Path) -> Path:
    """Create and verify a private directory."""
    expanded = Path(os.path.abspath(path.expanduser()))
    try:
        expanded.mkdir(parents=True, mode=0o700, exist_ok=True)
        directory_stat = expanded.lstat()
    except OSError as error:
        raise CredentialError("the protected directory cannot be created") from error
    if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(directory_stat.st_mode):
        raise CredentialError("the protected path is not a regular directory")
    if not _owned_by_current_user(directory_stat):
        raise CredentialError("the protected directory is not owned by the current user")
    try:
        expanded.chmod(0o700)
    except OSError as error:
        raise CredentialError("the protected directory cannot be secured") from error
    return expanded


def validate_private_file(
    path: Path, *, mode: int = 0o400, project_provider: str | None = None,
) -> Path:
    """Validate an existing protected regular file."""
    expanded = Path(os.path.abspath(path.expanduser()))
    if project_provider is not None:
        validate_credential_location(expanded, project_provider=project_provider)
    try:
        parent_stat = expanded.parent.lstat()
        file_stat = expanded.lstat()
    except FileNotFoundError as error:
        raise CredentialError("protected credentials are not configured") from error
    except OSError as error:
        raise CredentialError("protected credentials cannot be inspected") from error
    if (
        stat.S_ISLNK(parent_stat.st_mode)
        or not stat.S_ISDIR(parent_stat.st_mode)
        or not _owned_by_current_user(parent_stat)
        or stat.S_IMODE(parent_stat.st_mode) != 0o700
    ):
        raise CredentialError(
            "credential directory must be owned by the current user with mode 0700"
        )
    if (
        stat.S_ISLNK(file_stat.st_mode)
        or not stat.S_ISREG(file_stat.st_mode)
        or not _owned_by_current_user(file_stat)
        or stat.S_IMODE(file_stat.st_mode) != mode
    ):
        raise CredentialError(
            f"credential file must be owned by the current user with mode {mode:04o}"
        )
    return expanded


def atomic_private_write(
    path: Path,
    data: bytes,
    *,
    mode: int = 0o400,
    replace: bool = False,
    project_provider: str | None = None,
) -> None:
    """Atomically write a private file without following destination symlinks."""
    expanded = Path(os.path.abspath(path.expanduser()))
    project_root = validate_credential_location(expanded, project_provider=project_provider)
    if project_root is not None:
        for directory in reversed(expanded.parents):
            if directory != project_root and directory.is_relative_to(project_root):
                prepare_private_directory(directory)
    prepare_private_directory(expanded.parent)
    try:
        existing = expanded.lstat()
    except FileNotFoundError:
        existing = None
    except OSError as error:
        raise CredentialError("the protected destination cannot be inspected") from error
    if existing is not None:
        if not replace:
            raise CredentialError("protected credentials already exist")
        if (
            stat.S_ISLNK(existing.st_mode)
            or not stat.S_ISREG(existing.st_mode)
            or not _owned_by_current_user(existing)
            or stat.S_IMODE(existing.st_mode) != mode
        ):
            raise CredentialError("the existing protected file is unsafe to replace")

    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{expanded.name}.",
            suffix=".tmp",
            dir=expanded.parent,
        )
        temporary = Path(temporary_name)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(mode)
        os.replace(temporary, expanded)
        temporary = None
        if os.name != "nt":
            directory_descriptor = os.open(expanded.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    except OSError as error:
        raise CredentialError("the protected file could not be written atomically") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass
    validate_private_file(expanded, mode=mode, project_provider=project_provider)


def encode_credential(provider: str, token_type: str, token: str) -> bytes:
    """Create the canonical protected credential record."""
    return json.dumps(
        {
            "schema_version": 1,
            "provider": provider,
            "token_type": token_type,
            "token": validate_token(token),
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def load_credential(
    path: Path,
    *,
    provider: str,
    token_types: set[str],
) -> dict[str, str | int]:
    """Load a strict protected credential record."""
    expanded = validate_private_file(
        path, project_provider=provider if provider in PROJECT_CLI_PROVIDERS else None,
    )
    try:
        payload = json.loads(expanded.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CredentialError("protected credentials are invalid") from error
    expected = {"schema_version", "provider", "token_type", "token"}
    if (
        not isinstance(payload, dict)
        or set(payload) != expected
        or payload.get("schema_version") != 1
        or payload.get("provider") != provider
        or payload.get("token_type") not in token_types
    ):
        raise CredentialError(f"protected {provider} credentials are invalid")
    payload["token"] = validate_token(payload.get("token"))
    return payload


def archive_sources(provider: str, sources: list[Path]) -> list[Path]:
    """Move verified source files into a protected collision-safe archive."""
    archive = prepare_private_directory(
        Path.home() / ".config" / "agentic-workflows" / provider / "imported-sources"
    )
    resolved = [
        inspect_regular_source(path, maximum_bytes=MAX_ARCHIVE_BYTES) for path in sources
    ]
    destinations = [archive / path.name for path in resolved]
    if len({destination.name for destination in destinations}) != len(destinations):
        raise CredentialError("selected source names collide in the protected archive")
    if any(destination.exists() or destination.is_symlink() for destination in destinations):
        raise CredentialError("a selected source name already exists in the protected archive")
    moved: list[tuple[Path, Path]] = []
    try:
        for source, destination in zip(resolved, destinations, strict=True):
            os.replace(source, destination)
            moved.append((source, destination))
            destination.chmod(0o400)
    except OSError as error:
        for source, destination in reversed(moved):
            try:
                os.replace(destination, source)
                source.chmod(0o600)
            except OSError:
                pass
        raise CredentialError("verified sources could not be archived safely") from error
    return destinations


def redact_exact(text: str, secrets: list[str], marker: str = "[REDACTED]") -> str:
    """Remove exact secret values from captured output."""
    redacted = text
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, marker)
    return redacted
