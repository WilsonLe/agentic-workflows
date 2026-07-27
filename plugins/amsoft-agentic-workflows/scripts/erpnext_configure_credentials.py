#!/usr/bin/env python3
"""Install ERPNext API credentials without printing secret material."""

from __future__ import annotations

import argparse
import csv
import json
import os
import stat
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse


DESTINATION = Path.home() / ".config" / "amsoft" / "erpnext" / "credentials.json"


def fail(message: str) -> None:
    print(f"Credential setup failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_source(path: Path, site_url_override: str | None = None) -> dict[str, str]:
    if not path.exists() or not path.is_file():
        fail("the selected path is not a regular file")
    try:
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
            if len(rows) != 1:
                fail("the selected CSV must contain exactly one credential row")
            payload = {
                str(key).strip().lower(): value
                for key, value in rows[0].items()
                if key is not None
            }
        else:
            payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError):
        fail("the selected file is not readable JSON or CSV")
    if not isinstance(payload, dict):
        fail("the selected credential file must contain one object or CSV row")

    site_url = site_url_override or payload.get("site_url") or payload.get("url")
    api_key = payload.get("api_key") or payload.get("api_key_id")
    api_secret = payload.get("api_secret") or payload.get("api_key_secret")
    if not all(isinstance(value, str) and value.strip() for value in (site_url, api_key, api_secret)):
        fail("required values are site_url, api_key, and api_secret; pass --site-url for a two-column Frappe CSV")

    site_url = site_url.strip().rstrip("/")
    parsed = urlparse(site_url)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        fail("site_url must use HTTPS, except for an HTTP loopback development site")
    if parsed.username or parsed.password or not parsed.hostname:
        fail("site_url must be an origin without embedded credentials")

    source_mode = stat.S_IMODE(path.stat().st_mode)
    if source_mode & 0o077:
        print(
            "Warning: the source key file is readable by group or others; secure or remove it after setup.",
            file=sys.stderr,
        )
    return {"site_url": site_url, "api_key": api_key.strip(), "api_secret": api_secret.strip()}


def install(payload: dict[str, str], replace: bool) -> None:
    destination = DESTINATION
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination.parent, 0o700)
    if destination.exists() and not replace:
        fail(f"{destination} already exists; use --replace only for an approved credential rotation")

    encoded = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    temp_path: Path | None = None
    try:
        fd, raw_temp = tempfile.mkstemp(prefix=".credentials.", dir=destination.parent)
        temp_path = Path(raw_temp)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
        temp_path = None
        os.chmod(destination, 0o400)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    print(f"Installed protected ERPNext credentials at {destination}")
    print("Directory mode: 0700; credential file mode: 0400")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_file", type=Path, help="Path to the user-provided JSON or Frappe CSV key file")
    parser.add_argument("--site-url", help="ERPNext site origin when the source CSV does not contain it")
    parser.add_argument("--replace", action="store_true", help="Replace existing credentials during an approved rotation")
    args = parser.parse_args()
    install(load_source(args.source_file.expanduser().resolve(), args.site_url), args.replace)


if __name__ == "__main__":
    main()
