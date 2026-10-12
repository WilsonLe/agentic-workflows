#!/usr/bin/env python3
"""Run read-only Cloudflare API requests with protected API-token credentials."""

from __future__ import annotations

import argparse
import json
import os
import platform
import ssl
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from account_credential_common import CredentialError, load_credential, redact_exact

CREDENTIALS = Path.home() / ".config" / "agentic-workflows" / "cloudflare" / "credentials.json"
API_ROOT = "https://api.cloudflare.com/client/v4"
TOKEN_TYPES = {"user_api_token", "account_api_token"}


class CloudflareAPIError(CredentialError):
    """A sanitized Cloudflare API failure."""


def tls_context() -> ssl.SSLContext:
    """Build a verified TLS context, including the macOS system bundle fallback."""
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
    raise CloudflareAPIError(
        "no trusted CA bundle is available for verified Cloudflare TLS"
    )


def request_json(token: str, path: str) -> dict[str, Any]:
    if not path.startswith("/") or "://" in path or any(char.isspace() for char in path):
        raise CloudflareAPIError("the API path is invalid")
    request = urllib.request.Request(
        API_ROOT + path,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "agentic-workflows/1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=30,
            context=tls_context(),
        ) as response:
            raw = response.read(1_048_577)
            if len(raw) > 1_048_576:
                raise CloudflareAPIError("Cloudflare returned an oversized response")
    except urllib.error.HTTPError as error:
        try:
            raw_error = error.read(65_537).decode("utf-8", errors="replace")
        except OSError:
            raw_error = ""
        safe = redact_exact(raw_error, [token], "[REDACTED_CLOUDFLARE_TOKEN]")
        detail = ""
        try:
            payload = json.loads(safe)
            errors = payload.get("errors", [])
            if isinstance(errors, list):
                messages = [
                    item.get("message")
                    for item in errors
                    if isinstance(item, dict) and isinstance(item.get("message"), str)
                ]
                detail = f": {'; '.join(messages[:3])}" if messages else ""
        except json.JSONDecodeError:
            pass
        raise CloudflareAPIError(
            f"Cloudflare returned HTTP {error.code}{detail}"
        ) from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise CloudflareAPIError("the Cloudflare API could not be reached") from error
    try:
        payload = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CloudflareAPIError("Cloudflare returned invalid JSON") from error
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise CloudflareAPIError("Cloudflare reported an unsuccessful response")
    return payload


def discover_account_ids(token: str) -> list[str]:
    payload = request_json(token, "/accounts?per_page=50")
    result = payload.get("result")
    if not isinstance(result, list):
        raise CloudflareAPIError("Cloudflare returned an unknown account-list shape")
    identifiers = [
        item.get("id")
        for item in result
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    if len(identifiers) != len(result):
        raise CloudflareAPIError("Cloudflare returned an unknown account-list shape")
    return identifiers


def verify_token(token: str, token_type: str, account_id: str | None = None) -> dict[str, Any]:
    if token_type == "user_api_token":
        payload = request_json(token, "/user/tokens/verify")
    elif token_type == "account_api_token":
        identifiers = discover_account_ids(token)
        selected = account_id
        if selected is None:
            if len(identifiers) != 1:
                raise CloudflareAPIError(
                    "account-token verification requires an explicit account ID "
                    "unless exactly one account is visible"
                )
            selected = identifiers[0]
        if selected not in identifiers:
            raise CloudflareAPIError("the selected account is not visible to this token")
        payload = request_json(token, f"/accounts/{selected}/tokens/verify")
    else:
        raise CloudflareAPIError("the protected Cloudflare token type is unsupported")
    result = payload.get("result")
    if not isinstance(result, dict) or result.get("status") != "active":
        raise CloudflareAPIError("Cloudflare did not report an active token")
    account_count = len(discover_account_ids(token))
    return {
        "provider": "cloudflare",
        "token_type": token_type,
        "status": "active",
        "visible_account_count": account_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file", type=Path, default=CREDENTIALS)
    parser.add_argument("--account-id", help=argparse.SUPPRESS)
    parser.add_argument("command", choices=("verify", "accounts"))
    args = parser.parse_args()
    try:
        record = load_credential(
            args.credentials_file,
            provider="cloudflare",
            token_types=TOKEN_TYPES,
        )
        token = str(record["token"])
        token_type = str(record["token_type"])
        if args.command == "verify":
            output = verify_token(token, token_type, args.account_id)
        else:
            output = {
                "provider": "cloudflare",
                "visible_account_count": len(discover_account_ids(token)),
            }
        print(json.dumps(output, sort_keys=True))
    except CredentialError as error:
        print(f"Cloudflare request refused: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
