#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["tomlkit==0.13.3"]
# ///
"""Explicitly preview/apply/restore bundled local Codex defaults, without secrets output."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import uuid
from contextlib import contextmanager

import tomlkit

PRESET = Path(__file__).resolve().parents[1] / "templates" / "codex" / "config.toml"


class ConfigError(RuntimeError):
    """A sanitized configuration failure."""


def checked(path: Path) -> Path:
    """Reject links, non-files, foreign ownership, and Git-contained private state."""
    path = Path(os.path.abspath(path.expanduser()))
    for part in reversed((path, *path.parents)):
        if part.is_symlink() or (part / ".git").exists():
            raise ConfigError(
                "configuration and backups must be outside Git and symlink-free"
            )
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise ConfigError("expected a regular configuration file")
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise ConfigError("configuration must be owned by the current user")
    return path


def read(path: Path) -> bytes | None:
    checked(path)
    return path.read_bytes() if path.exists() else None


def digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    checked(path)
    fd, name = tempfile.mkstemp(prefix=".codex-config-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def locked(home: Path):
    lock = home / ".agentic-workflows-config.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ConfigError(
            "another configuration operation holds the lock; inspect before retrying"
        ) from error
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def merged(
    before: bytes | None,
    servers: list[str],
    plugin_servers: list[list[str]],
    *,
    all_servers: bool = False,
) -> bytes:
    try:
        document = tomlkit.parse((before or b"").decode("utf-8"))
        preset = tomlkit.parse(PRESET.read_text(encoding="utf-8"))
        if all_servers:
            servers = sorted(set(servers) | set(document.get("mcp_servers", {})))
            plugin_servers = plugin_servers + [
                [plugin, server]
                for plugin, values in document.get("plugins", {}).items()
                for server in values.get("mcp_servers", {})
            ]
        # Choose the supported legacy mode alone; retain custom profile definitions.
        document.pop("default_permissions", None)
        for key in ("approval_policy", "sandbox_mode", "web_search"):
            document[key] = preset[key]
        for section, values in (
            ("apps", preset["apps"]),
            ("computer_use", preset["computer_use"]),
        ):
            if section not in document:
                document[section] = tomlkit.table()
            if section == "apps":
                if "_default" not in document[section]:
                    document[section]["_default"] = tomlkit.table()
                document[section]["_default"].update(values["_default"])
            else:
                document[section].update(values)
        for server in servers:
            # Existing definitions only: never invent a connection or wildcard policy.
            document["mcp_servers"][server]["default_tools_approval_mode"] = "approve"
        for plugin, server in plugin_servers:
            document["plugins"][plugin]["mcp_servers"][server][
                "default_tools_approval_mode"
            ] = "approve"
        result = tomlkit.dumps(document).encode("utf-8")
        tomlkit.parse(result.decode("utf-8"))
        return result
    except Exception as error:
        raise ConfigError(
            "invalid TOML/table shape or named server is not configured; no changes applied"
        ) from error


def apply(
    home: Path,
    servers: list[str],
    plugin_servers: list[list[str]],
    *,
    preview: bool,
    all_servers: bool = False,
) -> dict:
    target = checked(home / "config.toml")
    home = target.parent
    before = read(target)
    after = merged(before, servers, plugin_servers, all_servers=all_servers)
    if after == before:
        return {"status": "unchanged"}
    if preview:
        return {
            "status": "preview",
            "changes": [
                "approval_policy",
                "sandbox_mode",
                "web_search",
                "apps._default",
                "computer_use.default_app_access",
            ],
            "removes_default_permissions": "default_permissions"
            in tomlkit.parse((before or b"").decode("utf-8")),
            "all_configured_servers": all_servers,
            "selected_mcp_server_count": len(servers) + len(plugin_servers),
        }
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    with locked(home):
        if read(target) != before:
            raise ConfigError("configuration changed during preparation; retry preview")
        mode = stat.S_IMODE(target.stat().st_mode) if before is not None else 0o600
        # Backups can contain credentials; create an independent, private directory.
        backup = home / ("agentic-workflows-config-backup-" + uuid.uuid4().hex)
        backup.mkdir(mode=0o700)
        if before is not None:
            atomic_write(backup / "config.toml", before)
        receipt = {
            "version": 1,
            "before_sha256": digest(before),
            "after_sha256": digest(after),
            "mode": mode,
        }
        atomic_write(backup / "receipt.json", json.dumps(receipt).encode("utf-8"))
        if read(target) != before:
            raise ConfigError(
                "configuration changed; backup retained, no activation performed"
            )
        atomic_write(target, after, mode)
    return {
        "status": "applied",
        "backup": str(backup),
        "restart": "start a new task/client and inspect effective permissions",
    }


def restore(home: Path, backup: Path) -> dict:
    target = checked(home / "config.toml")
    home = target.parent
    backup = Path(os.path.abspath(backup.expanduser()))
    if backup.parent != target.parent or not backup.name.startswith(
        "agentic-workflows-config-backup-"
    ):
        raise ConfigError(
            "backup must be the helper's backup directory in this Codex home"
        )
    try:
        receipt = json.loads(checked(backup / "receipt.json").read_bytes())
        before = read(backup / "config.toml")
        after_digest = receipt["after_sha256"]
        if (
            receipt["version"] != 1
            or digest(before) != receipt["before_sha256"]
            or not isinstance(after_digest, str)
            or len(after_digest) != 64
            or any(character not in "0123456789abcdef" for character in after_digest)
        ):
            raise ValueError()
        mode = receipt["mode"]
        if not isinstance(mode, int) or not 0 <= mode <= 0o777:
            raise ValueError()
    except (KeyError, ValueError, TypeError) as error:
        raise ConfigError("invalid backup; configuration was not changed") from error
    with locked(home):
        if digest(read(target)) != after_digest:
            raise ConfigError(
                "configuration changed since activation; preserve it and reconcile manually"
            )
        if before is None:
            target.unlink()
        else:
            atomic_write(target, before, mode)
    return {"status": "restored", "backup_retained": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("preview", "apply"):
        child = commands.add_parser(command)
        child.add_argument("--mcp-server", action="append", default=[])
        child.add_argument(
            "--plugin-server",
            nargs=2,
            action="append",
            default=[],
            metavar=("PLUGIN", "SERVER"),
        )
        child.add_argument(
            "--all-configured-servers",
            action="store_true",
            help="approve defaults for all MCP/plugin servers defined in this user config",
        )
    commands.add_parser("restore").add_argument("backup", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "restore":
            result = restore(args.codex_home, args.backup)
        else:
            result = apply(
                args.codex_home,
                args.mcp_server,
                args.plugin_server,
                preview=args.command == "preview",
                all_servers=args.all_configured_servers,
            )
        print(json.dumps(result))
        return 0
    except (ConfigError, OSError) as error:
        # Never print parser or OS exceptions, which can contain private content.
        print(
            str(error)
            if isinstance(error, ConfigError)
            else "configuration I/O failed; inspect local files before retrying",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
