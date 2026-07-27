#!/usr/bin/env python3
"""Small secret-safe ERPNext REST client for AMSoft skills."""

from __future__ import annotations

import argparse
import json
import os
import platform
import ssl
import stat
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


CREDENTIALS = Path.home() / ".config" / "amsoft" / "erpnext" / "credentials.json"
WRITE_PHRASE = "I_APPROVE_ERPNEXT_WRITE"


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def credentials() -> dict[str, str]:
    try:
        file_stat = CREDENTIALS.stat()
    except FileNotFoundError:
        fail(f"Credentials are not configured. Run onboarding for {CREDENTIALS}.")
    mode = stat.S_IMODE(file_stat.st_mode)
    if file_stat.st_uid != os.getuid() or mode != 0o400:
        fail(f"Refusing credentials with unexpected owner or mode; expected current user and 0400 at {CREDENTIALS}.")
    try:
        payload = json.loads(CREDENTIALS.read_text(encoding="utf-8"))
        values = {key: payload[key] for key in ("site_url", "api_key", "api_secret")}
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        fail("Protected credential file is invalid; rerun onboarding.")
    if not all(isinstance(value, str) and value for value in values.values()):
        fail("Protected credential file is invalid; rerun onboarding.")
    return values


def load_data(path: str | None) -> Any:
    if not path:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        fail("Request data file is not readable JSON.")


def trusted_ssl_context() -> ssl.SSLContext:
    """Use Python defaults, plus the macOS system CA bundle when Python lacks Keychain roots."""
    if platform.system() == "Darwin":
        macos_ca_bundle = Path("/etc/ssl/cert.pem")
        if macos_ca_bundle.is_file():
            return ssl.create_default_context(cafile=str(macos_ca_bundle))
    return ssl.create_default_context()


def call(method: str, path: str, query: dict[str, Any] | None = None, data: Any = None) -> Any:
    auth = credentials()
    if not path.startswith("/") or path.startswith("//") or "://" in path:
        fail("API path must be a site-relative path beginning with one slash.")
    url = auth["site_url"] + path
    if query:
        url += "?" + urlencode({key: json.dumps(value) if isinstance(value, (dict, list)) else value for key, value in query.items()})
    body = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"token {auth['api_key']}:{auth['api_secret']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AMSoft-ERPNext-Operations/0.1",
        },
    )
    try:
        with urlopen(request, timeout=30, context=trusted_ssl_context()) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {"status": response.status}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"message": raw[:1000]}
        safe_detail = {
            key: detail[key]
            for key in ("message", "exception", "exc_type")
            if isinstance(detail, dict) and key in detail
        }
        if not safe_detail:
            safe_detail = {"message": "ERPNext rejected the request."}
        print(json.dumps({"http_status": exc.code, "error": safe_detail}, indent=2), file=sys.stderr)
        raise SystemExit(2)
    except URLError as exc:
        fail(f"ERPNext request failed: {exc.reason}", 2)


def require_write_approval(value: str | None) -> None:
    if value != WRITE_PHRASE:
        fail(f"Write refused. After explicit user approval, pass --confirm-write {WRITE_PHRASE}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("whoami", help="Read the authenticated ERPNext user")
    sub.add_parser("user-summary", help="Read non-secret metadata and roles for the authenticated user")

    list_parser = sub.add_parser("list", help="List permitted documents")
    list_parser.add_argument("doctype")
    list_parser.add_argument("--fields", default='["name"]', help="JSON array")
    list_parser.add_argument("--filters", default="[]", help="JSON filters")
    list_parser.add_argument("--limit", type=int, default=20)

    get_parser = sub.add_parser("get", help="Read one permitted document")
    get_parser.add_argument("doctype")
    get_parser.add_argument("name")

    for command in ("create", "update"):
        item = sub.add_parser(command, help=f"{command.title()} a document after approval")
        item.add_argument("doctype")
        if command == "update":
            item.add_argument("name")
        item.add_argument("--data-file", required=True)
        item.add_argument("--confirm-write")

    delete_parser = sub.add_parser("delete", help="Delete a document after approval")
    delete_parser.add_argument("doctype")
    delete_parser.add_argument("name")
    delete_parser.add_argument("--confirm-write")

    method_parser = sub.add_parser("method", help="Call an allowed whitelisted method")
    method_parser.add_argument("method_name")
    method_parser.add_argument("--http-method", choices=("GET", "POST"), default="GET")
    method_parser.add_argument("--data-file")
    method_parser.add_argument("--confirm-write")

    args = parser.parse_args()
    if args.command == "whoami":
        result = call("GET", "/api/method/frappe.auth.get_logged_user")
    elif args.command == "user-summary":
        identity = call("GET", "/api/method/frappe.auth.get_logged_user").get("message")
        if not isinstance(identity, str) or not identity:
            fail("ERPNext returned an invalid authenticated identity.")
        user_response = call("GET", f"/api/resource/User/{quote(identity, safe='')}")
        user = user_response.get("data", {})
        result = {
            "data": {
                "name": user.get("name"),
                "enabled": user.get("enabled"),
                "user_type": user.get("user_type"),
                "role_profile_name": user.get("role_profile_name"),
                "roles": sorted(
                    row.get("role")
                    for row in user.get("roles", [])
                    if isinstance(row, dict) and isinstance(row.get("role"), str)
                ),
            }
        }
    elif args.command == "list":
        if args.limit < 1 or args.limit > 500:
            fail("--limit must be between 1 and 500")
        try:
            fields, filters = json.loads(args.fields), json.loads(args.filters)
        except json.JSONDecodeError:
            fail("--fields and --filters must be valid JSON")
        result = call(
            "GET",
            f"/api/resource/{quote(args.doctype, safe='')}",
            {"fields": fields, "filters": filters, "limit_page_length": args.limit},
        )
    elif args.command == "get":
        result = call("GET", f"/api/resource/{quote(args.doctype, safe='')}/{quote(args.name, safe='')}")
    elif args.command == "create":
        require_write_approval(args.confirm_write)
        result = call("POST", f"/api/resource/{quote(args.doctype, safe='')}", data=load_data(args.data_file))
    elif args.command == "update":
        require_write_approval(args.confirm_write)
        result = call(
            "PUT",
            f"/api/resource/{quote(args.doctype, safe='')}/{quote(args.name, safe='')}",
            data=load_data(args.data_file),
        )
    elif args.command == "delete":
        require_write_approval(args.confirm_write)
        result = call("DELETE", f"/api/resource/{quote(args.doctype, safe='')}/{quote(args.name, safe='')}")
    else:
        if args.http_method == "POST":
            require_write_approval(args.confirm_write)
        method_data = load_data(args.data_file)
        if args.http_method == "GET" and method_data is not None and not isinstance(method_data, dict):
            fail("GET method data must be a JSON object so it can be encoded as query parameters.")
        result = call(
            args.http_method,
            f"/api/method/{quote(args.method_name, safe='.')}",
            query=method_data if args.http_method == "GET" else None,
            data=method_data if args.http_method == "POST" else None,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
