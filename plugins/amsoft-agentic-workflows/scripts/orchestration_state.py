#!/usr/bin/env python3
"""Maintain a minimal, secret-safe Agent Orchestration coordination register."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1
TASK_STATUSES = {
    "active",
    "waiting",
    "needs_attention",
    "blocked",
    "completed",
    "archived_known",
    "excluded",
}
GOAL_STATES = {"clarifying", "active", "completed", "blocked"}
ARCHIVE_STATES = {"unarchived", "archive_intent", "archived"}
RUN_MODES = {"observed_peer", "issue_session"}
CLEANUP_STATES = {
    "not_applicable",
    "active",
    "cleanup_intent",
    "cleaned",
    "preserved",
}
CLOSEOUT_RESULTS = {
    None,
    "pending",
    "reconciled",
    "ineligible",
    "archived",
    "recovered",
}
BLOCKER_CATEGORIES = {
    None,
    "user_input",
    "dependency",
    "tooling",
    "unknown",
}
REGISTER_KEYS = {
    "schema_version",
    "project_id",
    "orchestrator_id",
    "goal",
    "inventory",
    "tasks",
    "updated_at",
}
TASK_KEYS = {
    "thread_id",
    "host_id",
    "project_id",
    "title",
    "status",
    "issue_number",
    "pr_number",
    "cursor",
    "archive_state",
    "last_observed_at",
    "last_action_at",
    "terminal_verified",
    "final_read",
    "reconciled",
    "needed_for_dependency",
    "closeout_result",
    "blocker_category",
    "run_mode",
    "worktree_path",
    "branch_name",
    "base_revision",
    "cleanup_state",
}
LEGACY_TASK_KEYS = TASK_KEYS - {
    "run_mode",
    "worktree_path",
    "branch_name",
    "base_revision",
    "cleanup_state",
}
TRIAGE_KEYS = {
    "issue_number",
    "priority",
    "blocked",
    "minor_dependency",
    "valuable",
    "overlap_keys",
}
FORBIDDEN_FIELD = re.compile(
    r"(?:^|_)(?:prompt|message|body|output|source_code|secret|token|password|"
    r"authorization|cookie|credential|environment_value)(?:_|$)",
    re.IGNORECASE,
)
SECRET_VALUE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._~+/=-]{16,}|"
    r"password\s*[:=]|authorization\s*[:=]|api[_-]?key\s*[:=])",
    re.IGNORECASE,
)


class OrchestrationStateError(RuntimeError):
    """Raised when coordination state is unsafe or invalid."""


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def parse_time(value: Any, label: str, *, nullable: bool = False) -> datetime | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value:
        raise OrchestrationStateError(f"{label} must be an RFC 3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise OrchestrationStateError(
            f"{label} must be an RFC 3339 timestamp"
        ) from error
    if parsed.tzinfo is None:
        raise OrchestrationStateError(f"{label} must include a timezone")
    return parsed


def require_text(
    value: Any,
    label: str,
    *,
    nullable: bool = False,
    maximum: int | None = None,
) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value:
        raise OrchestrationStateError(f"{label} must be non-empty text")
    if any(ord(character) < 32 for character in value):
        raise OrchestrationStateError(f"{label} contains control characters")
    if maximum is not None and len(value) > maximum:
        raise OrchestrationStateError(f"{label} exceeds {maximum} characters")
    if SECRET_VALUE.search(value):
        raise OrchestrationStateError(f"{label} contains secret-shaped text")
    return value


def validate_no_forbidden_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise OrchestrationStateError(f"{path} contains a non-text field")
            if FORBIDDEN_FIELD.search(key):
                raise OrchestrationStateError(
                    f"{path}.{key} is a prohibited coordination-state field"
                )
            validate_no_forbidden_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            validate_no_forbidden_fields(nested, f"{path}[{index}]")
    elif isinstance(value, str) and SECRET_VALUE.search(value):
        raise OrchestrationStateError(f"{path} contains secret-shaped text")


def positive_number(value: Any, label: str, *, nullable: bool = True) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise OrchestrationStateError(f"{label} must be a positive integer")
    return value


def absolute_path_text(value: Any, label: str, *, nullable: bool = True) -> str | None:
    text = require_text(value, label, nullable=nullable, maximum=1000)
    if text is None:
        return None
    windows_absolute = bool(re.match(r"^[A-Za-z]:[\\\\/]", text))
    if not Path(text).is_absolute() and not windows_absolute:
        raise OrchestrationStateError(f"{label} must be an absolute path")
    return text


def validate_task(task_value: Any, project_id: str, index: int = 0) -> dict[str, Any]:
    if not isinstance(task_value, dict):
        raise OrchestrationStateError(f"tasks[{index}] must be an object")
    if set(task_value) != TASK_KEYS:
        missing = sorted(TASK_KEYS - set(task_value))
        unexpected = sorted(set(task_value) - TASK_KEYS)
        raise OrchestrationStateError(
            f"tasks[{index}] fields differ: missing={missing}, unexpected={unexpected}"
        )
    task = task_value
    require_text(task["thread_id"], f"tasks[{index}].thread_id")
    require_text(
        task["host_id"],
        f"tasks[{index}].host_id",
        nullable=True,
        maximum=200,
    )
    if task["project_id"] != project_id:
        raise OrchestrationStateError(
            f"tasks[{index}].project_id differs from the register"
        )
    require_text(task["title"], f"tasks[{index}].title", maximum=160)
    if task["status"] not in TASK_STATUSES:
        raise OrchestrationStateError(f"tasks[{index}].status is unsupported")
    positive_number(task["issue_number"], f"tasks[{index}].issue_number")
    positive_number(task["pr_number"], f"tasks[{index}].pr_number")
    require_text(
        task["cursor"],
        f"tasks[{index}].cursor",
        nullable=True,
        maximum=1000,
    )
    if task["archive_state"] not in ARCHIVE_STATES:
        raise OrchestrationStateError(
            f"tasks[{index}].archive_state is unsupported"
        )
    parse_time(task["last_observed_at"], f"tasks[{index}].last_observed_at")
    parse_time(
        task["last_action_at"],
        f"tasks[{index}].last_action_at",
        nullable=True,
    )
    for field in (
        "terminal_verified",
        "final_read",
        "reconciled",
        "needed_for_dependency",
    ):
        if not isinstance(task[field], bool):
            raise OrchestrationStateError(
                f"tasks[{index}].{field} must be boolean"
            )
    if task["closeout_result"] not in CLOSEOUT_RESULTS:
        raise OrchestrationStateError(
            f"tasks[{index}].closeout_result is unsupported"
        )
    if task["blocker_category"] not in BLOCKER_CATEGORIES:
        raise OrchestrationStateError(
            f"tasks[{index}].blocker_category is unsupported"
        )
    if task["run_mode"] not in RUN_MODES:
        raise OrchestrationStateError(f"tasks[{index}].run_mode is unsupported")
    absolute_path_text(
        task["worktree_path"],
        f"tasks[{index}].worktree_path",
        nullable=True,
    )
    branch_name = require_text(
        task["branch_name"],
        f"tasks[{index}].branch_name",
        nullable=True,
        maximum=240,
    )
    if branch_name is not None and (
        branch_name.startswith(("-", "."))
        or ".." in branch_name
        or branch_name.endswith((".", "/"))
    ):
        raise OrchestrationStateError(
            f"tasks[{index}].branch_name is unsafe"
        )
    base_revision = require_text(
        task["base_revision"],
        f"tasks[{index}].base_revision",
        nullable=True,
        maximum=64,
    )
    if base_revision is not None and not re.fullmatch(
        r"[0-9a-fA-F]{7,64}", base_revision
    ):
        raise OrchestrationStateError(
            f"tasks[{index}].base_revision must be a Git object ID"
        )
    if task["cleanup_state"] not in CLEANUP_STATES:
        raise OrchestrationStateError(
            f"tasks[{index}].cleanup_state is unsupported"
        )
    if task["run_mode"] == "issue_session":
        for field in (
            "issue_number",
            "host_id",
            "worktree_path",
            "branch_name",
            "base_revision",
        ):
            if task[field] is None:
                raise OrchestrationStateError(
                    f"tasks[{index}] issue session requires {field}"
                )
        if task["cleanup_state"] == "not_applicable":
            raise OrchestrationStateError(
                f"tasks[{index}] issue session requires cleanup tracking"
            )
    elif any(
        task[field] is not None
        for field in ("worktree_path", "branch_name", "base_revision")
    ) or task["cleanup_state"] != "not_applicable":
        raise OrchestrationStateError(
            f"tasks[{index}] observed peer must not own issue-session resources"
        )
    if task["archive_state"] == "archived" and task["closeout_result"] != "archived":
        raise OrchestrationStateError(
            f"tasks[{index}] archived state requires archived closeout result"
        )
    return task


def migrate_register(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OrchestrationStateError("register must contain an object")
    version = payload.get("schema_version")
    if version == SCHEMA_VERSION:
        return validate_register(payload)
    if version != LEGACY_SCHEMA_VERSION:
        raise OrchestrationStateError(
            "unsupported schema version; migrate incompatible records explicitly"
        )
    if set(payload) != REGISTER_KEYS or not isinstance(payload.get("tasks"), list):
        raise OrchestrationStateError("legacy register fields differ")
    migrated = copy.deepcopy(payload)
    migrated["schema_version"] = SCHEMA_VERSION
    for index, task in enumerate(migrated["tasks"]):
        if not isinstance(task, dict) or set(task) != LEGACY_TASK_KEYS:
            raise OrchestrationStateError(
                f"legacy tasks[{index}] fields differ"
            )
        task.update(
            {
                "run_mode": "observed_peer",
                "worktree_path": None,
                "branch_name": None,
                "base_revision": None,
                "cleanup_state": "not_applicable",
            }
        )
    return validate_register(migrated)


def validate_register(payload: Any) -> dict[str, Any]:
    validate_no_forbidden_fields(payload)
    if not isinstance(payload, dict):
        raise OrchestrationStateError("register must contain an object")
    if set(payload) != REGISTER_KEYS:
        missing = sorted(REGISTER_KEYS - set(payload))
        unexpected = sorted(set(payload) - REGISTER_KEYS)
        raise OrchestrationStateError(
            f"register fields differ: missing={missing}, unexpected={unexpected}"
        )
    if payload["schema_version"] != SCHEMA_VERSION:
        raise OrchestrationStateError(
            "unsupported schema version; migrate incompatible records explicitly"
        )
    project_id = require_text(payload["project_id"], "project_id")
    require_text(payload["orchestrator_id"], "orchestrator_id")
    goal = payload["goal"]
    if not isinstance(goal, dict) or set(goal) != {"state", "last_checked_at"}:
        raise OrchestrationStateError("goal fields differ")
    if goal["state"] not in GOAL_STATES:
        raise OrchestrationStateError("goal.state is unsupported")
    parse_time(goal["last_checked_at"], "goal.last_checked_at", nullable=True)
    inventory = payload["inventory"]
    inventory_keys = {"complete", "limitation", "rotation_offset"}
    if not isinstance(inventory, dict) or set(inventory) != inventory_keys:
        raise OrchestrationStateError("inventory fields differ")
    if not isinstance(inventory["complete"], bool):
        raise OrchestrationStateError("inventory.complete must be boolean")
    if not isinstance(inventory["limitation"], str):
        raise OrchestrationStateError("inventory.limitation must be text")
    if len(inventory["limitation"]) > 240:
        raise OrchestrationStateError("inventory.limitation exceeds 240 characters")
    if SECRET_VALUE.search(inventory["limitation"]):
        raise OrchestrationStateError(
            "inventory.limitation contains secret-shaped text"
        )
    offset = inventory["rotation_offset"]
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise OrchestrationStateError(
            "inventory.rotation_offset must be a non-negative integer"
        )
    if not isinstance(payload["tasks"], list):
        raise OrchestrationStateError("tasks must be a list")
    seen: set[str] = set()
    for index, task in enumerate(payload["tasks"]):
        validated = validate_task(task, str(project_id), index)
        thread_id = str(validated["thread_id"])
        if thread_id in seen:
            raise OrchestrationStateError(f"duplicate task ID: {thread_id}")
        seen.add(thread_id)
    parse_time(payload["updated_at"], "updated_at")
    return payload


def state_directory(
    *,
    platform_name: str | None = None,
    environment: Any = None,
    home: Path | None = None,
) -> Path:
    selected_platform = platform_name or os.name
    selected_environment = environment if environment is not None else os.environ
    selected_home = home if home is not None else Path.home()

    def absolute(value: str, label: str) -> Path:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise OrchestrationStateError(f"{label} must be an absolute path")
        return path

    explicit = selected_environment.get("AMSOFT_ORCHESTRATION_STATE_DIR")
    if explicit:
        return absolute(explicit, "AMSOFT_ORCHESTRATION_STATE_DIR")
    if selected_platform == "nt" and selected_environment.get("LOCALAPPDATA"):
        return (
            absolute(selected_environment["LOCALAPPDATA"], "LOCALAPPDATA")
            / "AMSoft"
            / "agent-orchestration"
        )
    if selected_environment.get("XDG_STATE_HOME"):
        return (
            absolute(selected_environment["XDG_STATE_HOME"], "XDG_STATE_HOME")
            / "amsoft"
            / "agent-orchestration"
        )
    return selected_home / ".local" / "state" / "amsoft" / "agent-orchestration"


def identity_digest(value: str) -> str:
    require_text(value, "identity")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def register_path(
    project_id: str,
    orchestrator_id: str,
    *,
    root: Path | None = None,
) -> Path:
    selected_root = (root or state_directory()).expanduser()
    if not selected_root.is_absolute():
        raise OrchestrationStateError("state root must be an absolute path")
    if selected_root.exists() and selected_root.is_symlink():
        raise OrchestrationStateError("state root must not be a symlink")
    path = (
        selected_root
        / identity_digest(project_id)
        / identity_digest(orchestrator_id)
        / "register.json"
    )
    try:
        path.relative_to(selected_root)
    except ValueError as error:
        raise OrchestrationStateError("register path escapes the state root") from error
    for candidate in (path.parent.parent, path.parent):
        if candidate.exists() and candidate.is_symlink():
            raise OrchestrationStateError("register path contains a symlink")
    return path


def new_register(
    project_id: str,
    orchestrator_id: str,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    current = timestamp or now_utc()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "orchestrator_id": orchestrator_id,
        "goal": {"state": "clarifying", "last_checked_at": None},
        "inventory": {
            "complete": False,
            "limitation": "Live project inventory has not been recorded.",
            "rotation_offset": 0,
        },
        "tasks": [],
        "updated_at": current,
    }
    return migrate_register(payload)


def load_register(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise OrchestrationStateError("register must not be a symlink")
    try:
        details = path.stat()
    except OSError as error:
        raise OrchestrationStateError(f"cannot inspect register: {error}") from error
    if not stat.S_ISREG(details.st_mode):
        raise OrchestrationStateError("register must be a regular file")
    if os.name != "nt":
        if details.st_uid != os.getuid():
            raise OrchestrationStateError("register must be owned by the current user")
        if stat.S_IMODE(details.st_mode) & 0o077:
            raise OrchestrationStateError("register permissions must be owner-only")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise OrchestrationStateError(f"cannot read register safely: {error}") from error
    return migrate_register(payload)


def write_register(path: Path, payload: dict[str, Any]) -> None:
    validate_register(payload)
    if path.exists():
        load_register(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        path.parent.parent.chmod(0o700)
        path.parent.chmod(0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".register.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        if os.name != "nt":
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        if os.name != "nt":
            path.chmod(0o600)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def default_task(
    *,
    thread_id: str,
    project_id: str,
    status: str,
    observed_at: str,
    host_id: str | None = None,
    title: str = "",
    issue_number: int | None = None,
    pr_number: int | None = None,
    run_mode: str = "observed_peer",
    worktree_path: str | None = None,
    branch_name: str | None = None,
    base_revision: str | None = None,
) -> dict[str, Any]:
    task = {
        "thread_id": thread_id,
        "host_id": host_id,
        "project_id": project_id,
        "title": title,
        "status": status,
        "issue_number": issue_number,
        "pr_number": pr_number,
        "cursor": None,
        "archive_state": "unarchived",
        "last_observed_at": observed_at,
        "last_action_at": None,
        "terminal_verified": False,
        "final_read": False,
        "reconciled": False,
        "needed_for_dependency": False,
        "closeout_result": "pending",
        "blocker_category": None,
        "run_mode": run_mode,
        "worktree_path": worktree_path,
        "branch_name": branch_name,
        "base_revision": base_revision,
        "cleanup_state": (
            "active" if run_mode == "issue_session" else "not_applicable"
        ),
    }
    return validate_task(task, project_id)


def upsert_task(register: dict[str, Any], task: dict[str, Any]) -> None:
    validate_register(register)
    validated = validate_task(task, register["project_id"])
    current = next(
        (
            item
            for item in register["tasks"]
            if item["thread_id"] == validated["thread_id"]
        ),
        None,
    )
    if current is not None:
        old_time = parse_time(current["last_observed_at"], "existing observation")
        new_time = parse_time(validated["last_observed_at"], "new observation")
        assert old_time is not None and new_time is not None
        if new_time < old_time:
            raise OrchestrationStateError("stale live observation cannot replace newer state")
        register["tasks"].remove(current)
    register["tasks"].append(validated)
    register["tasks"].sort(key=lambda item: item["thread_id"])
    register["updated_at"] = now_utc()
    validate_register(register)


def format_title(
    *,
    status: str,
    issue_number: int | None = None,
    pr_number: int | None = None,
    fallback_kind: str | None = None,
    fallback_text: str | None = None,
) -> str:
    normalized_status = " ".join(status.split())
    if "|" in normalized_status or len(normalized_status.split()) > 3:
        raise OrchestrationStateError("status must be a short operational phrase")
    require_text(normalized_status, "status", maximum=24)
    references: list[str] = []
    if issue_number is not None:
        references.append(f"Issue #{positive_number(issue_number, 'issue_number')}")
    if pr_number is not None:
        references.append(f"PR #{positive_number(pr_number, 'pr_number')}")
    if not references:
        if fallback_kind not in {"Project", "Task"}:
            raise OrchestrationStateError(
                "fallback_kind must be Project or Task without an issue or PR"
            )
        normalized_fallback = " ".join((fallback_text or "").split())
        require_text(normalized_fallback, "fallback_text", maximum=36)
        if "|" in normalized_fallback:
            raise OrchestrationStateError("fallback_text must not contain a separator")
        references.append(f"{fallback_kind} {normalized_fallback}")
    return " | ".join([*references, normalized_status])


def archive_eligible(task: dict[str, Any]) -> bool:
    terminal = task["status"] == "completed" or (
        task["run_mode"] == "issue_session" and task["status"] == "blocked"
    )
    if task["run_mode"] == "observed_peer":
        blocker_safe = task["blocker_category"] is None
        dependency_safe = not task["needed_for_dependency"]
    elif task["status"] == "blocked":
        blocker_safe = task["blocker_category"] in {
            "user_input",
            "dependency",
            "tooling",
        }
        dependency_safe = True
    else:
        blocker_safe = task["blocker_category"] is None
        dependency_safe = True
    return bool(
        terminal
        and task["archive_state"] == "unarchived"
        and task["terminal_verified"]
        and task["final_read"]
        and task["reconciled"]
        and dependency_safe
        and blocker_safe
    )


def cleanup_eligible(
    task: dict[str, Any],
    *,
    worktree_clean: bool,
    branch_evidence_preserved: bool,
    task_owned: bool,
) -> bool:
    return bool(
        task["run_mode"] == "issue_session"
        and task["archive_state"] == "archived"
        and task["cleanup_state"] == "active"
        and task["worktree_path"]
        and task["branch_name"]
        and task["base_revision"]
        and worktree_clean
        and branch_evidence_preserved
        and task_owned
    )


def set_cleanup_state(
    register: dict[str, Any],
    *,
    thread_id: str,
    cleanup_state: str,
    worktree_clean: bool = False,
    branch_evidence_preserved: bool = False,
    task_owned: bool = False,
) -> dict[str, Any]:
    validate_register(register)
    task = resolve_task(register, thread_id)
    if task["run_mode"] != "issue_session":
        raise OrchestrationStateError(
            "cleanup state applies only to issue sessions"
        )
    if cleanup_state == "cleanup_intent":
        if not cleanup_eligible(
            task,
            worktree_clean=worktree_clean,
            branch_evidence_preserved=branch_evidence_preserved,
            task_owned=task_owned,
        ):
            raise OrchestrationStateError(
                "issue session is not eligible for cleanup intent"
            )
        task["cleanup_state"] = "cleanup_intent"
    elif cleanup_state == "cleaned":
        if task["cleanup_state"] != "cleanup_intent":
            raise OrchestrationStateError(
                "cleanup result requires a recorded cleanup intent"
            )
        task["cleanup_state"] = "cleaned"
    elif cleanup_state == "preserved":
        if task["archive_state"] != "archived" or task["cleanup_state"] not in {
            "active",
            "cleanup_intent",
        }:
            raise OrchestrationStateError(
                "preserved cleanup result requires an archived issue session"
            )
        task["cleanup_state"] = "preserved"
    else:
        raise OrchestrationStateError("cleanup state is unsupported")
    task["last_action_at"] = now_utc()
    register["updated_at"] = now_utc()
    validate_register(register)
    return task


def triage_issue_candidates(
    issues: Iterable[dict[str, Any]],
    *,
    capacity: int,
    active_overlap_keys: Iterable[str] = (),
) -> list[dict[str, Any]]:
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 0:
        raise OrchestrationStateError("triage capacity must be a non-negative integer")
    occupied: set[str] = set()
    for index, key in enumerate(active_overlap_keys):
        occupied.add(str(require_text(key, f"active_overlap_keys[{index}]", maximum=120)))

    normalized: list[dict[str, Any]] = []
    seen: set[int] = set()
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict) or set(issue) != TRIAGE_KEYS:
            raise OrchestrationStateError(f"issues[{index}] fields differ")
        number = positive_number(issue["issue_number"], f"issues[{index}].issue_number")
        assert number is not None
        if number in seen:
            raise OrchestrationStateError(f"duplicate issue number: {number}")
        seen.add(number)
        priority = issue["priority"]
        if isinstance(priority, bool) or not isinstance(priority, int) or priority < 0:
            raise OrchestrationStateError(
                f"issues[{index}].priority must be a non-negative integer"
            )
        for field in ("blocked", "minor_dependency", "valuable"):
            if not isinstance(issue[field], bool):
                raise OrchestrationStateError(f"issues[{index}].{field} must be boolean")
        keys = issue["overlap_keys"]
        if not isinstance(keys, list):
            raise OrchestrationStateError(
                f"issues[{index}].overlap_keys must be a list"
            )
        normalized_keys = [
            str(require_text(key, f"issues[{index}].overlap_keys", maximum=120))
            for key in keys
        ]
        if len(normalized_keys) != len(set(normalized_keys)):
            raise OrchestrationStateError(
                f"issues[{index}].overlap_keys contains duplicates"
            )
        normalized.append({**issue, "issue_number": number, "overlap_keys": normalized_keys})

    remaining = capacity
    decisions: list[dict[str, Any]] = []
    for issue in sorted(normalized, key=lambda item: (-item["priority"], item["issue_number"])):
        overlap = occupied.intersection(issue["overlap_keys"])
        if issue["blocked"]:
            decision = "blocked"
            reason = "A genuine dependency or required channel blocks meaningful progress."
        elif not issue["valuable"]:
            decision = "defer"
            reason = "No independently valuable ready lane is currently identified."
        elif overlap:
            decision = "defer"
            reason = "The ready lane conflicts with active overlap ownership."
        elif remaining == 0:
            decision = "defer"
            reason = "Available issue-session capacity is exhausted."
        else:
            decision = "start"
            reason = (
                "Start the independently valuable lane while its minor dependency remains in flight."
                if issue["minor_dependency"]
                else "Start the ready independently valuable lane."
            )
            remaining -= 1
            occupied.update(issue["overlap_keys"])
        decisions.append(
            {
                "issue_number": issue["issue_number"],
                "decision": decision,
                "reason": reason,
            }
        )
    return decisions


def set_inventory(
    register: dict[str, Any],
    *,
    complete: bool,
    limitation: str,
    rotation_offset: int,
) -> None:
    validate_register(register)
    if not isinstance(complete, bool):
        raise OrchestrationStateError("inventory.complete must be boolean")
    if not isinstance(limitation, str) or len(limitation) > 240:
        raise OrchestrationStateError(
            "inventory.limitation must be text of at most 240 characters"
        )
    if SECRET_VALUE.search(limitation):
        raise OrchestrationStateError(
            "inventory.limitation contains secret-shaped text"
        )
    if isinstance(rotation_offset, bool) or rotation_offset < 0:
        raise OrchestrationStateError(
            "inventory.rotation_offset must be a non-negative integer"
        )
    register["inventory"] = {
        "complete": complete,
        "limitation": limitation,
        "rotation_offset": rotation_offset,
    }
    register["updated_at"] = now_utc()
    validate_register(register)


def set_archive_state(
    register: dict[str, Any],
    *,
    thread_id: str,
    archive_state: str,
) -> dict[str, Any]:
    validate_register(register)
    task = resolve_task(register, thread_id)
    if archive_state == "archive_intent":
        if not archive_eligible(task):
            raise OrchestrationStateError(
                "task is not eligible for archive intent"
            )
        task["archive_state"] = "archive_intent"
        task["closeout_result"] = "reconciled"
    elif archive_state == "archived":
        if task["archive_state"] != "archive_intent":
            raise OrchestrationStateError(
                "archive result requires a recorded archive intent"
            )
        task["archive_state"] = "archived"
        task["closeout_result"] = "archived"
        task["status"] = "archived_known"
    elif archive_state == "unarchived":
        if task["archive_state"] != "archived":
            raise OrchestrationStateError(
                "unarchive result requires a recorded archived state"
            )
        task["archive_state"] = "unarchived"
        task["closeout_result"] = "recovered"
        task["status"] = "completed"
    else:
        raise OrchestrationStateError("archive state is unsupported")
    task["last_action_at"] = now_utc()
    register["updated_at"] = now_utc()
    validate_register(register)
    return task


def wait_batches(
    tasks: Iterable[dict[str, Any]],
    *,
    rotation_offset: int = 0,
    batch_size: int = 8,
) -> list[list[dict[str, str]]]:
    if batch_size < 1 or batch_size > 8:
        raise OrchestrationStateError("wait batch size must be between 1 and 8")
    candidates = sorted(
        (
            task
            for task in tasks
            if task["status"] in {"active", "waiting", "needs_attention"}
            and task["archive_state"] == "unarchived"
        ),
        key=lambda item: item["thread_id"],
    )
    if candidates:
        offset = rotation_offset % len(candidates)
        candidates = candidates[offset:] + candidates[:offset]
    targets = [
        {
            **{"threadId": task["thread_id"]},
            **({"hostId": task["host_id"]} if task["host_id"] else {}),
            **({"afterCursor": task["cursor"]} if task["cursor"] else {}),
        }
        for task in candidates
    ]
    return [
        targets[index : index + batch_size]
        for index in range(0, len(targets), batch_size)
    ]


def resolve_task(register: dict[str, Any], query: str) -> dict[str, Any]:
    require_text(query, "query")
    exact_id = [task for task in register["tasks"] if task["thread_id"] == query]
    if exact_id:
        return exact_id[0]
    matches = [
        task
        for task in register["tasks"]
        if task["title"].casefold() == query.casefold()
    ]
    if len(matches) != 1:
        raise OrchestrationStateError(
            "task recovery query is missing or ambiguous; use an exact task ID"
        )
    return matches[0]


def summarize(register: dict[str, Any]) -> str:
    validate_register(register)
    counts = {
        status: sum(task["status"] == status for task in register["tasks"])
        for status in sorted(TASK_STATUSES)
    }
    lines = [
        "# Agent Orchestration Register",
        "",
        f"- Project: `{register['project_id']}`",
        f"- Orchestrator: `{register['orchestrator_id']}`",
        f"- Goal: `{register['goal']['state']}`",
        f"- Inventory complete: `{str(register['inventory']['complete']).lower()}`",
        f"- Managed tasks: {len(register['tasks'])}",
        "- Issue sessions: "
        + str(sum(task["run_mode"] == "issue_session" for task in register["tasks"])),
        "- Statuses: "
        + ", ".join(f"{name}={count}" for name, count in counts.items() if count),
        f"- Archive eligible: {sum(archive_eligible(task) for task in register['tasks'])}",
    ]
    if register["inventory"]["limitation"]:
        lines.append(f"- Limitation: {register['inventory']['limitation']}")
    return "\n".join(lines) + "\n"


def parse_root(value: str | None) -> Path | None:
    return Path(value).expanduser() if value else None


def selected_path(args: argparse.Namespace) -> Path:
    return register_path(
        args.project_id,
        args.orchestrator_id,
        root=parse_root(args.state_root),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("state-dir")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=Path)

    for command in (
        "init",
        "goal",
        "inventory",
        "upsert",
        "archive",
        "cleanup",
        "list",
        "resolve",
        "summary",
    ):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--project-id", required=True)
        command_parser.add_argument("--orchestrator-id", required=True)
        command_parser.add_argument("--state-root")
        if command == "goal":
            command_parser.add_argument("--state", choices=sorted(GOAL_STATES), required=True)
            command_parser.add_argument("--checked-at")
        elif command == "inventory":
            command_parser.add_argument(
                "--complete",
                action=argparse.BooleanOptionalAction,
                required=True,
            )
            command_parser.add_argument("--limitation", default="")
            command_parser.add_argument("--rotation-offset", type=int, default=0)
        elif command == "upsert":
            command_parser.add_argument("--thread-id", required=True)
            command_parser.add_argument("--host-id")
            command_parser.add_argument("--title", required=True)
            command_parser.add_argument("--status", choices=sorted(TASK_STATUSES), required=True)
            command_parser.add_argument("--issue-number", type=int)
            command_parser.add_argument("--pr-number", type=int)
            command_parser.add_argument(
                "--run-mode",
                choices=sorted(RUN_MODES),
                default="observed_peer",
            )
            command_parser.add_argument("--worktree-path")
            command_parser.add_argument("--branch-name")
            command_parser.add_argument("--base-revision")
            command_parser.add_argument("--cursor")
            command_parser.add_argument("--observed-at")
            command_parser.add_argument("--terminal-verified", action="store_true")
            command_parser.add_argument("--final-read", action="store_true")
            command_parser.add_argument("--reconciled", action="store_true")
            command_parser.add_argument("--needed-for-dependency", action="store_true")
            command_parser.add_argument("--blocker-category", choices=sorted(
                value for value in BLOCKER_CATEGORIES if value is not None
            ))
        elif command == "archive":
            command_parser.add_argument("--thread-id", required=True)
            command_parser.add_argument(
                "--state",
                choices=("archive_intent", "archived", "unarchived"),
                required=True,
            )
        elif command == "cleanup":
            command_parser.add_argument("--thread-id", required=True)
            command_parser.add_argument(
                "--state",
                choices=("cleanup_intent", "cleaned", "preserved"),
                required=True,
            )
            command_parser.add_argument("--worktree-clean", action="store_true")
            command_parser.add_argument(
                "--branch-evidence-preserved", action="store_true"
            )
            command_parser.add_argument("--task-owned", action="store_true")
        elif command == "resolve":
            command_parser.add_argument("--query", required=True)

    title_parser = subparsers.add_parser("format-title")
    title_parser.add_argument("--status", required=True)
    title_parser.add_argument("--issue-number", type=int)
    title_parser.add_argument("--pr-number", type=int)
    title_parser.add_argument("--fallback-kind", choices=("Project", "Task"))
    title_parser.add_argument("--fallback-text")

    triage_parser = subparsers.add_parser("triage")
    triage_parser.add_argument("--input", type=Path, required=True)
    triage_parser.add_argument("--capacity", type=int, required=True)
    triage_parser.add_argument("--active-overlap-key", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "state-dir":
            print(state_directory())
            return 0
        if args.command == "validate":
            load_register(args.path)
            print(json.dumps({"status": "valid", "path": str(args.path)}))
            return 0
        if args.command == "format-title":
            print(
                format_title(
                    status=args.status,
                    issue_number=args.issue_number,
                    pr_number=args.pr_number,
                    fallback_kind=args.fallback_kind,
                    fallback_text=args.fallback_text,
                )
            )
            return 0
        if args.command == "triage":
            try:
                issues = json.loads(args.input.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                raise OrchestrationStateError(
                    f"cannot read triage input safely: {error}"
                ) from error
            if not isinstance(issues, list):
                raise OrchestrationStateError("triage input must contain a list")
            print(
                json.dumps(
                    triage_issue_candidates(
                        issues,
                        capacity=args.capacity,
                        active_overlap_keys=args.active_overlap_key,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        path = selected_path(args)
        if args.command == "init":
            register = new_register(args.project_id, args.orchestrator_id)
            write_register(path, register)
            print(json.dumps({"status": "initialized", "path": str(path)}))
            return 0

        register = load_register(path)
        if args.command == "goal":
            checked_at = args.checked_at or now_utc()
            parse_time(checked_at, "checked_at")
            register["goal"] = {"state": args.state, "last_checked_at": checked_at}
            register["updated_at"] = now_utc()
            write_register(path, register)
            print(json.dumps(register["goal"], sort_keys=True))
        elif args.command == "inventory":
            set_inventory(
                register,
                complete=args.complete,
                limitation=args.limitation,
                rotation_offset=args.rotation_offset,
            )
            write_register(path, register)
            print(json.dumps(register["inventory"], sort_keys=True))
        elif args.command == "upsert":
            task = default_task(
                thread_id=args.thread_id,
                project_id=args.project_id,
                status=args.status,
                observed_at=args.observed_at or now_utc(),
                host_id=args.host_id,
                title=args.title,
                issue_number=args.issue_number,
                pr_number=args.pr_number,
                run_mode=args.run_mode,
                worktree_path=args.worktree_path,
                branch_name=args.branch_name,
                base_revision=args.base_revision,
            )
            task["cursor"] = args.cursor
            task["terminal_verified"] = args.terminal_verified
            task["final_read"] = args.final_read
            task["reconciled"] = args.reconciled
            task["needed_for_dependency"] = args.needed_for_dependency
            task["blocker_category"] = args.blocker_category
            if archive_eligible(task):
                task["closeout_result"] = "reconciled"
            upsert_task(register, task)
            write_register(path, register)
            print(json.dumps(task, sort_keys=True))
        elif args.command == "archive":
            task = set_archive_state(
                register,
                thread_id=args.thread_id,
                archive_state=args.state,
            )
            write_register(path, register)
            print(json.dumps(task, sort_keys=True))
        elif args.command == "cleanup":
            task = set_cleanup_state(
                register,
                thread_id=args.thread_id,
                cleanup_state=args.state,
                worktree_clean=args.worktree_clean,
                branch_evidence_preserved=args.branch_evidence_preserved,
                task_owned=args.task_owned,
            )
            write_register(path, register)
            print(json.dumps(task, sort_keys=True))
        elif args.command == "list":
            print(json.dumps(register["tasks"], indent=2, sort_keys=True))
        elif args.command == "resolve":
            print(json.dumps(resolve_task(register, args.query), indent=2, sort_keys=True))
        elif args.command == "summary":
            print(summarize(register), end="")
        return 0
    except OrchestrationStateError as error:
        print(f"orchestration state error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
