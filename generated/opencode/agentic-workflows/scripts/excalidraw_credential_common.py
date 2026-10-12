#!/usr/bin/env python3
"""Excalidraw bindings for shared Agentic Workflows credential primitives."""

from __future__ import annotations

from pathlib import Path

from account_credential_common import (
    MAX_CREDENTIAL_BYTES,
    CredentialError as CredentialError,
    archive_sources,
    atomic_private_write as atomic_private_write,
    encode_credential as encode_account_credential,
    git_container as git_container,
    inspect_regular_source,
    load_credential as load_account_credential,
    read_private_text as read_private_text,
    redact_exact as redact_account_secrets,
    validate_private_file as validate_private_file,
    validate_token as validate_token,
)


def inspect_source(path: Path, *, allow_broad_mode: bool = False) -> Path:
    """Apply the shared source contract with Excalidraw's size bound."""
    return inspect_regular_source(
        path,
        maximum_bytes=MAX_CREDENTIAL_BYTES,
        allow_broad_mode=allow_broad_mode,
    )


def encode_credential(token: str) -> bytes:
    """Encode the strict Excalidraw personal-key record."""
    return encode_account_credential("excalidraw", "personal", token)


def load_credential(path: Path) -> dict[str, str | int]:
    """Load a protected Excalidraw personal-key record."""
    return load_account_credential(
        path,
        provider="excalidraw",
        token_types={"personal"},
    )


def redact_exact(text: str, token: str) -> str:
    """Redact the exact Excalidraw key from diagnostic text."""
    return redact_account_secrets(
        text,
        [token],
        marker="[REDACTED_EXCALIDRAW_KEY]",
    )


def archive_source(source: Path) -> Path:
    """Archive one verified source using shared transactional rollback."""
    return archive_sources("excalidraw", [source])[0]
