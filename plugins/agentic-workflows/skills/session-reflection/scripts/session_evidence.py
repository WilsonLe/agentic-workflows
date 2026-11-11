#!/usr/bin/env python3
"""Project Codex thread pages into bounded, secret-safe reflection evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SECRET_PATTERNS = (
    re.compile(r"\b(?:gh[opusr]_|sk-|rk-)[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
    re.compile(r"(?i)\b(?:password|passphrase|access[_ -]?token|refresh[_ -]?token|api[_ -]?key|client[_ -]?secret|authorization|cookie)\s*[:=]\s*[^\s,;]+"),
    re.compile(r'(?i)"(?:password|passphrase|access_token|refresh_token|api_key|client_secret|authorization|cookie)"\s*:\s*"[^"]*"'),
    re.compile(r"https?://[^/\s:@]+:[^@\s/]+@", re.IGNORECASE),
)


def clean_text(value: str, *, limit: int) -> tuple[str, bool]:
    """Redact recognizable credentials and mark every shortened excerpt."""

    text = value.replace("\x00", " ")
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[redacted]", text)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[:limit].rstrip() + "…", True
    return text, False


def _message_text(item: dict[str, Any]) -> str:
    if item.get("type") == "userMessage":
        return " ".join(
            part.get("text", "") for part in item.get("content", [])
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return str(item.get("text", ""))


def _page(value: dict[str, Any]) -> dict[str, Any]:
    if "thread" in value and "turns" in value:
        return value
    blocks = value.get("content", [])
    for block in blocks:
        if block.get("type") == "text":
            candidate = json.loads(block["text"])
            if isinstance(candidate, dict) and "thread" in candidate:
                return candidate
    raise ValueError("input has no Codex thread page")


def triage_page(
    value: dict[str, Any], *, max_chars: int = 3200, message_chars: int = 120,
    requested_cursor: str = "",
) -> dict[str, Any]:
    """Retain stable IDs and user/outcome excerpts, never whole tool traces."""

    if max_chars < 500 or message_chars < 30:
        raise ValueError("output limits are too small for coverage metadata")
    page = _page(value)
    thread = page["thread"]
    turns = page.get("turns", [])
    result: dict[str, Any] = {
        "thread_id": thread.get("id"),
        "created_at": thread.get("createdAt"),
        "updated_at": thread.get("updatedAt"),
        "turn_ids": [turn.get("id") for turn in turns],
        "requested_cursor": requested_cursor,
        "page_next_cursor": page.get("page", {}).get("nextCursor"),
        "has_more": bool(page.get("page", {}).get("hasMore")),
        "messages": [],
        "omitted_message_ids": [],
        "tool_item_count": 0,
        "failed_tool_item_count": 0,
        "failed_tool_item_ids": [],
        "truncated": False,
    }
    candidates: list[dict[str, Any]] = []
    for turn in turns:
        for item in turn.get("items", []):
            kind = item.get("type")
            if kind == "userMessage" or kind == "agentMessage" and item.get("phase") == "final_answer":
                excerpt, shortened = clean_text(_message_text(item), limit=message_chars)
                candidates.append({
                    "id": item.get("id"), "turn_id": turn.get("id"),
                    "kind": "user" if kind == "userMessage" else "outcome",
                    "excerpt": excerpt, "excerpt_truncated": shortened,
                })
            elif kind in {"commandExecution", "mcpToolCall", "fileChange"}:
                result["tool_item_count"] += 1
                if item.get("status") == "failed" or item.get("exitCode") not in (None, 0):
                    result["failed_tool_item_count"] += 1
                    result["failed_tool_item_ids"].append(item.get("id"))
    # Account for the JSON envelope before adding excerpts. The omitted IDs preserve
    # drill-down coverage even when a long session exceeds the display budget.
    # User corrections are the primary retrospective signal. Reserve space for
    # them before lower-priority outcome excerpts; turn IDs retain source order.
    prioritized = [item for item in candidates if item["kind"] == "user"]
    prioritized.extend(item for item in candidates if item["kind"] == "outcome")
    for candidate in prioritized:
        trial = json.dumps({**result, "messages": result["messages"] + [candidate]},
                           separators=(",", ":"))
        if len(trial) <= max_chars:
            result["messages"].append(candidate)
        else:
            result["omitted_message_ids"].append(candidate["id"])
            result["truncated"] = True
    def compact() -> str:
        return json.dumps(result, separators=(",", ":"))
    if len(compact()) > max_chars:
        # IDs remain discoverable via the source page cursor and turn IDs.
        result["omitted_message_count"] = len(result["omitted_message_ids"])
        result["omitted_message_ids"] = []
    if len(compact()) > max_chars:
        result["failed_tool_item_ids"] = []
        result["truncated"] = True
    while len(compact()) > max_chars and result["messages"]:
        result["messages"].pop()
        result["omitted_message_count"] = result.get("omitted_message_count", 0) + 1
        result["truncated"] = True
    if len(compact()) > max_chars:
        raise ValueError("coverage metadata exceeds the output budget; increase --max-chars")
    return result


def detail_item(
    value: dict[str, Any], *, item_id: str, max_chars: int = 900
) -> dict[str, Any]:
    """Expand only a specifically selected item; omit command arguments."""

    page = _page(value)
    for turn in page.get("turns", []):
        for item in turn.get("items", []):
            if item.get("id") != item_id:
                continue
            kind = item.get("type", "unknown")
            raw = _message_text(item) if kind in {"userMessage", "agentMessage"} else str(
                item.get("output", item.get("error", ""))
            )
            excerpt, shortened = clean_text(raw, limit=max_chars)
            return {
                "thread_id": page["thread"].get("id"), "turn_id": turn.get("id"),
                "item_id": item_id, "kind": kind, "status": item.get("status"),
                "excerpt": excerpt, "excerpt_truncated": shortened,
                "source_digest": "sha256:" + hashlib.sha256(raw.encode()).hexdigest(),
            }
    raise ValueError(f"item {item_id} is not present on this page")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("triage", "detail"))
    parser.add_argument("source", type=Path)
    parser.add_argument("--item-id")
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--requested-cursor", default="")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.source.read_text(encoding="utf-8"))
        if args.mode == "detail":
            if not args.item_id:
                raise ValueError("detail mode requires --item-id")
            result = detail_item(payload, item_id=args.item_id,
                                 max_chars=args.max_chars or 900)
        else:
            result = triage_page(payload, max_chars=args.max_chars or 3200,
                                 requested_cursor=args.requested_cursor)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"session evidence error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
