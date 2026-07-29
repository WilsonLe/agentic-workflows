#!/usr/bin/env python3
"""Typed Excalidraw Plus REST API client with destructive-operation gating."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import ssl
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from excalidraw_credential_common import (
    CredentialError,
    atomic_private_write,
    git_container,
    load_credential,
    redact_exact,
)

API_ROOT = "https://api.excalidraw.com/api/v1"
CREDENTIALS = Path.home() / ".config" / "amsoft" / "excalidraw" / "credentials.json"
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_ERROR_BYTES = 65_536
DESTRUCTIVE_CONFIRMATION = "I_APPROVE_EXCALIDRAW_DESTRUCTIVE"
SUPPORTED_ELEMENTS = {
    "rectangle",
    "diamond",
    "ellipse",
    "embeddable",
    "frame",
    "magicframe",
    "iframe",
    "image",
    "text",
    "line",
    "arrow",
    "freedraw",
}


class ExcalidrawAPIError(CredentialError):
    """A sanitized Excalidraw API failure."""


class UnknownWriteOutcome(ExcalidrawAPIError):
    """The request may have reached Excalidraw but no response was received."""


@dataclass(frozen=True)
class Operation:
    method: str
    template: str
    body: bool = False
    destructive: bool = False
    replacement: bool = False
    backup_scene: bool = False


OPERATIONS = {
    "verify": Operation("GET", "/collections"),
    "collections": Operation("GET", "/collections"),
    "collection": Operation("GET", "/collections/{collection_id}"),
    "collection-scenes": Operation("GET", "/collections/{collection_id}/scenes"),
    "scenes": Operation("GET", "/scenes"),
    "scene": Operation("GET", "/scenes/{scene_id}"),
    "scene-content": Operation("GET", "/scenes/{scene_id}/content"),
    "workspace": Operation("GET", "/workspaces"),
    "users": Operation("GET", "/workspaces/users"),
    "user": Operation("GET", "/workspaces/users/{user_id}"),
    "invites": Operation("GET", "/workspaces/invites"),
    "invite": Operation("GET", "/workspaces/invites/{invite_id}"),
    "logs": Operation("GET", "/logs"),
    "collection-create": Operation("POST", "/collections", body=True),
    "collection-scene-create": Operation(
        "POST", "/collections/{collection_id}/scenes", body=True
    ),
    "collection-update": Operation("PATCH", "/collections/{collection_id}", body=True),
    "collection-delete": Operation(
        "DELETE", "/collections/{collection_id}", destructive=True
    ),
    "scene-create": Operation("POST", "/scenes", body=True),
    "scene-update": Operation(
        "PATCH", "/scenes/{scene_id}", body=True, backup_scene=True
    ),
    "scene-content-patch": Operation(
        "PATCH", "/scenes/{scene_id}/content", body=True, backup_scene=True
    ),
    "scene-content-replace": Operation(
        "PUT",
        "/scenes/{scene_id}/content",
        body=True,
        replacement=True,
        backup_scene=True,
    ),
    "scene-delete": Operation(
        "DELETE", "/scenes/{scene_id}", destructive=True, backup_scene=True
    ),
    "workspace-update": Operation("PATCH", "/workspaces", body=True),
    "user-update": Operation("PATCH", "/workspaces/users/{user_id}", body=True),
    "user-delete": Operation("DELETE", "/workspaces/users/{user_id}", destructive=True),
    "invite-create": Operation("POST", "/workspaces/invites", body=True),
    "invite-update": Operation("PATCH", "/workspaces/invites/{invite_id}", body=True),
    "invite-delete": Operation(
        "DELETE", "/workspaces/invites/{invite_id}", destructive=True
    ),
}


def tls_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    if context.cert_store_stats().get("x509_ca", 0) > 0:
        return context
    if platform.system() == "Darwin":
        system_bundle = Path("/etc/ssl/cert.pem")
        try:
            bundle_stat = system_bundle.lstat()
        except OSError:
            bundle_stat = None
        if (
            bundle_stat is not None
            and stat.S_ISREG(bundle_stat.st_mode)
            and not stat.S_ISLNK(bundle_stat.st_mode)
            and os.access(system_bundle, os.R_OK)
        ):
            return ssl.create_default_context(cafile=str(system_bundle))
    raise ExcalidrawAPIError("no trusted CA bundle is available for verified TLS")


def segment(value: str | None, name: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or any(character.isspace() for character in value)
    ):
        raise ExcalidrawAPIError(f"{name} must be one non-empty identifier")
    return urllib.parse.quote(value, safe="")


def bounded_pagination(limit: int, offset: int) -> dict[str, str]:
    if not 1 <= limit <= 100:
        raise ExcalidrawAPIError("limit must be between 1 and 100")
    if offset < 0:
        raise ExcalidrawAPIError("offset must be non-negative")
    return {"limit": str(limit), "offset": str(offset)}


def _error_detail(raw: bytes, token: str) -> str:
    text = redact_exact(raw.decode("utf-8", errors="replace"), token)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return ""
    if isinstance(payload, dict) and isinstance(payload.get("message"), str):
        return f": {payload['message'][:300]}"
    return ""


def request_json(
    token: str,
    method: str,
    path: str,
    *,
    query: dict[str, str] | None = None,
    body: object | None = None,
    timeout: float = 30,
    max_read_retries: int = 2,
) -> tuple[object, dict[str, str]]:
    if method not in {"GET", "POST", "PATCH", "PUT", "DELETE"}:
        raise ExcalidrawAPIError("unsupported HTTP method")
    if (
        not path.startswith("/")
        or "://" in path
        or any(character.isspace() for character in path)
    ):
        raise ExcalidrawAPIError("the API path is invalid")
    url = API_ROOT + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    encoded = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "amsoft-excalidraw/1",
    }
    if body is not None:
        encoded = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
        headers["Content-Type"] = "application/json"
    attempts = 0
    while True:
        request = urllib.request.Request(
            url, data=encoded, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(
                request, timeout=timeout, context=tls_context()
            ) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ExcalidrawAPIError(
                        "Excalidraw returned an oversized response"
                    )
                response_headers = {
                    key.lower(): value for key, value in response.headers.items()
                }
        except urllib.error.HTTPError as error:
            raw_error = error.read(MAX_ERROR_BYTES + 1)[:MAX_ERROR_BYTES]
            if method == "GET" and error.code == 429 and attempts < max_read_retries:
                attempts += 1
                reset = error.headers.get("X-RateLimit-Reset")
                wait = 1.0
                if reset:
                    try:
                        wait = max(0.0, min(5.0, float(reset) - time.time()))
                    except ValueError:
                        wait = 1.0
                time.sleep(wait)
                continue
            detail = _error_detail(raw_error, token)
            raise ExcalidrawAPIError(
                f"Excalidraw returned HTTP {error.code}{detail}"
            ) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if method != "GET":
                raise UnknownWriteOutcome(
                    "Excalidraw write outcome is unknown; do not retry blindly"
                ) from error
            if attempts < max_read_retries:
                attempts += 1
                time.sleep(min(2.0, 0.25 * (2**attempts)))
                continue
            raise ExcalidrawAPIError(
                "the Excalidraw API could not be reached"
            ) from error
        if not raw:
            payload: object = {}
        else:
            try:
                payload = json.loads(raw)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise ExcalidrawAPIError("Excalidraw returned invalid JSON") from error
        return payload, response_headers


def _finite(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_scene_content(payload: object, *, partial: bool) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ExcalidrawAPIError("scene content must be a JSON object")
    allowed = {
        "type",
        "version",
        "source",
        "appState",
        "elements",
        "sceneVersion",
        "files",
        "filesFailedToEmbed",
    }
    if not set(payload) <= allowed:
        raise ExcalidrawAPIError("scene content contains unsupported top-level fields")
    if partial:
        if not any(name in payload for name in ("elements", "appState", "files")):
            raise ExcalidrawAPIError(
                "a content patch requires elements, appState, or files"
            )
    else:
        for name in ("type", "version", "source", "appState", "elements", "files"):
            if name not in payload:
                raise ExcalidrawAPIError(f"complete scene content requires {name}")
        if payload.get("type") != "excalidraw":
            raise ExcalidrawAPIError("scene content type must be excalidraw")
        if not _finite(payload.get("version")):
            raise ExcalidrawAPIError("scene content version must be finite")
        if not isinstance(payload.get("source"), str):
            raise ExcalidrawAPIError("scene content source must be a string")
    app_state = payload.get("appState")
    if app_state is not None:
        if not isinstance(app_state, dict) or not set(app_state) <= {
            "viewBackgroundColor",
            "lockedMultiSelections",
        }:
            raise ExcalidrawAPIError("scene appState contains unsupported fields")
    elements = payload.get("elements", [])
    if elements is not None and not isinstance(elements, list):
        raise ExcalidrawAPIError("scene elements must be an array")
    files = payload.get("files", {})
    if files is not None and not isinstance(files, dict):
        raise ExcalidrawAPIError("scene files must be an object")
    by_id: dict[str, dict[str, object]] = {}
    for element in elements or []:
        if not isinstance(element, dict):
            raise ExcalidrawAPIError("every scene element must be an object")
        identifier = element.get("id")
        kind = element.get("type")
        if not isinstance(identifier, (str, int)) or str(identifier) in by_id:
            raise ExcalidrawAPIError(
                "scene element IDs must be unique strings or numbers"
            )
        if kind not in SUPPORTED_ELEMENTS:
            raise ExcalidrawAPIError("scene contains an unsupported element type")
        for field in ("x", "y", "width", "height", "angle"):
            if field in element and not _finite(element[field]):
                raise ExcalidrawAPIError(f"element {field} must be finite")
        by_id[str(identifier)] = element
    for identifier, element in by_id.items():
        frame_id = element.get("frameId")
        if frame_id is not None:
            target = by_id.get(str(frame_id))
            if target is None or target.get("type") not in {"frame", "magicframe"}:
                raise ExcalidrawAPIError(f"element {identifier} has an invalid frameId")
        if element.get("type") == "text" and element.get("containerId") is not None:
            target = by_id.get(str(element["containerId"]))
            if target is None or target.get("type") not in {
                "rectangle",
                "diamond",
                "ellipse",
                "arrow",
            }:
                raise ExcalidrawAPIError(
                    f"text {identifier} has an invalid containerId"
                )
            reverse = target.get("boundElements")
            if not isinstance(reverse, list) or not any(
                isinstance(item, dict)
                and str(item.get("id")) == identifier
                and item.get("type") == "text"
                for item in reverse
            ):
                raise ExcalidrawAPIError(
                    f"text {identifier} is missing its container reverse reference"
                )
        if element.get("type") == "image":
            file_id = element.get("fileId")
            if files is not None and file_id is not None and str(file_id) not in files:
                raise ExcalidrawAPIError(
                    f"image {identifier} references a missing file"
                )
        if element.get("type") in {"line", "arrow", "freedraw"}:
            points = element.get("points")
            if not isinstance(points, list) or not all(
                isinstance(point, list)
                and len(point) == 2
                and all(_finite(value) for value in point)
                for point in points
            ):
                raise ExcalidrawAPIError(f"element {identifier} has invalid points")
        if element.get("type") in {"line", "arrow"}:
            for binding_name in ("startBinding", "endBinding"):
                binding = element.get(binding_name)
                if binding is None:
                    continue
                if (
                    not isinstance(binding, dict)
                    or binding.get("mode") not in {"inside", "orbit", "skip"}
                    or str(binding.get("elementId")) not in by_id
                ):
                    raise ExcalidrawAPIError(
                        f"element {identifier} has an invalid {binding_name}"
                    )
                target = by_id[str(binding["elementId"])]
                reverse = target.get("boundElements")
                if not isinstance(reverse, list) or not any(
                    isinstance(item, dict)
                    and str(item.get("id")) == identifier
                    and item.get("type") == "arrow"
                    for item in reverse
                ):
                    raise ExcalidrawAPIError(
                        f"element {identifier} is missing a binding reverse reference"
                    )
        bound_elements = element.get("boundElements")
        if bound_elements is not None:
            if not isinstance(bound_elements, list):
                raise ExcalidrawAPIError(
                    f"element {identifier} has invalid boundElements"
                )
            for bound in bound_elements:
                if (
                    not isinstance(bound, dict)
                    or bound.get("type") not in {"arrow", "text"}
                    or str(bound.get("id")) not in by_id
                ):
                    raise ExcalidrawAPIError(
                        f"element {identifier} has an invalid bound reference"
                    )
    for file_id, file_record in (files or {}).items():
        if (
            not isinstance(file_record, dict)
            or str(file_record.get("id")) != str(file_id)
            or not isinstance(file_record.get("mimeType"), str)
            or not isinstance(file_record.get("dataURL"), str)
        ):
            raise ExcalidrawAPIError("scene contains an invalid file record")
    return payload


def validate_metadata_payload(
    command: str, payload: dict[str, object]
) -> dict[str, object]:
    if command in {"collection-create", "collection-update"}:
        if (
            set(payload) != {"name"}
            or not isinstance(payload.get("name"), str)
            or not str(payload["name"]).strip()
        ):
            raise ExcalidrawAPIError(
                "collection payload must contain one non-empty name"
            )
    elif command in {"scene-create", "collection-scene-create"}:
        required = (
            {"name", "pinned", "collectionId"}
            if command == "scene-create"
            else {"name", "pinned"}
        )
        if set(payload) != required:
            fields = ", ".join(sorted(required))
            raise ExcalidrawAPIError(f"{command} payload requires exactly: {fields}")
        if not isinstance(payload.get("name"), str) or not str(payload["name"]).strip():
            raise ExcalidrawAPIError("scene name must be non-empty")
        if not isinstance(payload.get("pinned"), bool):
            raise ExcalidrawAPIError("scene pinned must be boolean")
        if command == "scene-create" and (
            not isinstance(payload.get("collectionId"), str)
            or not payload["collectionId"]
        ):
            raise ExcalidrawAPIError("scene collectionId must be non-empty")
    elif command == "scene-update":
        if not payload or not set(payload) <= {"name", "pinned", "collectionId"}:
            raise ExcalidrawAPIError(
                "scene-update payload may contain name, pinned, or collectionId"
            )
        if "name" in payload and (
            not isinstance(payload["name"], str) or not str(payload["name"]).strip()
        ):
            raise ExcalidrawAPIError("scene name must be non-empty")
        if "pinned" in payload and not isinstance(payload["pinned"], bool):
            raise ExcalidrawAPIError("scene pinned must be boolean")
        if "collectionId" in payload and (
            not isinstance(payload["collectionId"], str) or not payload["collectionId"]
        ):
            raise ExcalidrawAPIError("scene collectionId must be non-empty")
    elif command == "workspace-update":
        _validate_workspace_payload(payload)
    elif command == "user-update":
        _validate_user_payload(payload)
    elif command in {"invite-create", "invite-update"}:
        _validate_invite_payload(command, payload)
    return payload


def _is_uri(value: object) -> bool:
    return isinstance(value, str) and bool(
        re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value)
    )


def _validate_workspace_payload(payload: dict[str, object]) -> None:
    if not payload or not set(payload) <= {"name", "picture"}:
        raise ExcalidrawAPIError("workspace-update payload may contain name or picture")
    if "name" in payload and not isinstance(payload["name"], str):
        raise ExcalidrawAPIError("workspace name must be a string")
    if (
        "picture" in payload
        and payload["picture"] is not None
        and not _is_uri(payload["picture"])
    ):
        raise ExcalidrawAPIError("workspace picture must be a URI or null")


def _validate_user_payload(payload: dict[str, object]) -> None:
    allowed = {"name", "picture", "workspaceTeams", "preferences", "role"}
    if not payload or not set(payload) <= allowed:
        raise ExcalidrawAPIError(
            "user-update payload contains unsupported or no fields"
        )
    if "name" in payload and not isinstance(payload["name"], str):
        raise ExcalidrawAPIError("user name must be a string")
    if (
        "picture" in payload
        and payload["picture"] is not None
        and not _is_uri(payload["picture"])
    ):
        raise ExcalidrawAPIError("user picture must be a URI or null")
    if "role" in payload and payload["role"] not in {"member", "admin"}:
        raise ExcalidrawAPIError("user role must be member or admin")
    if "workspaceTeams" in payload:
        teams = payload["workspaceTeams"]
        if not isinstance(teams, dict) or any(
            not isinstance(key, str)
            or not isinstance(value, list)
            or any(not isinstance(item, str) for item in value)
            for key, value in teams.items()
        ):
            raise ExcalidrawAPIError(
                "workspaceTeams must map string keys to string arrays"
            )
    if "preferences" in payload:
        preferences = payload["preferences"]
        boolean_fields = {
            "ossAutoRedirect",
            "hideDeprecatedFonts",
            "enableAutoSceneNamingForPrivateCollections",
            "blockCommentEmailNotifications",
        }
        allowed_preferences = boolean_fields | {"sceneOrder", "initialRedirect"}
        if (
            not isinstance(preferences, dict)
            or not set(preferences) <= allowed_preferences
        ):
            raise ExcalidrawAPIError("user preferences contain unsupported fields")
        if any(
            field in preferences and not isinstance(preferences[field], bool)
            for field in boolean_fields
        ):
            raise ExcalidrawAPIError("documented boolean preferences must be boolean")
        if "sceneOrder" in preferences and preferences["sceneOrder"] not in {
            "manual",
            "created",
            "updated",
            "name",
        }:
            raise ExcalidrawAPIError("user sceneOrder preference is invalid")
        if "initialRedirect" in preferences and preferences["initialRedirect"] not in {
            "dashboard",
            "lastEditedScene",
            "lastVisitedScene",
            "privateCollection",
        }:
            raise ExcalidrawAPIError("user initialRedirect preference is invalid")


def _validate_invite_payload(command: str, payload: dict[str, object]) -> None:
    allowed = {"email", "role", "maxUses", "restrictedDomains"}
    if not payload or not set(payload) <= allowed:
        raise ExcalidrawAPIError(f"{command} payload contains unsupported or no fields")
    if command == "invite-create":
        if "role" not in payload:
            raise ExcalidrawAPIError("invite-create requires role")
        if "email" in payload and set(payload) != {"email", "role"}:
            raise ExcalidrawAPIError("email invite-create accepts only email and role")
    if "role" in payload and payload["role"] not in {"member", "admin"}:
        raise ExcalidrawAPIError("invite role must be member or admin")
    if "email" in payload:
        email = payload["email"]
        if command == "invite-update" and email is None:
            pass
        elif not isinstance(email, str) or not re.fullmatch(
            r"(?!\.)(?!.*\.\.)[A-Za-z0-9_'+.-]*[A-Za-z0-9_+-]"
            r"@(?:[A-Za-z0-9][A-Za-z0-9-]*\.)+[A-Za-z]{2,}",
            email,
        ):
            raise ExcalidrawAPIError("invite email is invalid")
    if "maxUses" in payload:
        max_uses = payload["maxUses"]
        if max_uses != "unlimited" and (
            isinstance(max_uses, bool)
            or not isinstance(max_uses, int)
            or max_uses <= 0
            or max_uses > 9_007_199_254_740_991
        ):
            raise ExcalidrawAPIError(
                "invite maxUses must be a positive integer or unlimited"
            )
    if "restrictedDomains" in payload:
        domains = payload["restrictedDomains"]
        if domains is not None and (
            not isinstance(domains, list)
            or any(not isinstance(domain, str) for domain in domains)
        ):
            raise ExcalidrawAPIError(
                "invite restrictedDomains must be a string array or null"
            )


def load_payload(path: Path) -> dict[str, object]:
    expanded = path.expanduser().resolve(strict=True)
    if git_container(expanded) is not None:
        raise ExcalidrawAPIError("write payload files must be outside a Git worktree")
    try:
        payload = json.loads(expanded.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ExcalidrawAPIError("the write payload is not valid JSON") from error
    if not isinstance(payload, dict):
        raise ExcalidrawAPIError("the write payload must be a JSON object")
    forbidden = {"token", "apiKey", "api_key", "authorization"}

    def walk(value: object) -> None:
        if isinstance(value, dict):
            if any(
                str(key).lower() in {item.lower() for item in forbidden}
                for key in value
            ):
                raise ExcalidrawAPIError(
                    "write payloads cannot contain credential fields"
                )
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return payload


def resolve_path(operation: Operation, args: argparse.Namespace) -> str:
    path = operation.template
    for key, label in (
        ("collection_id", "collection ID"),
        ("scene_id", "scene ID"),
        ("user_id", "user ID"),
        ("invite_id", "invite ID"),
    ):
        placeholder = "{" + key + "}"
        if placeholder in path:
            path = path.replace(placeholder, segment(getattr(args, key), label))
    return path


def require_destructive_approval(
    operation: Operation, args: argparse.Namespace
) -> None:
    if operation.destructive and args.confirm_destructive != DESTRUCTIVE_CONFIRMATION:
        raise ExcalidrawAPIError("the destructive confirmation is required")


def create_backup(token: str, scene_id: str, backup_directory: Path) -> Path:
    expanded = backup_directory.expanduser().resolve(strict=False)
    if git_container(expanded) is not None:
        raise ExcalidrawAPIError("scene backups must be outside a Git worktree")
    metadata, _ = request_json(token, "GET", f"/scenes/{segment(scene_id, 'scene ID')}")
    content, _ = request_json(
        token, "GET", f"/scenes/{segment(scene_id, 'scene ID')}/content"
    )
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup = expanded / f"scene-{segment(scene_id, 'scene ID')}-{timestamp}.json"
    record = json.dumps(
        {
            "schema_version": 1,
            "scene_id": scene_id,
            "metadata": metadata,
            "content": content,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    atomic_private_write(backup, record)
    return backup


def execute(args: argparse.Namespace) -> dict[str, object]:
    operation = OPERATIONS[args.command]
    credential = load_credential(args.credentials_file)
    token = str(credential["token"])
    require_destructive_approval(operation, args)
    path = resolve_path(operation, args)
    query = None
    if args.command in {
        "verify",
        "collections",
        "collection-scenes",
        "scenes",
        "users",
        "invites",
        "logs",
    }:
        query = bounded_pagination(
            1 if args.command == "verify" else args.limit, args.offset
        )
        if args.command == "scenes" and args.collection_id:
            query["collectionId"] = args.collection_id
    if operation.body and args.payload is None:
        raise ExcalidrawAPIError("this operation requires --payload")
    payload = load_payload(args.payload) if operation.body else None
    if args.command == "scene-content-patch":
        payload = validate_scene_content(payload, partial=True)
    elif args.command == "scene-content-replace":
        payload = validate_scene_content(payload, partial=False)
    elif operation.body:
        payload = validate_metadata_payload(args.command, payload)
    backup_path = None
    if operation.backup_scene:
        if args.backup_directory is None:
            raise ExcalidrawAPIError("this scene write requires --backup-directory")
        backup_path = create_backup(token, args.scene_id, args.backup_directory)
    response, headers = request_json(
        token, operation.method, path, query=query, body=payload
    )
    output: dict[str, object] = {
        "operation": args.command,
        "method": operation.method,
        "path": path,
        "result": response,
        "rate_limit": {
            key: headers[key]
            for key in (
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            )
            if key in headers
        },
    }
    if backup_path is not None:
        output["backup_path"] = str(backup_path)
    return output


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("command", choices=sorted(OPERATIONS))
    result.add_argument("--credentials-file", type=Path, default=CREDENTIALS)
    result.add_argument("--collection-id")
    result.add_argument("--scene-id")
    result.add_argument("--user-id")
    result.add_argument("--invite-id")
    result.add_argument("--limit", type=int, default=10)
    result.add_argument("--offset", type=int, default=0)
    result.add_argument("--payload", type=Path)
    result.add_argument("--backup-directory", type=Path)
    result.add_argument("--confirm-destructive")
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        output = execute(args)
        print(json.dumps(output, sort_keys=True))
    except CredentialError as error:
        print(f"Excalidraw request refused: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
