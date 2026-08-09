#!/usr/bin/env python3
"""Guarded WordPress content-as-code synchronization and adoption toolkit.

The CLI is intentionally transport-agnostic. Repository tests and migration
rehearsals use the atomic fixture transport. Real WordPress writes require the
reviewed AMSoft runtime endpoint and a secret-free credential reference.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import getpass
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
SERIALIZER = "amsoft-wordpress-managed-object-json-v1"
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_DIFF_LINES = 2_000
MAX_OBJECTS = 10_000
MAX_WAVE_SIZE = 25
IDENTITY_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,31}:[a-z0-9][a-z0-9._:-]{0,198}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "application_password",
    "authorization",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "nonce",
    "password",
    "private_key",
    "secret",
    "signed_url",
    "token",
}
PUBLIC_STATUSES = {"available", "inherit", "publish"}
OWNERSHIP_STATES = {
    "git",
    "wordpress",
    "shared-guarded",
    "manifest",
    "runtime-generated",
    "read-only",
    "excluded",
}
OBJECT_FIELDS: dict[str, frozenset[str]] = {
    "post": frozenset({
        "title", "content", "excerpt", "slug", "status", "date_gmt", "parent_ref",
        "author_ref", "terms", "meta", "featured_media_ref", "template",
    }),
    "page": frozenset({
        "title", "content", "excerpt", "slug", "status", "date_gmt", "parent_ref",
        "author_ref", "terms", "meta", "featured_media_ref", "template",
    }),
    "cpt": frozenset({
        "post_type", "title", "content", "excerpt", "slug", "status", "date_gmt",
        "parent_ref", "author_ref", "terms", "meta", "featured_media_ref", "template",
    }),
    "wp_template": frozenset({"title", "content", "slug", "status", "theme", "area"}),
    "wp_template_part": frozenset({"title", "content", "slug", "status", "theme", "area"}),
    "wp_navigation": frozenset({"title", "content", "slug", "status"}),
    "wp_global_styles": frozenset({"title", "slug", "status", "theme", "settings", "styles"}),
    "wp_block": frozenset({"title", "content", "slug", "status", "sync_behavior"}),
    "attachment": frozenset({
        "logical_id", "source_sha256", "mime_type", "bytes", "width", "height",
        "alt_text", "caption", "credit", "license", "storage", "status",
    }),
    "acf_field_group": frozenset({"key", "title", "fields", "location", "active", "modified"}),
    "acf_values": frozenset({"target_ref", "field_group_refs", "values", "status"}),
}
SITE_EDITOR_TYPES = {
    "wp_template", "wp_template_part", "wp_navigation", "wp_global_styles", "wp_block",
}
CODE_EXPORT_SUFFIXES = {".css", ".html", ".json", ".md", ".png", ".svg", ".webp"}
CODE_EXPORT_ROOTS = {"assets", "parts", "patterns", "styles", "templates"}


class SyncError(RuntimeError):
    """Typed, secret-safe operation error."""

    def __init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def payload(self) -> dict[str, Any]:
        return {"ok": False, "error": {"code": self.code, "message": self.message, "details": self.details}}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _normalize(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        raise SyncError("invalid_number", f"{path}: floating-point values are not canonical")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    if isinstance(value, list):
        return [_normalize(item, f"{path}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise SyncError("invalid_key", f"{path}: object keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise SyncError("identity_collision", f"{path}: normalized key collision")
            normalized[normalized_key] = _normalize(value[key], f"{path}.{normalized_key}")
        return normalized
    raise SyncError("invalid_type", f"{path}: unsupported value type {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    normalized = _normalize(value)
    return (
        json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def reject_secret_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS or normalized.endswith(("_password", "_secret", "_token")):
                raise SyncError("secret_field", f"{path}.{key}: secret-shaped fields are prohibited")
            reject_secret_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_secret_fields(nested, f"{path}[{index}]")


def read_json(path: Path, *, max_bytes: int = MAX_JSON_BYTES) -> Any:
    expanded = path.expanduser().resolve()
    if path.is_symlink() or expanded.is_symlink():
        raise SyncError("unsafe_path", f"refusing symlink input: {path}")
    try:
        size = expanded.stat().st_size
    except OSError as error:
        raise SyncError("missing_input", f"cannot read {path}: {error.strerror}") from error
    if size > max_bytes:
        raise SyncError("input_too_large", f"{path}: {size} bytes exceeds {max_bytes}")
    try:
        payload = json.loads(expanded.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SyncError("invalid_json", f"{path}: invalid UTF-8 JSON") from error
    reject_secret_fields(payload)
    return payload


def _fsync_directory(directory: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write(path: Path, content: bytes, *, replace: bool = True, mode: int = 0o600) -> None:
    destination = path.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or destination.is_symlink():
        raise SyncError("unsafe_path", f"refusing symlink destination: {path}")
    if destination.exists() and not replace:
        raise SyncError("output_exists", f"refusing to replace {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        os.chmod(destination, mode)
        _fsync_directory(destination.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, payload: Any, *, replace: bool = True, mode: int = 0o600) -> None:
    atomic_write(path, canonical_bytes(payload), replace=replace, mode=mode)


def validate_identity(object_type: str, object_key: str) -> str:
    if object_type not in OBJECT_FIELDS:
        raise SyncError("unsupported_object", f"unsupported object type: {object_type}")
    identity = f"{object_type}:{object_key}"
    if not IDENTITY_PATTERN.fullmatch(identity) or ".." in identity or object_key.isdigit():
        raise SyncError("invalid_identity", "object identity must be a portable namespaced key, not a database ID")
    return identity


def _content_status(data: Mapping[str, Any]) -> str | None:
    status = data.get("status")
    return status if isinstance(status, str) else None


def validate_managed_object(payload: Any, *, git_safe: bool = False) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SyncError("invalid_object", "managed object must be a JSON object")
    required = {
        "schema_version", "kind", "object_type", "object_key", "environment", "ownership",
        "managed_fields", "remote_fields", "data", "references", "provenance", "state",
        "classification", "tombstone",
    }
    if set(payload) != required:
        raise SyncError(
            "invalid_object_fields",
            "managed object fields differ from the v1 contract",
            details={"missing": sorted(required - set(payload)), "unexpected": sorted(set(payload) - required)},
        )
    if payload["schema_version"] != SCHEMA_VERSION or payload["kind"] != "wordpress-managed-object":
        raise SyncError("schema_version", "managed object schema version or kind is unsupported")
    object_type = payload.get("object_type")
    object_key = payload.get("object_key")
    if not isinstance(object_type, str) or not isinstance(object_key, str):
        raise SyncError("invalid_identity", "object type and key must be strings")
    validate_identity(object_type, object_key)
    if payload.get("environment") not in {"local", "development", "staging", "production"}:
        raise SyncError("invalid_environment", "environment is unsupported")
    ownership = payload.get("ownership")
    if ownership not in OWNERSHIP_STATES:
        raise SyncError("invalid_ownership", "ownership state is unsupported")
    managed = payload.get("managed_fields")
    remote = payload.get("remote_fields")
    if not isinstance(managed, list) or not isinstance(remote, list):
        raise SyncError("invalid_fields", "managed_fields and remote_fields must be arrays")
    if len(set(managed)) != len(managed) or len(set(remote)) != len(remote):
        raise SyncError("duplicate_field", "field ownership arrays must be unique")
    if set(managed) & set(remote):
        raise SyncError("ownership_collision", "a field cannot be both managed and remote-owned")
    allowed = OBJECT_FIELDS[object_type]
    unknown = (set(managed) | set(remote)) - allowed
    if unknown:
        raise SyncError("unsupported_field", "field adapter does not support all declared fields", details={"fields": sorted(unknown)})
    data = payload.get("data")
    if not isinstance(data, dict):
        raise SyncError("invalid_data", "data must be an object")
    if set(data) - (set(managed) | set(remote)):
        raise SyncError("unowned_field", "every data field requires an ownership declaration")
    if set(managed) - set(data):
        raise SyncError("missing_managed_field", "every managed field requires a value")
    if not isinstance(payload.get("references"), list):
        raise SyncError("invalid_references", "references must be an array")
    for reference in payload["references"]:
        if not isinstance(reference, str) or not IDENTITY_PATTERN.fullmatch(reference):
            raise SyncError("invalid_reference", "references must use portable managed identities")
    if len(payload["references"]) != len(set(payload["references"])):
        raise SyncError("duplicate_reference", "managed object references must be unique")
    if not isinstance(payload.get("provenance"), dict):
        raise SyncError("invalid_provenance", "provenance must be an object")
    if payload.get("state") not in {"active", "read-only", "unsupported", "excluded", "deleted"}:
        raise SyncError("invalid_state", "managed object state is unsupported")
    if payload.get("classification") not in {"public", "internal", "restricted"}:
        raise SyncError("invalid_classification", "classification is unsupported")
    if not isinstance(payload.get("tombstone"), bool):
        raise SyncError("invalid_tombstone", "tombstone must be boolean")
    if payload["tombstone"] != (payload["state"] == "deleted"):
        raise SyncError("invalid_tombstone", "deleted state and tombstone must agree")
    if ownership in {"read-only", "excluded", "runtime-generated"} and managed:
        raise SyncError("invalid_ownership", f"{ownership} objects cannot declare managed fields")
    reject_secret_fields(payload)
    _normalize(payload)
    if git_safe:
        status = _content_status(data)
        if payload["classification"] != "public" or (status is not None and status not in PUBLIC_STATUSES):
            raise SyncError("nonpublic_git_content", "non-public content payloads are excluded from Git exports")
    if object_type == "attachment":
        validate_media_data(data)
    if object_type == "acf_values":
        validate_acf_values(data)
    return _normalize(payload)


def managed_view(payload: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_managed_object(dict(payload))
    managed_fields = sorted(validated["managed_fields"])
    return {
        "schema_version": SCHEMA_VERSION,
        "serializer": SERIALIZER,
        "identity": f"{validated['object_type']}:{validated['object_key']}",
        "object_type": validated["object_type"],
        "object_key": validated["object_key"],
        "ownership": validated["ownership"],
        "managed_fields": managed_fields,
        "data": {field: validated["data"][field] for field in managed_fields},
        "references": sorted(validated["references"]),
        "state": validated["state"],
        "tombstone": validated["tombstone"],
    }


def managed_digest(payload: Mapping[str, Any]) -> str:
    return canonical_digest(managed_view(payload))


def validate_media_data(data: Mapping[str, Any]) -> None:
    required = {"logical_id", "source_sha256", "mime_type", "bytes", "storage"}
    missing = required - set(data)
    if missing:
        raise SyncError("invalid_media", "media manifest is incomplete", details={"missing": sorted(missing)})
    if not isinstance(data.get("source_sha256"), str) or not SHA256_PATTERN.fullmatch(data["source_sha256"]):
        raise SyncError("invalid_media_hash", "media source_sha256 must be lowercase SHA-256")
    if not isinstance(data.get("bytes"), int) or not 0 < data["bytes"] <= 100 * 1024 * 1024:
        raise SyncError("invalid_media_size", "media size must be between 1 byte and 100 MiB")
    mime = data.get("mime_type")
    if not isinstance(mime, str) or not re.fullmatch(r"(?:image|video|audio|application)/[a-z0-9.+-]+", mime):
        raise SyncError("invalid_media_mime", "media MIME type is invalid")
    storage = data.get("storage")
    if not isinstance(storage, dict) or storage.get("kind") not in {"object-store", "release-artifact", "git-lfs"}:
        raise SyncError("invalid_media_storage", "media storage must use an approved manifest lane")
    if not data.get("license") or not data.get("credit"):
        raise SyncError("missing_media_rights", "media license and credit are required")
    reject_secret_fields(data)


def _contains_php_serialization(value: Any) -> bool:
    if isinstance(value, str):
        return bool(re.match(r"^(?:a|O|C|s|i|b|d|N):", value))
    if isinstance(value, list):
        return any(_contains_php_serialization(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_php_serialization(item) for item in value.values())
    return False


def validate_acf_values(data: Mapping[str, Any]) -> None:
    if not isinstance(data.get("target_ref"), str) or not IDENTITY_PATTERN.fullmatch(data["target_ref"]):
        raise SyncError("invalid_acf_target", "ACF values require a portable target reference")
    if not isinstance(data.get("field_group_refs"), list) or not all(
        isinstance(item, str) and item.startswith("acf_field_group:") for item in data["field_group_refs"]
    ):
        raise SyncError("invalid_acf_groups", "ACF values require declared field-group references")
    if not isinstance(data.get("values"), dict):
        raise SyncError("invalid_acf_values", "ACF values must be an object")
    if _contains_php_serialization(data["values"]):
        raise SyncError("unsafe_serialized_value", "raw PHP-serialized ACF values are unsupported")


def validate_project(payload: Any, *, source_path: Path | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SyncError("invalid_project", "project contract must be an object")
    required = {
        "schema_version", "kind", "project_key", "site_key", "environment", "canonical_url",
        "transport", "credential_ref", "repository_root", "ownership_policy", "adapter_policy",
        "limits",
    }
    if set(payload) != required:
        raise SyncError("invalid_project_fields", "project fields differ from the v1 contract")
    if payload.get("schema_version") != 1 or payload.get("kind") != "wordpress-sync-project":
        raise SyncError("schema_version", "project schema version or kind is unsupported")
    for field in ("project_key", "site_key"):
        if not isinstance(payload.get(field), str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", payload[field]):
            raise SyncError("invalid_project_identity", f"{field} is invalid")
    if payload.get("environment") not in {"local", "development", "staging", "production"}:
        raise SyncError("invalid_environment", "project environment is unsupported")
    parsed = urllib.parse.urlparse(str(payload.get("canonical_url")))
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise SyncError("invalid_url", "canonical_url must be credential-free HTTPS")
    transport = payload.get("transport")
    if not isinstance(transport, dict) or transport.get("kind") not in {"fixture", "wordpress-rest"}:
        raise SyncError("invalid_transport", "transport kind is unsupported")
    if transport["kind"] == "fixture":
        if set(transport) != {"kind", "state_path"} or not isinstance(transport.get("state_path"), str):
            raise SyncError("invalid_transport", "fixture transport requires only state_path")
    else:
        if set(transport) != {"kind", "namespace", "username"} or transport.get("namespace") != "amsoft/v1":
            raise SyncError("invalid_transport", "WordPress transport contract is invalid")
    credential_ref = payload.get("credential_ref")
    if transport["kind"] == "fixture":
        if credential_ref is not None:
            raise SyncError("invalid_credential_ref", "fixture transport must not use credentials")
    elif not isinstance(credential_ref, dict) or credential_ref.get("store") not in {"macos-keychain", "protected-file", "prompt"}:
        raise SyncError("invalid_credential_ref", "WordPress transport requires an approved credential reference")
    if not isinstance(payload.get("ownership_policy"), dict) or not isinstance(payload.get("adapter_policy"), dict):
        raise SyncError("invalid_policy", "ownership and adapter policies must be objects")
    limits = payload.get("limits")
    if not isinstance(limits, dict) or set(limits) != {"max_objects", "max_json_bytes", "max_wave_size"}:
        raise SyncError("invalid_limits", "limits differ from the v1 contract")
    if not 1 <= limits["max_objects"] <= MAX_OBJECTS or not 1024 <= limits["max_json_bytes"] <= MAX_JSON_BYTES:
        raise SyncError("invalid_limits", "project object or JSON limit is invalid")
    if not 1 <= limits["max_wave_size"] <= MAX_WAVE_SIZE:
        raise SyncError("invalid_limits", "project wave limit is invalid")
    reject_secret_fields(payload)
    if source_path is not None:
        root = Path(payload["repository_root"]).expanduser().resolve()
        try:
            source_path.expanduser().resolve().relative_to(root)
        except ValueError as error:
            raise SyncError("project_path", "project contract must reside beneath repository_root") from error
    return _normalize(payload)


def load_project(path: Path) -> dict[str, Any]:
    return validate_project(read_json(path), source_path=path)


def _inside_git(path: Path) -> bool:
    current = path.expanduser().resolve()
    for parent in (current, *current.parents):
        if (parent / ".git").exists():
            return True
    return False


def resolve_credential(reference: Mapping[str, Any]) -> str:
    store = reference.get("store")
    if store == "prompt":
        return getpass.getpass("WordPress Application Password: ")
    if store == "macos-keychain":
        service = reference.get("service")
        account = reference.get("account")
        if not isinstance(service, str) or not isinstance(account, str):
            raise SyncError("invalid_credential_ref", "Keychain reference is incomplete")
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", service, "-a", account, "-w"],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise SyncError("credential_unavailable", "WordPress Application Password is unavailable")
        return result.stdout.rstrip("\n")
    if store == "protected-file":
        value = reference.get("path")
        if not isinstance(value, str):
            raise SyncError("invalid_credential_ref", "protected-file reference is incomplete")
        path = Path(value).expanduser()
        if _inside_git(path):
            raise SyncError("unsafe_credential_path", "credential files must stay outside Git worktrees")
        if path.is_symlink():
            raise SyncError("unsafe_credential_path", "credential files cannot be symlinks")
        mode = path.stat().st_mode & 0o777
        if mode & 0o077:
            raise SyncError("unsafe_credential_mode", "credential file must be owner-only")
        secret = path.read_text(encoding="utf-8").strip()
        if not secret:
            raise SyncError("credential_unavailable", "credential file is empty")
        return secret
    raise SyncError("invalid_credential_ref", "unsupported credential store")


class FixtureLock:
    def __init__(self, path: Path) -> None:
        self.path = path.with_suffix(path.suffix + ".lock")
        self.descriptor: int | None = None

    def __enter__(self) -> "FixtureLock":
        try:
            self.descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise SyncError("operation_busy", "fixture transport is locked by another operation") from error
        os.write(self.descriptor, f"{os.getpid()}\n".encode("ascii"))
        os.fsync(self.descriptor)
        return self

    def __exit__(self, _kind: object, _value: object, _traceback: object) -> None:
        if self.descriptor is not None:
            os.close(self.descriptor)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


class FixtureTransport:
    guard = "atomic-compare-and-swap"

    def __init__(self, state_path: Path, project: Mapping[str, Any]) -> None:
        self.state_path = state_path.expanduser().resolve()
        self.project = project

    def _load(self) -> dict[str, Any]:
        state = read_json(self.state_path, max_bytes=MAX_JSON_BYTES * 4)
        if not isinstance(state, dict) or set(state) != {
            "schema_version", "site_fingerprint", "revision_counter", "objects", "idempotency",
        }:
            raise SyncError("invalid_fixture", "fixture transport state is invalid")
        if state["schema_version"] != 1 or not isinstance(state["objects"], dict):
            raise SyncError("invalid_fixture", "fixture transport version is unsupported")
        expected = canonical_digest({
            "site_key": self.project["site_key"],
            "environment": self.project["environment"],
            "canonical_url": self.project["canonical_url"],
        })
        if state["site_fingerprint"] != expected:
            raise SyncError("target_mismatch", "fixture fingerprint differs from project contract")
        return state

    def list_objects(self) -> list[dict[str, Any]]:
        state = self._load()
        return [self._record(item) for _identity, item in sorted(state["objects"].items())]

    def _record(self, record: Mapping[str, Any]) -> dict[str, Any]:
        obj = validate_managed_object(record["object"])
        return {
            "object": obj,
            "identity": f"{obj['object_type']}:{obj['object_key']}",
            "revision": str(record["revision"]),
            "modified_gmt": record["modified_gmt"],
            "sha256": managed_digest(obj),
            "guard": self.guard,
        }

    def get(self, identity: str) -> dict[str, Any]:
        state = self._load()
        record = state["objects"].get(identity)
        if record is None:
            raise SyncError("not_found", f"managed object not found: {identity}")
        return self._record(record)

    def apply(
        self,
        obj: Mapping[str, Any],
        *,
        expected_sha256: str,
        expected_revision: str,
        idempotency_key: str,
        dry_run: bool,
    ) -> dict[str, Any]:
        validated = validate_managed_object(dict(obj))
        identity = f"{validated['object_type']}:{validated['object_key']}"
        if not SHA256_PATTERN.fullmatch(expected_sha256):
            raise SyncError("invalid_expected_hash", "expected hash must be lowercase SHA-256")
        if not re.fullmatch(r"[A-Za-z0-9._:-]{8,128}", idempotency_key):
            raise SyncError("invalid_idempotency_key", "idempotency key is invalid")
        request_hash = canonical_digest({
            "identity": identity,
            "expected_sha256": expected_sha256,
            "expected_revision": str(expected_revision),
            "desired_sha256": managed_digest(validated),
        })
        with FixtureLock(self.state_path):
            state = self._load()
            prior = state["idempotency"].get(idempotency_key)
            if prior is not None:
                if prior["request_hash"] != request_hash:
                    raise SyncError("idempotency_conflict", "idempotency key was used for another request")
                return {**prior["result"], "idempotent_replay": True}
            record = state["objects"].get(identity)
            if record is None:
                raise SyncError("not_found", f"managed object not found: {identity}")
            before = self._record(record)
            if before["sha256"] != expected_sha256 or before["revision"] != str(expected_revision):
                raise SyncError(
                    "stale_remote",
                    "remote object changed since the expected baseline",
                    details={"actual_sha256": before["sha256"], "actual_revision": before["revision"]},
                )
            result = {
                "ok": True,
                "dry_run": dry_run,
                "identity": identity,
                "guard": self.guard,
                "before_sha256": before["sha256"],
                "before_revision": before["revision"],
                "desired_sha256": managed_digest(validated),
            }
            if dry_run:
                return result
            state["revision_counter"] += 1
            revision = str(state["revision_counter"])
            record = {"object": validated, "revision": revision, "modified_gmt": utc_now()}
            state["objects"][identity] = record
            after = self._record(record)
            result.update({
                "after_sha256": after["sha256"],
                "after_revision": after["revision"],
                "readback": after,
                "idempotent_replay": False,
            })
            state["idempotency"][idempotency_key] = {"request_hash": request_hash, "result": result}
            atomic_write_json(self.state_path, state, mode=0o600)
            return result


class WordPressRestTransport:
    guard = "atomic-compare-and-swap"

    def __init__(self, project: Mapping[str, Any]) -> None:
        self.project = project
        self.base = project["canonical_url"].rstrip("/") + "/wp-json/amsoft/v1"

    def _request(self, method: str, route: str, payload: Any | None = None) -> Any:
        password = resolve_credential(self.project["credential_ref"])
        username = self.project["transport"]["username"]
        auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        data = None if payload is None else canonical_bytes(payload)
        request = urllib.request.Request(
            self.base + route,
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth}",
                "User-Agent": "AMSoft-wp-content-sync/1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read(MAX_JSON_BYTES + 1)
        except urllib.error.HTTPError as error:
            raw = error.read(MAX_JSON_BYTES + 1)
            try:
                parsed = json.loads(raw)
                code = str(parsed.get("code", "remote_error"))
                message = str(parsed.get("message", "WordPress runtime rejected the request"))
            except (UnicodeError, json.JSONDecodeError):
                code, message = "remote_error", "WordPress runtime rejected the request"
            raise SyncError(code, message, details={"status": error.code}) from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise SyncError("transport_failure", "WordPress runtime is unavailable") from error
        finally:
            password = ""
        if len(raw) > MAX_JSON_BYTES:
            raise SyncError("remote_response_too_large", "WordPress runtime response exceeds limit")
        try:
            result = json.loads(raw)
        except (UnicodeError, json.JSONDecodeError) as error:
            raise SyncError("invalid_remote_response", "WordPress runtime returned invalid JSON") from error
        reject_secret_fields(result)
        return result

    def list_objects(self) -> list[dict[str, Any]]:
        result = self._request("GET", "/registry")
        if not isinstance(result, dict) or not isinstance(result.get("objects"), list):
            raise SyncError("invalid_remote_response", "registry response is invalid")
        return result["objects"]

    def get(self, identity: str) -> dict[str, Any]:
        object_type, object_key = identity.split(":", 1)
        route = f"/objects/{urllib.parse.quote(object_type)}/{urllib.parse.quote(object_key, safe='')}"
        result = self._request("GET", route)
        if not isinstance(result, dict):
            raise SyncError("invalid_remote_response", "object response is invalid")
        return result

    def apply(
        self,
        obj: Mapping[str, Any],
        *,
        expected_sha256: str,
        expected_revision: str,
        idempotency_key: str,
        dry_run: bool,
    ) -> dict[str, Any]:
        identity = f"{obj['object_type']}:{obj['object_key']}"
        object_type, object_key = identity.split(":", 1)
        route = f"/objects/{urllib.parse.quote(object_type)}/{urllib.parse.quote(object_key, safe='')}/apply"
        result = self._request("POST", route, {
            "schema_version": 1,
            "object": obj,
            "expected_sha256": expected_sha256,
            "expected_revision": str(expected_revision),
            "idempotency_key": idempotency_key,
            "dry_run": dry_run,
        })
        if not isinstance(result, dict):
            raise SyncError("invalid_remote_response", "apply response is invalid")
        return result


def transport_for(project: Mapping[str, Any], project_path: Path) -> FixtureTransport | WordPressRestTransport:
    config = project["transport"]
    if config["kind"] == "fixture":
        path = Path(config["state_path"])
        if not path.is_absolute():
            path = project_path.parent / path
        return FixtureTransport(path, project)
    return WordPressRestTransport(project)


def make_lock(project: Mapping[str, Any], record: Mapping[str, Any], source_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "kind": "wordpress-content-lock",
        "project_key": project["project_key"],
        "site_key": project["site_key"],
        "environment": project["environment"],
        "identity": record["identity"],
        "serializer": SERIALIZER,
        "managed_fields": sorted(record["object"]["managed_fields"]),
        "guard": record["guard"],
        "remote": {
            "revision": str(record["revision"]),
            "modified_gmt": record["modified_gmt"],
            "sha256": record["sha256"],
            "observed_at": utc_now(),
        },
        "local": {"sha256": source_sha256},
    }


def validate_lock(lock: Any, project: Mapping[str, Any], identity: str) -> dict[str, Any]:
    if not isinstance(lock, dict) or set(lock) != {
        "schema_version", "kind", "project_key", "site_key", "environment", "identity",
        "serializer", "managed_fields", "guard", "remote", "local",
    }:
        raise SyncError("invalid_lock", "content lock differs from the v2 contract")
    if lock["schema_version"] != 2 or lock["kind"] != "wordpress-content-lock":
        raise SyncError("invalid_lock", "content lock version is unsupported")
    expected = (project["project_key"], project["site_key"], project["environment"], identity)
    actual = (lock["project_key"], lock["site_key"], lock["environment"], lock["identity"])
    if actual != expected:
        raise SyncError("lock_target_mismatch", "content lock identifies another target")
    if lock["serializer"] != SERIALIZER or lock["guard"] != "atomic-compare-and-swap":
        raise SyncError("invalid_lock", "content lock serializer or guard is unsupported")
    for digest in (lock["remote"].get("sha256"), lock["local"].get("sha256")):
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            raise SyncError("invalid_lock", "content lock hash is invalid")
    return _normalize(lock)


def status_result(local: Mapping[str, Any], lock: Mapping[str, Any], remote: Mapping[str, Any]) -> dict[str, Any]:
    local_sha = managed_digest(local)
    base_local = lock["local"]["sha256"]
    base_remote = lock["remote"]["sha256"]
    remote_sha = remote["sha256"]
    local_changed = local_sha != base_local
    remote_changed = remote_sha != base_remote
    if local_changed and remote_changed:
        state = "both-changed"
    elif local_changed:
        state = "local-changed"
    elif remote_changed:
        state = "remote-changed"
    else:
        state = "clean"
    return {
        "ok": True,
        "state": state,
        "identity": remote["identity"],
        "local_sha256": local_sha,
        "base_local_sha256": base_local,
        "remote_sha256": remote_sha,
        "base_remote_sha256": base_remote,
        "remote_revision": remote["revision"],
        "guard": remote["guard"],
    }


def unified_diff(local: Mapping[str, Any], remote: Mapping[str, Any]) -> str:
    left = canonical_bytes(managed_view(remote)).decode("utf-8").splitlines()
    right = canonical_bytes(managed_view(local)).decode("utf-8").splitlines()
    lines = list(difflib.unified_diff(left, right, fromfile="wordpress", tofile="git", lineterm=""))
    if len(lines) > MAX_DIFF_LINES:
        raise SyncError("diff_too_large", f"diff exceeds {MAX_DIFF_LINES} lines")
    return "\n".join(lines) + ("\n" if lines else "")


def classify_object(obj: Mapping[str, Any], adapter_policy: Mapping[str, Any]) -> dict[str, Any]:
    object_type = str(obj["object_type"])
    state = str(obj["state"])
    ownership = str(obj["ownership"])
    adapter = adapter_policy.get(object_type, "unsupported")
    if state in {"unsupported", "excluded"} or adapter == "unsupported":
        disposition = "unsupported/read-only"
    elif object_type == "attachment":
        disposition = "manifest-media"
    elif object_type == "acf_field_group":
        disposition = "git-owned-code"
    elif object_type in SITE_EDITOR_TYPES or object_type in {"post", "page", "cpt", "acf_values"}:
        disposition = "managed-database-content"
    else:
        disposition = ownership
    return {
        "identity": f"{object_type}:{obj['object_key']}",
        "object_type": object_type,
        "disposition": disposition,
        "ownership": ownership,
        "classification": obj["classification"],
        "compatibility": "supported" if adapter != "unsupported" and state == "active" else "blocked",
        "reason": "declared adapter and active state" if adapter != "unsupported" and state == "active" else "adapter or object state is unsupported",
        "dependencies": sorted(obj["references"]),
    }


def inventory(project: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(records) > project["limits"]["max_objects"]:
        raise SyncError("inventory_too_large", "remote inventory exceeds the project limit")
    surfaces = [classify_object(record["object"], project["adapter_policy"]) for record in records]
    identities = [item["identity"] for item in surfaces]
    if len(identities) != len(set(identities)):
        raise SyncError("identity_collision", "inventory contains duplicate portable identities")
    counts: dict[str, int] = {}
    for item in surfaces:
        counts[item["disposition"]] = counts.get(item["disposition"], 0) + 1
    return {
        "schema_version": 1,
        "kind": "wordpress-migration-inventory",
        "project_key": project["project_key"],
        "site_key": project["site_key"],
        "environment": project["environment"],
        "generated_at": "normalized-at-review",
        "site_fingerprint": canonical_digest({
            "site_key": project["site_key"],
            "environment": project["environment"],
            "canonical_url": project["canonical_url"],
        }),
        "surfaces": sorted(surfaces, key=lambda item: item["identity"]),
        "summary": {key: counts[key] for key in sorted(counts)},
        "blocked": sorted(item["identity"] for item in surfaces if item["compatibility"] == "blocked"),
    }


def topological_waves(inventory_payload: Mapping[str, Any], max_wave_size: int) -> list[list[str]]:
    surfaces = inventory_payload.get("surfaces")
    if not isinstance(surfaces, list):
        raise SyncError("invalid_inventory", "inventory surfaces must be an array")
    supported = {
        item["identity"]: set(item.get("dependencies", []))
        for item in surfaces
        if item.get("compatibility") == "supported"
    }
    for identity, dependencies in supported.items():
        missing = dependencies - set(supported)
        if missing:
            raise SyncError("missing_dependency", f"{identity} has unavailable dependencies", details={"dependencies": sorted(missing)})
    remaining = {identity: set(dependencies) for identity, dependencies in supported.items()}
    completed: set[str] = set()
    waves: list[list[str]] = []
    while remaining:
        ready = sorted(identity for identity, dependencies in remaining.items() if dependencies <= completed)
        if not ready:
            raise SyncError("dependency_cycle", "migration dependency graph contains a cycle")
        while ready:
            wave = ready[:max_wave_size]
            ready = ready[max_wave_size:]
            waves.append(wave)
            completed.update(wave)
            for identity in wave:
                remaining.pop(identity)
    return waves


def validate_code_export(root: Path) -> dict[str, Any]:
    expanded = root.expanduser().resolve()
    if not expanded.is_dir() or root.is_symlink():
        raise SyncError("invalid_export", "code export root must be a real directory")
    files: list[dict[str, Any]] = []
    for path in sorted(expanded.rglob("*")):
        if path.is_symlink():
            raise SyncError("unsafe_export_path", f"export contains a symlink: {path.relative_to(expanded)}")
        if not path.is_file():
            continue
        relative = path.relative_to(expanded)
        if any(part.startswith(".") or part in {"node_modules", "vendor"} for part in relative.parts):
            raise SyncError("unsafe_export_path", f"export contains prohibited path: {relative}")
        if relative.name == "theme.json":
            pass
        elif relative.parts[0] not in CODE_EXPORT_ROOTS or path.suffix.lower() not in CODE_EXPORT_SUFFIXES:
            raise SyncError("unsafe_export_path", f"export path is not allowlisted: {relative}")
        size = path.stat().st_size
        if size > 5 * 1024 * 1024:
            raise SyncError("export_too_large", f"export file exceeds 5 MiB: {relative}")
        files.append({"path": relative.as_posix(), "bytes": size, "sha256": sha256_bytes(path.read_bytes())})
    if not files:
        raise SyncError("empty_export", "code export contains no allowlisted files")
    return {
        "schema_version": 1,
        "kind": "wordpress-code-export-plan",
        "trust_boundary": "untrusted-editor-export",
        "files": files,
        "requires_human_review": True,
        "direct_protected_branch_write": False,
    }


def automation_plan(event: Mapping[str, Any]) -> dict[str, Any]:
    required = {"schema_version", "event", "site_key", "environment", "identity", "correlation_id", "actor", "autosave", "revision", "classification"}
    if set(event) != required or event.get("schema_version") != 1:
        raise SyncError("invalid_event", "automation event differs from the v1 contract")
    reject_secret_fields(event)
    if event["event"] not in {"wordpress-save", "git-merge"}:
        raise SyncError("invalid_event", "automation event type is unsupported")
    if not isinstance(event["site_key"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", event["site_key"]):
        raise SyncError("invalid_event", "automation site_key is invalid")
    if event["environment"] not in {"local", "development", "staging", "production"}:
        raise SyncError("invalid_event", "automation environment is unsupported")
    if not isinstance(event["identity"], str) or not IDENTITY_PATTERN.fullmatch(event["identity"]):
        raise SyncError("invalid_event", "automation identity is invalid")
    actor = event["actor"]
    if (not isinstance(actor, (str, int)) or isinstance(actor, bool)
            or (isinstance(actor, str) and not 1 <= len(actor) <= 128)
            or (isinstance(actor, int) and actor < 0)):
        raise SyncError("invalid_event", "automation actor must be a string or integer")
    if not isinstance(event["autosave"], bool) or not isinstance(event["revision"], bool):
        raise SyncError("invalid_event", "automation save flags must be boolean")
    if event["classification"] != "public":
        return {"ok": True, "action": "excluded", "reason": "non-public content cannot enter Git automation"}
    if event["autosave"] or event["revision"]:
        return {"ok": True, "action": "ignored", "reason": "autosaves and revisions do not create pull requests"}
    correlation = str(event["correlation_id"])
    if not re.fullmatch(r"[A-Za-z0-9._:-]{8,128}", correlation):
        raise SyncError("invalid_correlation", "correlation_id is invalid")
    if event["event"] == "wordpress-save":
        branch = f"wordpress-sync/{event['site_key']}/{canonical_digest(event)[:12]}"
        return {
            "ok": True,
            "action": "create-or-update-pull-request",
            "branch": branch,
            "debounce_key": f"{event['site_key']}:{event['environment']}:{event['identity']}",
            "loop_suppression": correlation,
            "protected_branch_write": False,
        }
    return {
        "ok": True,
        "action": "fresh-read-plan-cas-apply",
        "concurrency_group": f"wordpress-sync-{event['site_key']}-{event['environment']}",
        "requires_environment_approval": event["environment"] in {"staging", "production"},
        "loop_suppression": correlation,
    }


def output_json(payload: Any, output: Path | None = None) -> None:
    content = canonical_bytes(payload)
    if output is None:
        sys.stdout.buffer.write(content)
    else:
        atomic_write(output, content, mode=0o600)


def _load_local_and_lock(arguments: argparse.Namespace, project: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str]:
    local = validate_managed_object(read_json(arguments.source))
    identity = f"{local['object_type']}:{local['object_key']}"
    if arguments.object and arguments.object != identity:
        raise SyncError("identity_mismatch", "--object differs from the source object identity")
    lock = validate_lock(read_json(arguments.lock), project, identity)
    return local, lock, identity


def command_validate(arguments: argparse.Namespace) -> dict[str, Any]:
    if arguments.kind == "object":
        value = validate_managed_object(read_json(arguments.input), git_safe=arguments.git_safe)
        return {"ok": True, "kind": "object", "identity": f"{value['object_type']}:{value['object_key']}", "sha256": managed_digest(value)}
    if arguments.kind == "project":
        value = load_project(arguments.input)
        return {"ok": True, "kind": "project", "project_key": value["project_key"], "site_key": value["site_key"]}
    if arguments.kind == "media":
        value = read_json(arguments.input)
        if not isinstance(value, dict):
            raise SyncError("invalid_media", "media input must be an object")
        validate_media_data(value)
        return {"ok": True, "kind": "media", "sha256": canonical_digest(value)}
    raise SyncError("invalid_kind", "validation kind is unsupported")


def command_pull(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    record = transport.get(arguments.object)
    obj = validate_managed_object(record["object"], git_safe=True)
    source_bytes = canonical_bytes(obj)
    source_sha = managed_digest(obj)
    if arguments.output.exists():
        existing = validate_managed_object(read_json(arguments.output))
        if managed_digest(existing) != source_sha:
            raise SyncError("local_conflict", "pull refuses to overwrite locally changed content")
    atomic_write(arguments.output, source_bytes, mode=0o600)
    lock = make_lock(project, record, source_sha)
    atomic_write_json(arguments.lock_output, lock, mode=0o600)
    return {"ok": True, "operation": "pull", "identity": arguments.object, "sha256": source_sha, "revision": record["revision"], "guard": record["guard"]}


def command_status(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    local, lock, identity = _load_local_and_lock(arguments, project)
    remote = transport.get(identity)
    return status_result(local, lock, remote)


def command_diff(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    local, lock, identity = _load_local_and_lock(arguments, project)
    remote = transport.get(identity)
    status = status_result(local, lock, remote)
    return {**status, "diff": unified_diff(local, remote["object"])}


def command_plan(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    local, lock, identity = _load_local_and_lock(arguments, project)
    remote = transport.get(identity)
    status = status_result(local, lock, remote)
    if status["state"] in {"remote-changed", "both-changed"}:
        action = "blocked-conflict"
    elif status["state"] == "local-changed":
        action = "apply"
    else:
        action = "no-op"
    return {**status, "operation": "plan", "action": action, "dry_run_required": True, "diff": unified_diff(local, remote["object"])}


def command_apply(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    local, lock, identity = _load_local_and_lock(arguments, project)
    if not arguments.require_atomic_check:
        raise SyncError("atomic_required", "apply requires --require-atomic-check")
    if transport.guard != "atomic-compare-and-swap":
        raise SyncError("atomic_unavailable", "transport cannot provide atomic compare-and-swap")
    if arguments.expected_remote_sha256 != lock["remote"]["sha256"] or str(arguments.expected_remote_revision) != str(lock["remote"]["revision"]):
        raise SyncError("expectation_mismatch", "apply expectations differ from the reviewed lock")
    if not re.fullmatch(r"issue-[0-9]+|pr-[0-9]+|approval-[A-Za-z0-9._-]+", arguments.approval_id):
        raise SyncError("approval_required", "apply requires a bounded approval identifier")
    dry_run = not arguments.execute
    result = transport.apply(
        local,
        expected_sha256=arguments.expected_remote_sha256,
        expected_revision=str(arguments.expected_remote_revision),
        idempotency_key=arguments.idempotency_key,
        dry_run=dry_run,
    )
    if dry_run:
        return {**result, "operation": "apply", "approval_id": arguments.approval_id}
    readback = transport.get(identity)
    desired = managed_digest(local)
    if readback["sha256"] != desired:
        raise SyncError("readback_mismatch", "post-apply canonical readback differs from desired content")
    new_lock = make_lock(project, readback, desired)
    atomic_write_json(arguments.lock, new_lock, mode=0o600)
    return {**result, "operation": "apply", "approval_id": arguments.approval_id, "lock_updated": True}


def command_inventory(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    result = inventory(project, transport.list_objects())
    if arguments.output:
        output_json(result, arguments.output)
    return result


def command_wave_plan(arguments: argparse.Namespace, project: Mapping[str, Any]) -> dict[str, Any]:
    inventory_payload = read_json(arguments.inventory)
    max_wave = arguments.max_wave_size or project["limits"]["max_wave_size"]
    if not 1 <= max_wave <= project["limits"]["max_wave_size"]:
        raise SyncError("invalid_wave_size", "wave size exceeds the project limit")
    waves = topological_waves(inventory_payload, max_wave)
    return {
        "schema_version": 1,
        "kind": "wordpress-migration-wave-plan",
        "project_key": project["project_key"],
        "inventory_sha256": canonical_digest(inventory_payload),
        "waves": [{"wave": index, "objects": wave, "state": "pending"} for index, wave in enumerate(waves, 1)],
        "requires_one_object_canary": True,
    }


def command_checkpoint(arguments: argparse.Namespace, project: Mapping[str, Any]) -> dict[str, Any]:
    plan = read_json(arguments.wave_plan)
    if not isinstance(plan, dict) or plan.get("kind") != "wordpress-migration-wave-plan":
        raise SyncError("invalid_wave_plan", "checkpoint requires a migration wave plan")
    if arguments.state not in {"planned", "running", "completed", "failed", "blocked", "rolled-back"}:
        raise SyncError("invalid_checkpoint_state", "checkpoint state is unsupported")
    if plan.get("project_key") != project["project_key"]:
        raise SyncError("wave_plan_target_mismatch", "wave plan belongs to another project")
    if not re.fullmatch(r"[A-Za-z0-9._:-]{8,128}", arguments.operation_id):
        raise SyncError("invalid_operation_id", "checkpoint operation_id is invalid")
    if arguments.wave < 1:
        raise SyncError("invalid_wave", "checkpoint wave must be positive")
    if not IDENTITY_PATTERN.fullmatch(arguments.object):
        raise SyncError("invalid_identity", "checkpoint object identity is invalid")
    if not SHA256_PATTERN.fullmatch(arguments.expected_sha256):
        raise SyncError("invalid_expected_hash", "checkpoint expected hash is invalid")
    if arguments.observed_sha256 is not None and not SHA256_PATTERN.fullmatch(arguments.observed_sha256):
        raise SyncError("invalid_observed_hash", "checkpoint observed hash is invalid")
    checkpoint = {
        "schema_version": 1,
        "kind": "wordpress-migration-checkpoint",
        "project_key": project["project_key"],
        "plan_sha256": canonical_digest(plan),
        "operation_id": arguments.operation_id,
        "wave": arguments.wave,
        "identity": arguments.object,
        "state": arguments.state,
        "expected_sha256": arguments.expected_sha256,
        "observed_sha256": arguments.observed_sha256,
        "updated_at": utc_now(),
        "resume_requires_readback": arguments.state not in {"completed", "rolled-back"},
    }
    reject_secret_fields(checkpoint)
    if arguments.output.exists():
        previous = read_json(arguments.output)
        if previous.get("operation_id") != arguments.operation_id:
            raise SyncError("checkpoint_collision", "checkpoint belongs to another operation")
        terminal = {"completed", "rolled-back"}
        if previous.get("state") in terminal and previous.get("state") != arguments.state:
            raise SyncError("checkpoint_terminal", "terminal checkpoints cannot be rewritten")
    atomic_write_json(arguments.output, checkpoint, mode=0o600)
    return {"ok": True, "operation": "checkpoint", "checkpoint": checkpoint}


def command_baseline(arguments: argparse.Namespace, project: Mapping[str, Any], transport: Any) -> dict[str, Any]:
    if arguments.output_dir.is_symlink():
        raise SyncError("unsafe_path", "baseline destination cannot be a symlink")
    destination = arguments.output_dir.expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise SyncError("output_not_empty", "baseline destination must be empty")
    records = transport.list_objects()
    inventory_payload = inventory(project, records)
    if inventory_payload["blocked"] and not arguments.allow_read_only_exceptions:
        raise SyncError("unsupported_inventory", "baseline contains unsupported objects", details={"objects": inventory_payload["blocked"]})
    destination.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for record in records:
        obj = record["object"]
        classification = classify_object(obj, project["adapter_policy"])
        if classification["compatibility"] != "supported":
            continue
        validate_managed_object(obj, git_safe=True)
        identity = record["identity"]
        filename = identity.replace(":", "__") + ".json"
        source_path = destination / "objects" / filename
        lock_path = destination / "locks" / filename
        atomic_write_json(source_path, obj, replace=False, mode=0o600)
        atomic_write_json(lock_path, make_lock(project, record, managed_digest(obj)), replace=False, mode=0o600)
        written.append(identity)
    atomic_write_json(destination / "inventory.json", inventory_payload, replace=False, mode=0o600)
    manifest = {
        "schema_version": 1,
        "kind": "wordpress-managed-object-manifest",
        "project_key": project["project_key"],
        "site_key": project["site_key"],
        "environment": project["environment"],
        "objects": written,
        "inventory_sha256": canonical_digest(inventory_payload),
        "created_at": utc_now(),
    }
    atomic_write_json(destination / "manifest.json", manifest, replace=False, mode=0o600)
    return {"ok": True, "operation": "baseline", "objects": written, "manifest_sha256": canonical_digest(manifest)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wp-content-sync")
    parser.add_argument("--json", action="store_true", help="emit structured JSON (default)")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--kind", choices=("object", "project", "media"), required=True)
    validate.add_argument("--input", type=Path, required=True)
    validate.add_argument("--git-safe", action="store_true")

    for name in ("pull", "status", "diff", "plan", "apply", "inventory", "wave-plan", "checkpoint", "baseline"):
        command = sub.add_parser(name)
        command.add_argument("--project", type=Path, required=True)
        if name in {"pull"}:
            command.add_argument("--object", required=True)
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--lock-output", type=Path, required=True)
            command.add_argument("--verify-remote", action="store_true", required=True)
        elif name in {"status", "diff", "plan", "apply"}:
            command.add_argument("--object")
            command.add_argument("--source", type=Path, required=True)
            command.add_argument("--lock", type=Path, required=True)
        if name == "apply":
            command.add_argument("--expected-remote-sha256", required=True)
            command.add_argument("--expected-remote-revision", required=True)
            command.add_argument("--require-atomic-check", action="store_true")
            command.add_argument("--idempotency-key", required=True)
            command.add_argument("--approval-id", required=True)
            command.add_argument("--execute", action="store_true", help="perform the reviewed write; otherwise dry-run")
        elif name == "inventory":
            command.add_argument("--output", type=Path)
        elif name == "wave-plan":
            command.add_argument("--inventory", type=Path, required=True)
            command.add_argument("--max-wave-size", type=int)
        elif name == "checkpoint":
            command.add_argument("--wave-plan", type=Path, required=True)
            command.add_argument("--operation-id", required=True)
            command.add_argument("--wave", type=int, required=True)
            command.add_argument("--object", required=True)
            command.add_argument("--state", required=True)
            command.add_argument("--expected-sha256", required=True)
            command.add_argument("--observed-sha256")
            command.add_argument("--output", type=Path, required=True)
        elif name == "baseline":
            command.add_argument("--output-dir", type=Path, required=True)
            command.add_argument("--allow-read-only-exceptions", action="store_true")

    code = sub.add_parser("code-export-plan")
    code.add_argument("--input-dir", type=Path, required=True)
    automation = sub.add_parser("automation-plan")
    automation.add_argument("--event", type=Path, required=True)
    return parser


def dispatch(arguments: argparse.Namespace) -> dict[str, Any]:
    if arguments.command == "validate":
        return command_validate(arguments)
    if arguments.command == "code-export-plan":
        return validate_code_export(arguments.input_dir)
    if arguments.command == "automation-plan":
        event = read_json(arguments.event)
        if not isinstance(event, dict):
            raise SyncError("invalid_event", "automation event must be an object")
        return automation_plan(event)
    project = load_project(arguments.project)
    transport = transport_for(project, arguments.project)
    handlers = {
        "pull": command_pull,
        "status": command_status,
        "diff": command_diff,
        "plan": command_plan,
        "apply": command_apply,
        "inventory": command_inventory,
        "wave-plan": command_wave_plan,
        "checkpoint": command_checkpoint,
        "baseline": command_baseline,
    }
    handler = handlers[arguments.command]
    if arguments.command in {"wave-plan", "checkpoint"}:
        return handler(arguments, project)
    return handler(arguments, project, transport)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        result = dispatch(arguments)
    except SyncError as error:
        output_json(error.payload())
        return 2
    except (OSError, ValueError):
        output_json(SyncError("operation_failure", "operation failed without a verified result").payload())
        return 3
    output_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
