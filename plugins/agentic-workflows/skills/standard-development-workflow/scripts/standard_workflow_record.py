#!/usr/bin/env python3
"""Validate and summarize Standard Development Workflow records."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RECORD_KINDS = {"repository_profile", "task_run"}
APPLICABILITY_STATES = {"required", "optional", "not_applicable", "blocked"}
STEP_STATES = {
    "pending",
    "running",
    "passed",
    "failed",
    "skipped",
    "blocked",
}
OPERATION_STATES = {
    "planned",
    "running",
    "stalled",
    "failed",
    "cancelled",
    "completed_unverified",
    "verified",
}
FAILURE_CLASSES = {
    "product",
    "harness",
    "fixture_state",
    "environment",
    "platform_tooling",
    "external_dependency",
    "expected_behavior",
    "nondeterministic",
    "unknown",
}
CHANNEL_DECISIONS = {"primary", "equivalent", "partial", "diagnostic"}
RESOURCE_OWNERSHIP = {"task", "repository_shared", "host_shared", "external"}
COST_ORDER = {
    "integrity": 0,
    "static": 1,
    "focused": 2,
    "build": 3,
    "stateful": 4,
    "browser_manual": 5,
    "external": 6,
}
DELIVERABLE_STATES = {"required", "excluded", "unknown"}
DELIVERABLE_KINDS = {
    "outcome", "issue", "issue_first", "pull_request", "review", "merge",
    "deployment", "local_artifact", "explanation", "verification", "decision",
}
EXTERNAL_STATES = {"pending", "observed", "saved", "read_back", "flow_verified", "blocked"}
SOURCE_FAILURES = {
    "authentication_redirect", "permission", "stale_session", "unavailable_connector",
    "network", "unsupported_control", "other",
}
DIGEST_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
SECRET_KEYS = {
    "api_key",
    "api_secret",
    "credential",
    "credential_value",
    "password",
    "secret",
    "token",
    "value",
}
SECRET_PATTERNS = (
    re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:sk|rk)-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
    re.compile(r"https?://[^/\s:@]+:[^@\s/]+@", re.IGNORECASE),
)


class RecordError(ValueError):
    """A user-facing workflow-record validation failure."""


def canonical_bytes(value: Any) -> bytes:
    """Return canonical UTF-8 JSON with stable ordering and one final newline."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def content_digest(value: Any) -> str:
    """Return the SHA-256 identity of canonical JSON."""

    return f"sha256:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def file_digest(path: Path) -> str:
    """Return the SHA-256 digest for one regular file."""

    if not path.is_file() or path.is_symlink():
        raise RecordError(f"evidence path is not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def load_record(path: Path) -> dict[str, Any]:
    """Load one JSON object."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RecordError(f"{path} is not valid UTF-8 JSON: {error}") from error
    if not isinstance(payload, dict):
        raise RecordError("workflow record must be a JSON object")
    return payload


def require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RecordError(f"{path} must be an object")
    return value


def require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise RecordError(f"{path} must be an array")
    return value


def require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordError(f"{path} must be non-empty text")
    return value


def require_choice(value: Any, choices: set[str], path: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise RecordError(f"{path} has unsupported value")
    return value


def require_keys(payload: dict[str, Any], keys: set[str], path: str) -> None:
    missing = sorted(keys - payload.keys())
    if missing:
        raise RecordError(f"{path} is missing required keys: {', '.join(missing)}")


def reconcile_delivery_contract(contract_value: Any, update_value: Any) -> dict[str, Any]:
    """Apply one explicit correction without discarding unrelated requirements."""

    contract = json.loads(json.dumps(require_object(contract_value, "delivery_contract")))
    update = require_object(update_value, "contract update")
    require_keys(update, {"id", "kind", "target", "proof_source", "state", "authority", "source_ref"}, "contract update")
    requirement_id = require_text(update["id"], "contract update.id")
    require_choice(update["kind"], DELIVERABLE_KINDS, "contract update.kind")
    require_choice(update["state"], DELIVERABLE_STATES, "contract update.state")
    require_choice(update["authority"], {"explicit", "inferred"}, "contract update.authority")
    require_text(update["source_ref"], "contract update.source_ref")
    require_text(update["target"], "contract update.target")
    require_text(update["proof_source"], "contract update.proof_source")
    requirements = require_list(contract.get("requirements"), "delivery_contract.requirements")
    changes = require_list(contract.get("changes"), "delivery_contract.changes")
    existing = next((item for item in requirements if item.get("id") == requirement_id), None)
    if existing and existing["authority"] == "explicit" and update["authority"] == "inferred":
        raise RecordError("an inferred update cannot override an explicit user requirement")
    if existing and existing["kind"] != update["kind"]:
        raise RecordError("contract update cannot change a requirement kind")
    previous_state = existing["state"] if existing else None
    previous_target = existing["target"] if existing else None
    if (existing and previous_state == update["state"]
            and existing["authority"] == update["authority"]
            and previous_target == update["target"]
            and existing["proof_source"] == update["proof_source"]):
        return contract
    item = existing if existing else {"id": requirement_id, "kind": update["kind"]}
    item.update({
        "state": update["state"], "authority": update["authority"],
        "target": update["target"], "proof_source": update["proof_source"],
        "source_ref": update["source_ref"],
        "status": "not_applicable" if update["state"] == "excluded" else "pending",
        "evidence_ref": "",
    })
    if existing is None:
        requirements.append(item)
    changes.append({
        "sequence": len(changes) + 1, "id": requirement_id,
        "previous_state": previous_state, "new_state": update["state"],
        "previous_target": previous_target, "new_target": update["target"],
        "authority": update["authority"], "source_ref": update["source_ref"],
    })
    return contract


def validate_delivery_contract(value: Any, *, require_final: bool) -> None:
    contract = require_object(value, "delivery_contract")
    require_keys(contract, {"requirements", "changes"}, "delivery_contract")
    requirements: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(require_list(contract["requirements"], "delivery_contract.requirements")):
        item = require_object(raw, f"delivery_contract.requirements[{index}]")
        require_keys(item, {"id", "kind", "target", "proof_source", "state", "authority", "source_ref", "status", "evidence_ref"}, "delivery requirement")
        item_id = require_text(item["id"], "delivery requirement.id")
        if item_id in requirements:
            raise RecordError(f"duplicate delivery requirement: {item_id}")
        require_choice(item["kind"], DELIVERABLE_KINDS, f"delivery requirement {item_id}.kind")
        require_choice(item["state"], DELIVERABLE_STATES, f"delivery requirement {item_id}.state")
        require_choice(item["authority"], {"explicit", "inferred"}, f"delivery requirement {item_id}.authority")
        require_text(item["source_ref"], f"delivery requirement {item_id}.source_ref")
        require_text(item["target"], f"delivery requirement {item_id}.target")
        require_text(item["proof_source"], f"delivery requirement {item_id}.proof_source")
        require_choice(item["status"], {"pending", "complete", "blocked", "not_applicable"}, f"delivery requirement {item_id}.status")
        if item["state"] == "excluded" and item["status"] != "not_applicable":
            raise RecordError(f"excluded delivery requirement {item_id} cannot be performed")
        if item["status"] == "complete":
            require_text(item["evidence_ref"], f"delivery requirement {item_id}.evidence_ref")
        if require_final and item["state"] == "required" and item["status"] != "complete":
            raise RecordError(f"required delivery requirement {item_id} is incomplete")
        requirements[item_id] = item
    if require_final and not requirements:
        raise RecordError("final delivery contract has no outcome or deliverables")
    replayed: dict[str, tuple[str, str, str]] = {}
    for sequence, raw in enumerate(require_list(contract["changes"], "delivery_contract.changes"), 1):
        change = require_object(raw, f"delivery_contract.changes[{sequence - 1}]")
        require_keys(change, {"sequence", "id", "previous_state", "new_state", "previous_target", "new_target", "authority", "source_ref"}, "delivery change")
        change_id = require_text(change["id"], "delivery change.id")
        if change["sequence"] != sequence or change_id not in requirements:
            raise RecordError("delivery changes have invalid sequence or requirement id")
        require_choice(change["new_state"], DELIVERABLE_STATES, "delivery change.new_state")
        require_choice(change["authority"], {"explicit", "inferred"}, "delivery change.authority")
        require_text(change["source_ref"], "delivery change.source_ref")
        previous = replayed.get(change["id"])
        if change["previous_state"] != (previous[0] if previous else None):
            raise RecordError("delivery changes do not replay from the prior state")
        if change["previous_target"] != (previous[2] if previous else None):
            raise RecordError("delivery changes do not replay from the prior target")
        if previous and previous[1] == "explicit" and change["authority"] == "inferred":
            raise RecordError("delivery changes downgrade an explicit user requirement")
        require_text(change["new_target"], "delivery change.new_target")
        replayed[change["id"]] = (change["new_state"], change["authority"], change["new_target"])
    latest = {change["id"]: change for change in contract["changes"]}
    for item_id, change in latest.items():
        if (requirements[item_id]["state"] != change["new_state"]
                or requirements[item_id]["authority"] != change["authority"]
                or requirements[item_id]["target"] != change["new_target"]):
            raise RecordError(f"delivery requirement {item_id} disagrees with its latest change")
    if require_final and any(item["state"] == "unknown" for item in requirements.values()):
        raise RecordError("unresolved delivery requirements prevent final evidence")


def validate_plan_comment(
    plan_value: Any,
    *,
    issue_url: str,
    source_revision: str,
    task_status: str,
) -> None:
    plan = require_object(plan_value, "task.plan")
    require_keys(
        plan,
        {
            "comment_id",
            "comment_url",
            "marker",
            "pinned",
            "pinned_at",
            "canonical_comment_count",
            "last_reconciled_at",
            "reconciled_revision",
            "state",
            "findings_count",
        },
        "task.plan",
    )
    if isinstance(plan["comment_id"], bool) or not isinstance(plan["comment_id"], int):
        raise RecordError("task.plan.comment_id must be a positive integer")
    if plan["comment_id"] < 1:
        raise RecordError("task.plan.comment_id must be a positive integer")
    comment_url = require_text(plan["comment_url"], "task.plan.comment_url")
    expected_url = (
        f"{issue_url.rstrip('/')}#issuecomment-{plan['comment_id']}"
    )
    if comment_url != expected_url:
        raise RecordError("task.plan.comment_url does not belong to the task issue")
    if plan["marker"] != "<!-- standard-development-plan -->":
        raise RecordError("task.plan.marker is not the canonical plan marker")
    if plan["pinned"] is not True:
        raise RecordError("task.plan must be pinned")
    require_text(plan["pinned_at"], "task.plan.pinned_at")
    if plan["canonical_comment_count"] != 1:
        raise RecordError("task.plan requires exactly one canonical plan comment")
    require_text(plan["last_reconciled_at"], "task.plan.last_reconciled_at")
    if plan["reconciled_revision"] != source_revision:
        raise RecordError("task.plan is stale for the current source revision")
    if plan["state"] not in {
        "awaiting_approval",
        "approved",
        "reapproval_required",
        "implemented",
    }:
        raise RecordError("task.plan.state is unsupported")
    if (
        isinstance(plan["findings_count"], bool)
        or not isinstance(plan["findings_count"], int)
        or plan["findings_count"] < 0
    ):
        raise RecordError("task.plan.findings_count must be a non-negative integer")
    if task_status not in {"planned", "blocked"} and plan["state"] not in {
        "approved",
        "implemented",
    }:
        raise RecordError("execution requires an approved canonical plan comment")


def reject_secrets(value: Any, path: str = "$") -> None:
    """Reject credential-bearing fields and common secret-shaped values."""

    if isinstance(value, dict):
        for key, nested in value.items():
            if key.lower() in SECRET_KEYS:
                raise RecordError(f"{path}.{key} is a prohibited secret-bearing field")
            reject_secrets(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_secrets(nested, f"{path}[{index}]")
    elif isinstance(value, str):
        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                raise RecordError(f"{path} appears to contain a secret value")


def validate_evidence_sources(
    sources: Any,
    *,
    source_root: Path | None,
) -> None:
    identifiers: set[str] = set()
    for index, source_value in enumerate(require_list(sources, "provenance.sources")):
        source = require_object(source_value, f"provenance.sources[{index}]")
        require_keys(
            source,
            {"id", "kind", "location", "digest", "freshness", "checked_at"},
            f"provenance.sources[{index}]",
        )
        source_id = require_text(source["id"], f"provenance.sources[{index}].id")
        if source_id in identifiers:
            raise RecordError(f"duplicate provenance source id: {source_id}")
        identifiers.add(source_id)
        digest = require_text(
            source["digest"], f"provenance.sources[{index}].digest"
        )
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise RecordError(
                f"provenance.sources[{index}].digest must be a SHA-256 identity"
            )
        freshness = source["freshness"]
        if freshness not in {"revision_bound", "transient"}:
            raise RecordError(
                f"provenance.sources[{index}].freshness is not supported"
            )
        if freshness == "transient":
            require_text(
                source.get("expires_at"),
                f"provenance.sources[{index}].expires_at",
            )
        if source_root is not None and source["kind"] == "repository_file":
            location = Path(
                require_text(
                    source["location"], f"provenance.sources[{index}].location"
                )
            )
            if location.is_absolute() or ".." in location.parts:
                raise RecordError(
                    f"provenance.sources[{index}].location must be repository-relative"
                )
            resolved_root = source_root.resolve()
            resolved_source = (resolved_root / location).resolve()
            if not resolved_source.is_relative_to(resolved_root):
                raise RecordError(
                    f"provenance source escapes the repository: {source['location']}"
                )
            if file_digest(resolved_source) != digest:
                raise RecordError(
                    f"provenance source drifted: {source['location']}"
                )


def validate_applicability(value: Any) -> None:
    capabilities = require_object(value, "applicability")
    if not capabilities:
        raise RecordError("applicability must contain at least one capability")
    for name, capability_value in capabilities.items():
        capability = require_object(capability_value, f"applicability.{name}")
        require_keys(capability, {"state", "reason", "evidence_refs"}, f"applicability.{name}")
        if capability["state"] not in APPLICABILITY_STATES:
            raise RecordError(f"applicability.{name}.state is not supported")
        require_text(capability["reason"], f"applicability.{name}.reason")
        refs = require_list(
            capability["evidence_refs"], f"applicability.{name}.evidence_refs"
        )
        if capability["state"] in {"required", "optional"} and not refs:
            raise RecordError(
                f"applicability.{name} requires repository or user evidence"
            )


def validate_scope(scope_value: Any) -> None:
    scope = require_object(scope_value, "scope")
    require_keys(
        scope,
        {
            "direct",
            "enabling",
            "follow_up",
            "prohibited",
            "change_envelope",
            "expansion",
        },
        "scope",
    )
    for key in (
        "direct",
        "enabling",
        "follow_up",
        "prohibited",
        "change_envelope",
    ):
        require_list(scope[key], f"scope.{key}")
    for index, enabling_value in enumerate(scope["enabling"]):
        enabling = require_object(enabling_value, f"scope.enabling[{index}]")
        require_keys(
            enabling,
            {"change", "inseparability_evidence"},
            f"scope.enabling[{index}]",
        )
        require_text(
            enabling["inseparability_evidence"],
            f"scope.enabling[{index}].inseparability_evidence",
        )
    expansion = require_object(scope["expansion"], "scope.expansion")
    require_keys(expansion, {"triggered", "reasons", "approval_state"}, "scope.expansion")
    require_list(expansion["reasons"], "scope.expansion.reasons")
    if expansion["triggered"] and expansion["approval_state"] != "revised_approved":
        raise RecordError(
            "material scope expansion blocks implementation until revised approval"
        )


def validate_resources(
    resources_value: Any,
    reclamation_approval_ids: set[str],
    *,
    task_status: str,
) -> None:
    for index, resource_value in enumerate(require_list(resources_value, "resources")):
        resource = require_object(resource_value, f"resources[{index}]")
        require_keys(
            resource,
            {
                "id",
                "kind",
                "ownership",
                "capacity",
                "cleanup",
                "recovery",
            },
            f"resources[{index}]",
        )
        if resource["ownership"] not in RESOURCE_OWNERSHIP:
            raise RecordError(f"resources[{index}].ownership is not supported")
        if resource["capacity"] not in {
            "sufficient",
            "insufficient",
            "unknown",
            "not_applicable",
        }:
            raise RecordError(f"resources[{index}].capacity is not supported")
        if (
            resource["capacity"] in {"insufficient", "unknown"}
            and task_status not in {"planned", "blocked"}
        ):
            raise RecordError(
                f"resources[{index}] capacity blocks expensive work"
            )
        require_text(resource["recovery"], f"resources[{index}].recovery")
        cleanup = require_object(resource["cleanup"], f"resources[{index}].cleanup")
        require_keys(cleanup, {"allowed", "exact_target", "approval_ref"}, f"resources[{index}].cleanup")
        if cleanup["allowed"] and not cleanup["exact_target"]:
            raise RecordError(f"resources[{index}] cleanup requires an exact target")
        if resource["ownership"] != "task" and cleanup["allowed"]:
            approval_ref = cleanup["approval_ref"]
            if approval_ref not in reclamation_approval_ids:
                raise RecordError(
                    f"resources[{index}] shared cleanup requires explicit approval"
                )


def validate_steps(validation_value: Any) -> dict[str, dict[str, Any]]:
    validation = require_object(validation_value, "validation")
    require_keys(validation, {"source_revision", "steps"}, "validation")
    require_text(validation["source_revision"], "validation.source_revision")
    steps: dict[str, dict[str, Any]] = {}
    ordered_steps = require_list(validation["steps"], "validation.steps")
    previous_cost = -1
    for index, step_value in enumerate(ordered_steps):
        step = require_object(step_value, f"validation.steps[{index}]")
        require_keys(
            step,
            {
                "id",
                "command_or_boundary",
                "evidence_ref",
                "prerequisites",
                "cost",
                "completion_required",
                "state",
                "skip_reason",
            },
            f"validation.steps[{index}]",
        )
        step_id = require_text(step["id"], f"validation.steps[{index}].id")
        if step_id in steps:
            raise RecordError(f"duplicate validation step id: {step_id}")
        if step["state"] not in STEP_STATES:
            raise RecordError(f"validation step {step_id} has unsupported state")
        if step["cost"] not in COST_ORDER:
            raise RecordError(f"validation step {step_id} has unsupported cost")
        if COST_ORDER[step["cost"]] < previous_cost:
            raise RecordError("validation ladder is not ordered cheap-first")
        previous_cost = COST_ORDER[step["cost"]]
        if step["state"] == "skipped" and not step["skip_reason"]:
            raise RecordError(f"validation step {step_id} requires a skip reason")
        steps[step_id] = step
    for step_id, step in steps.items():
        prerequisites = require_list(
            step["prerequisites"], f"validation step {step_id}.prerequisites"
        )
        for prerequisite in prerequisites:
            if prerequisite not in steps:
                raise RecordError(
                    f"validation step {step_id} has unknown prerequisite {prerequisite}"
                )
            if (
                steps[prerequisite]["state"] in {"failed", "blocked"}
                and step["state"] in {"running", "passed"}
            ):
                raise RecordError(
                    f"validation step {step_id} ran after failed prerequisite {prerequisite}"
                )
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visiting:
            raise RecordError("validation prerequisites contain a cycle")
        if step_id in visited:
            return
        visiting.add(step_id)
        for prerequisite in steps[step_id]["prerequisites"]:
            visit(prerequisite)
        visiting.remove(step_id)
        visited.add(step_id)

    for step_id in steps:
        visit(step_id)
    return steps


def validate_failures(failures_value: Any, steps: dict[str, dict[str, Any]]) -> None:
    for index, failure_value in enumerate(require_list(failures_value, "failures")):
        failure = require_object(failure_value, f"failures[{index}]")
        require_keys(
            failure,
            {
                "id",
                "step_ref",
                "first_evidence",
                "reproduction",
                "classification",
                "classification_evidence",
                "remedy",
                "rerun_steps",
                "accepted",
            },
            f"failures[{index}]",
        )
        if failure["step_ref"] not in steps:
            raise RecordError(f"failures[{index}] references an unknown step")
        if failure["classification"] not in FAILURE_CLASSES:
            raise RecordError(f"failures[{index}] has unsupported classification")
        require_text(failure["first_evidence"], f"failures[{index}].first_evidence")
        require_text(failure["reproduction"], f"failures[{index}].reproduction")
        if (
            steps[failure["step_ref"]]["completion_required"]
            and failure["classification"] == "unknown"
            and not failure["accepted"]
        ):
            raise RecordError("unknown required failure blocks the review gate")


def validate_sandboxes(sandboxes_value: Any) -> None:
    sandboxes = require_list(sandboxes_value, "sandboxes")
    for index, sandbox_value in enumerate(sandboxes):
        sandbox = require_object(sandbox_value, f"sandboxes[{index}]")
        require_keys(
            sandbox,
            {
                "id",
                "suite",
                "mutable_resources",
                "readiness",
                "cleanup_targets",
                "safe_sharing_evidence",
            },
            f"sandboxes[{index}]",
        )
    for left_index, left_value in enumerate(sandboxes):
        left = require_object(left_value, f"sandboxes[{left_index}]")
        left_resources = set(require_list(left["mutable_resources"], "mutable_resources"))
        for right_value in sandboxes[left_index + 1 :]:
            right = require_object(right_value, "sandbox")
            overlap = left_resources & set(
                require_list(right["mutable_resources"], "mutable_resources")
            )
            if overlap and not (
                left["safe_sharing_evidence"] and right["safe_sharing_evidence"]
            ):
                raise RecordError(
                    "validation sandboxes share mutable state without safety evidence"
                )


def validate_artifacts(artifacts_value: Any, source_revision: str) -> set[str]:
    artifact_ids: set[str] = set()
    for index, artifact_value in enumerate(require_list(artifacts_value, "artifacts")):
        artifact = require_object(artifact_value, f"artifacts[{index}]")
        require_keys(
            artifact,
            {
                "id",
                "digest",
                "source_revision",
                "build_inputs_digest",
                "command_ref",
                "platform",
                "immutable",
                "verified",
            },
            f"artifacts[{index}]",
        )
        artifact_id = require_text(artifact["id"], f"artifacts[{index}].id")
        if artifact_id in artifact_ids:
            raise RecordError(f"duplicate artifact id: {artifact_id}")
        artifact_ids.add(artifact_id)
        if not artifact["immutable"]:
            raise RecordError(f"artifact {artifact_id} is mutable and cannot be reused")
        if not artifact["verified"]:
            raise RecordError(f"artifact {artifact_id} output is not verified")
        if artifact["source_revision"] != source_revision:
            raise RecordError(f"artifact {artifact_id} has stale source identity")
        for key in ("digest", "build_inputs_digest"):
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(artifact[key])):
                raise RecordError(f"artifact {artifact_id} requires immutable {key}")
    return artifact_ids


def validate_operations(operations_value: Any, source_revision: str) -> None:
    mutation_keys: set[str] = set()
    for index, operation_value in enumerate(require_list(operations_value, "operations")):
        operation = require_object(operation_value, f"operations[{index}]")
        require_keys(
            operation,
            {
                "id",
                "purpose",
                "command_or_tool",
                "evidence_ref",
                "working_directory",
                "source_revision",
                "inputs_digest",
                "expected_outputs",
                "ownership",
                "budgets",
                "liveness",
                "cancellation",
                "resumability",
                "state",
                "checkpoint",
                "mutating",
                "mutation_key",
                "retry_count",
                "max_retries",
                "retry_reason",
            },
            f"operations[{index}]",
        )
        operation_id = require_text(operation["id"], f"operations[{index}].id")
        for key in (
            "purpose",
            "command_or_tool",
            "evidence_ref",
            "working_directory",
            "liveness",
            "cancellation",
            "resumability",
        ):
            require_text(operation[key], f"operation {operation_id}.{key}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(operation["inputs_digest"])):
            raise RecordError(f"operation {operation_id} inputs_digest is not immutable")
        require_list(operation["expected_outputs"], f"operation {operation_id}.expected_outputs")
        if operation["state"] not in OPERATION_STATES:
            raise RecordError(f"operation {operation_id} has unsupported state")
        if operation["source_revision"] != source_revision:
            raise RecordError(f"operation {operation_id} checkpoint is stale")
        budgets = require_object(operation["budgets"], f"operation {operation_id}.budgets")
        require_keys(budgets, {"soft_seconds", "hard_seconds"}, f"operation {operation_id}.budgets")
        if budgets["soft_seconds"] <= 0 or budgets["hard_seconds"] < budgets["soft_seconds"]:
            raise RecordError(f"operation {operation_id} has invalid time budgets")
        if operation["retry_count"] > operation["max_retries"]:
            raise RecordError(f"operation {operation_id} exceeded its retry budget")
        if operation["retry_count"] > 0:
            require_text(
                operation["retry_reason"],
                f"operation {operation_id}.retry_reason",
            )
        if operation["state"] != "planned" and not operation["checkpoint"]:
            raise RecordError(f"operation {operation_id} requires a durable checkpoint")
        if operation["mutating"]:
            mutation_key = require_text(
                operation["mutation_key"], f"operation {operation_id}.mutation_key"
            )
            if mutation_key in mutation_keys and operation["state"] in {
                "running",
                "completed_unverified",
                "verified",
            }:
                raise RecordError("duplicate mutating operation identity")
            mutation_keys.add(mutation_key)


def validate_verification(
    verification_value: Any,
    *,
    artifact_ids: set[str],
    fallback_approval_ids: set[str],
) -> set[str]:
    verification = require_object(verification_value, "verification")
    require_keys(verification, {"claims"}, "verification")
    satisfied_claims: set[str] = set()
    for index, claim_value in enumerate(require_list(verification["claims"], "verification.claims")):
        claim = require_object(claim_value, f"verification.claims[{index}]")
        require_keys(
            claim,
            {
                "id",
                "claim",
                "primary_channel",
                "availability",
                "selected_channel",
                "decision",
                "equivalence_justification",
                "approval_owner",
                "approval_ref",
                "satisfied",
                "artifact_refs",
            },
            f"verification.claims[{index}]",
        )
        claim_id = require_text(claim["id"], f"verification.claims[{index}].id")
        if claim["decision"] not in CHANNEL_DECISIONS:
            raise RecordError(f"verification claim {claim_id} has unsupported decision")
        if claim["decision"] == "equivalent":
            require_text(
                claim["equivalence_justification"],
                f"verification claim {claim_id}.equivalence_justification",
            )
            require_text(
                claim["approval_owner"],
                f"verification claim {claim_id}.approval_owner",
            )
            if claim["approval_ref"] not in fallback_approval_ids:
                raise RecordError(
                    f"verification claim {claim_id} lacks approved fallback authority"
                )
        if claim["decision"] in {"partial", "diagnostic"} and claim["satisfied"]:
            raise RecordError(
                f"verification claim {claim_id} cannot be satisfied by a weaker channel"
            )
        if (
            claim["availability"] == "unavailable"
            and claim["decision"] == "primary"
            and claim["satisfied"]
        ):
            raise RecordError(
                f"verification claim {claim_id} uses an unavailable primary channel"
            )
        if claim["satisfied"]:
            satisfied_claims.add(claim_id)
        if not set(require_list(claim["artifact_refs"], "artifact_refs")).issubset(
            artifact_ids
        ):
            raise RecordError(
                f"verification claim {claim_id} references an unknown artifact"
            )
    return satisfied_claims


def validate_evidence(
    evidence_value: Any,
    *,
    source_revision: str,
    steps: dict[str, dict[str, Any]],
    artifact_ids: set[str],
    satisfied_claims: set[str],
    require_final: bool,
) -> None:
    evidence = require_object(evidence_value, "evidence")
    require_keys(
        evidence,
        {
            "status",
            "source_revision",
            "tracked_source_clean",
            "artifact_refs",
            "validation_refs",
            "claim_refs",
            "files",
            "limitations",
            "finalized_at",
        },
        "evidence",
    )
    if evidence["status"] not in {"rehearsal", "final"}:
        raise RecordError("evidence.status must be rehearsal or final")
    if require_final and evidence["status"] != "final":
        raise RecordError("rehearsal evidence cannot satisfy the review gate")
    if evidence["status"] != "final":
        return
    if evidence["source_revision"] != source_revision:
        raise RecordError("final evidence has stale source identity")
    if not evidence["tracked_source_clean"]:
        raise RecordError("final evidence requires clean tracked source")
    for step_ref in require_list(evidence["validation_refs"], "evidence.validation_refs"):
        if step_ref not in steps or steps[step_ref]["state"] != "passed":
            raise RecordError(f"final evidence references incomplete validation: {step_ref}")
    required_steps = {
        step_id
        for step_id, step in steps.items()
        if step["completion_required"] and step["state"] != "skipped"
    }
    if not required_steps.issubset(set(evidence["validation_refs"])):
        raise RecordError("final evidence omits a completion-required validation step")
    if not set(evidence["artifact_refs"]).issubset(artifact_ids):
        raise RecordError("final evidence references an unknown artifact")
    if not set(evidence["claim_refs"]).issubset(satisfied_claims):
        raise RecordError("final evidence references an unsatisfied verification claim")
    for index, file_value in enumerate(require_list(evidence["files"], "evidence.files")):
        file_record = require_object(file_value, f"evidence.files[{index}]")
        require_keys(
            file_record,
            {"path", "digest", "channel", "capture_context"},
            f"evidence.files[{index}]",
        )
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", str(file_record["digest"])):
            raise RecordError(f"evidence.files[{index}].digest is not immutable")
    require_text(evidence["finalized_at"], "evidence.finalized_at")


def validate_verification_costs(value: Any) -> dict[str, dict[str, Any]]:
    costs: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(require_list(value, "capabilities.verification_costs")):
        item = require_object(raw, f"capabilities.verification_costs[{index}]")
        require_keys(item, {
            "id", "command", "claim_refs", "required_gate", "setup_seconds",
            "median_seconds", "p95_seconds", "mutable_resources", "reuse_policy",
            "measured_at", "evidence_ref",
        }, "verification cost")
        check_id = require_text(item["id"], "verification cost.id")
        if check_id in costs:
            raise RecordError(f"duplicate verification cost: {check_id}")
        require_text(item["command"], f"verification cost {check_id}.command")
        require_text(item["measured_at"], f"verification cost {check_id}.measured_at")
        require_text(item["evidence_ref"], f"verification cost {check_id}.evidence_ref")
        require_list(item["claim_refs"], f"verification cost {check_id}.claim_refs")
        require_list(item["mutable_resources"], f"verification cost {check_id}.mutable_resources")
        if not isinstance(item["required_gate"], bool):
            raise RecordError(f"verification cost {check_id}.required_gate must be boolean")
        require_choice(item["reuse_policy"], {"immutable", "candidate", "never"}, f"verification cost {check_id}.reuse_policy")
        for field in ("setup_seconds", "median_seconds", "p95_seconds"):
            number = item[field]
            if isinstance(number, bool) or not isinstance(number, (int, float)) or number < 0:
                raise RecordError(f"verification cost {check_id}.{field} must be non-negative")
        if item["p95_seconds"] < item["median_seconds"]:
            raise RecordError(f"verification cost {check_id} has p95 below median")
        costs[check_id] = item
    return costs


def profile_check(value: Any) -> dict[str, Any]:
    """Build one measured cost entry from timestamped setup/run samples."""

    payload = require_object(value, "verification profile input")
    reject_secrets(payload)
    require_keys(payload, {
        "id", "command", "claim_refs", "required_gate", "mutable_resources",
        "reuse_policy", "evidence_ref", "samples",
    }, "verification profile input")
    samples = require_list(payload["samples"], "verification profile input.samples")
    if not samples:
        raise RecordError("verification profile requires measured samples")
    setup: list[float] = []
    duration: list[float] = []
    measured_at = ""
    for index, raw in enumerate(samples):
        sample = require_object(raw, f"verification profile input.samples[{index}]")
        require_keys(sample, {"setup_seconds", "run_seconds", "measured_at"}, "verification sample")
        for field in ("setup_seconds", "run_seconds"):
            number = sample[field]
            if isinstance(number, bool) or not isinstance(number, (int, float)) or number < 0:
                raise RecordError(f"verification sample {index}.{field} must be non-negative")
        setup.append(sample["setup_seconds"])
        duration.append(sample["run_seconds"])
        measured_at = max(measured_at, require_text(sample["measured_at"], f"verification sample {index}.measured_at"))
    ordered = sorted(duration)
    cost = {key: payload[key] for key in (
        "id", "command", "claim_refs", "required_gate", "mutable_resources",
        "reuse_policy", "evidence_ref",
    )}
    cost.update({
        "setup_seconds": statistics.median(setup),
        "median_seconds": statistics.median(duration),
        "p95_seconds": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "measured_at": measured_at,
    })
    validate_verification_costs([cost])
    return cost


def validate_verification_runs(
    value: Any, *, source_revision: str, costs: dict[str, dict[str, Any]] | None = None,
) -> None:
    runs: dict[str, dict[str, Any]] = {}
    executed: dict[tuple[str, str, str, str, str, str], str] = {}
    groups: dict[str, list[dict[str, Any]]] = {}
    for index, raw in enumerate(require_list(value, "verification_runs")):
        run = require_object(raw, f"verification_runs[{index}]")
        require_keys(run, {
            "id", "check_id", "environment", "platform", "source_revision", "input_digest",
            "artifact_digest", "started_at", "duration_seconds", "result", "phase",
            "execution", "reused_from", "claim_refs", "isolation_refs",
            "overlap_group", "capacity_evidence_ref", "invalidation_reason",
        }, "verification run")
        run_id = require_text(run["id"], "verification run.id")
        if run_id in runs:
            raise RecordError(f"duplicate verification run id: {run_id}")
        check_id = require_text(run["check_id"], f"verification run {run_id}.check_id")
        if costs is not None and check_id not in costs:
            raise RecordError(f"verification run {run_id} has no measured cost inventory entry")
        for field in ("environment", "platform", "source_revision", "started_at"):
            require_text(run[field], f"verification run {run_id}.{field}")
        if run["source_revision"] != source_revision and not run["invalidation_reason"]:
            raise RecordError(f"verification run {run_id} has stale source revision without invalidation")
        if not DIGEST_PATTERN.fullmatch(str(run["input_digest"])):
            raise RecordError(f"verification run {run_id} has invalid input digest")
        if run["artifact_digest"] and not DIGEST_PATTERN.fullmatch(str(run["artifact_digest"])):
            raise RecordError(f"verification run {run_id} has invalid artifact digest")
        require_choice(run["result"], {"passed", "failed", "blocked"}, f"verification run {run_id}.result")
        require_choice(run["phase"], {"iteration", "final"}, f"verification run {run_id}.phase")
        require_choice(run["execution"], {"executed", "reused"}, f"verification run {run_id}.execution")
        duration = run["duration_seconds"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration < 0:
            raise RecordError(f"verification run {run_id} has invalid duration")
        require_list(run["claim_refs"], f"verification run {run_id}.claim_refs")
        isolation = require_list(run["isolation_refs"], f"verification run {run_id}.isolation_refs")
        group = run["overlap_group"]
        if group:
            require_text(group, f"verification run {run_id}.overlap_group")
            require_text(run["capacity_evidence_ref"], f"verification run {run_id}.capacity_evidence_ref")
            if not isolation:
                raise RecordError(f"concurrent verification run {run_id} lacks isolated resources")
            for other in groups.get(group, []):
                if set(isolation) & set(other["isolation_refs"]):
                    raise RecordError(f"concurrent verification runs share mutable state: {run_id}")
            groups.setdefault(group, []).append(run)
        identity = (check_id, run["environment"], run["platform"], run["source_revision"], run["input_digest"], run["phase"])
        if run["execution"] == "reused":
            origin = runs.get(run["reused_from"])
            if origin is None or origin["result"] != "passed" or origin["execution"] != "executed":
                raise RecordError(f"verification run {run_id} lacks a prior passed execution")
            origin_identity = (origin["check_id"], origin["environment"], origin["platform"], origin["source_revision"], origin["input_digest"], origin["phase"])
            if identity != origin_identity or run["result"] != "passed":
                raise RecordError(f"verification run {run_id} cannot reuse mismatched evidence")
            if costs is not None and costs[check_id]["reuse_policy"] == "never":
                raise RecordError(f"verification run {run_id} cannot reuse this check")
        elif run["result"] == "passed":
            if identity in executed and not run["invalidation_reason"]:
                raise RecordError(f"verification run {run_id} repeats an unchanged passed check")
            executed[identity] = run_id
        runs[run_id] = run


def verification_plan(
    costs: list[dict[str, Any]], runs: list[dict[str, Any]], *,
    source_revision: str, environment: str, platform: str, input_digests: dict[str, str],
) -> list[dict[str, Any]]:
    """Select reusable final checks by exact identity; never reuse an unmeasured shortcut."""

    inventory = validate_verification_costs(costs)
    plan = []
    for check_id, cost in inventory.items():
        digest = input_digests.get(check_id)
        if not digest or not DIGEST_PATTERN.fullmatch(digest):
            plan.append({"check_id": check_id, "action": "run", "reason": "missing current input digest"})
            continue
        previous = next((run for run in reversed(runs) if
            run.get("check_id") == check_id and run.get("environment") == environment
            and run.get("platform") == platform
            and run.get("source_revision") == source_revision
            and run.get("input_digest") == digest and run.get("phase") == "final"), None)
        origin = previous
        if previous and previous.get("execution") == "reused":
            origin = next((run for run in runs if run.get("id") == previous.get("reused_from")), None)
        if (previous and previous.get("result") == "passed" and origin
                and origin.get("result") == "passed" and origin.get("execution") == "executed"
                and (cost["reuse_policy"] != "immutable" or origin.get("artifact_digest"))
                and cost["reuse_policy"] != "never"):
            plan.append({"check_id": check_id, "action": "reuse", "run_id": origin["id"],
                         "estimated_seconds_saved": cost["setup_seconds"] + cost["median_seconds"]})
        else:
            plan.append({"check_id": check_id, "action": "run", "reason": "no valid final evidence"})
    return plan


def next_external_step(value: Any) -> dict[str, Any] | None:
    """Return the first actionable or blocked provider step after verified dependencies."""

    external = require_object(value, "external_work")
    steps = require_list(external.get("provider_steps"), "external_work.provider_steps")
    states = {step["id"]: step["state"] for step in steps}
    for step in steps:
        if step["state"] == "flow_verified":
            continue
        if all(states.get(dep) == "flow_verified" for dep in step["dependencies"]):
            return step
    return None


def source_recovery_plan(value: Any, *, target: str, source_identity: str) -> dict[str, Any]:
    """Choose only an authorized route to the same authoritative source."""

    external = require_object(value, "external_work")
    routes = [route for route in require_list(external.get("source_routes"), "external_work.source_routes")
              if route["target"] == target and route["source_identity"] == source_identity
              and route["authorization_ref"]]
    verified = next((route for route in routes if route["state"] == "verified"), None)
    if verified:
        return {"action": "use_verified", "route_id": verified["id"], "channel": verified["channel"]}
    available = next((route for route in routes if route["state"] == "available"), None)
    if available:
        return {"action": "check_authorized_route", "route_id": available["id"], "channel": available["channel"]}
    return {"action": "blocked", "reason": "no verified or available authorized route to the same source"}


def validate_external_work(value: Any, *, require_final: bool) -> None:
    external = require_object(value, "external_work")
    require_keys(external, {"source_routes", "provider_steps", "artifact_checks"}, "external_work")
    route_ids: set[str] = set()
    for index, raw in enumerate(require_list(external["source_routes"], "external_work.source_routes")):
        route = require_object(raw, f"external_work.source_routes[{index}]")
        require_keys(route, {"id", "target", "source_identity", "channel", "authorization_ref", "state", "failure_class", "checked_at", "evidence_ref"}, "source route")
        route_id = require_text(route["id"], "source route.id")
        if route_id in route_ids:
            raise RecordError(f"duplicate source route: {route_id}")
        route_ids.add(route_id)
        for field in ("target", "source_identity", "channel", "authorization_ref", "checked_at"):
            require_text(route[field], f"source route {route_id}.{field}")
        require_choice(route["state"], {"available", "failed", "verified"}, f"source route {route_id}.state")
        if route["state"] == "failed":
            require_choice(route["failure_class"], SOURCE_FAILURES, f"source route {route_id}.failure_class")
        if route["state"] in {"failed", "verified"}:
            require_text(route["evidence_ref"], f"source route {route_id}.evidence_ref")
    steps: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(require_list(external["provider_steps"], "external_work.provider_steps")):
        step = require_object(raw, f"external_work.provider_steps[{index}]")
        require_keys(step, {"id", "target", "environment", "action", "dependencies", "state", "required", "observations", "evidence_ref", "checked_at", "blocker"}, "provider step")
        step_id = require_text(step["id"], "provider step.id")
        if step_id in steps:
            raise RecordError(f"duplicate provider step: {step_id}")
        for field in ("target", "environment", "action"):
            require_text(step[field], f"provider step {step_id}.{field}")
        require_choice(step["state"], EXTERNAL_STATES, f"provider step {step_id}.state")
        if not isinstance(step["required"], bool):
            raise RecordError(f"provider step {step_id}.required must be boolean")
        observations = require_list(step["observations"], f"provider step {step_id}.observations")
        stages = {"observed": 0, "saved": 1, "read_back": 2, "flow_verified": 3}
        prior_rank = -1
        for observation_index, raw_observation in enumerate(observations):
            observation = require_object(raw_observation, f"provider step {step_id}.observations[{observation_index}]")
            require_keys(observation, {"stage", "checked_at", "evidence_ref"}, "provider observation")
            stage = require_choice(observation["stage"], set(stages), f"provider step {step_id}.observation.stage")
            if stages[stage] < prior_rank:
                raise RecordError(f"provider step {step_id} has out-of-order observations")
            prior_rank = stages[stage]
            require_text(observation["checked_at"], f"provider step {step_id}.observation.checked_at")
            require_text(observation["evidence_ref"], f"provider step {step_id}.observation.evidence_ref")
        if step["state"] == "pending" and observations:
            raise RecordError(f"pending provider step {step_id} has completed observations")
        if step["state"] in {"observed", "saved", "read_back", "flow_verified"}:
            require_text(step["evidence_ref"], f"provider step {step_id}.evidence_ref")
            require_text(step["checked_at"], f"provider step {step_id}.checked_at")
            if not observations or observations[-1]["stage"] != step["state"]:
                raise RecordError(f"provider step {step_id} disagrees with observation history")
            if (step["evidence_ref"] != observations[-1]["evidence_ref"]
                    or step["checked_at"] != observations[-1]["checked_at"]):
                raise RecordError(f"provider step {step_id} has stale current evidence")
        if step["state"] == "flow_verified" and not any(
            observation["stage"] == "read_back" for observation in observations
        ):
            raise RecordError(f"provider step {step_id} lacks live readback before flow verification")
        if step["state"] == "blocked":
            require_text(step["blocker"], f"provider step {step_id}.blocker")
        if require_final and step["required"] and step["state"] != "flow_verified":
            raise RecordError(f"required provider step {step_id} lacks flow verification")
        steps[step_id] = step
    for step_id, step in steps.items():
        for dependency in require_list(step["dependencies"], f"provider step {step_id}.dependencies"):
            if dependency not in steps or dependency == step_id:
                raise RecordError(f"provider step {step_id} has invalid dependency")
            if step["state"] == "flow_verified" and steps[dependency]["state"] != "flow_verified":
                raise RecordError(f"provider step {step_id} has unverified dependency")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visiting:
            raise RecordError("provider steps contain a dependency cycle")
        if step_id in visited:
            return
        visiting.add(step_id)
        for dependency in steps[step_id]["dependencies"]:
            visit(dependency)
        visiting.remove(step_id)
        visited.add(step_id)

    for step_id in steps:
        visit(step_id)
    check_ids: set[str] = set()
    for index, raw in enumerate(require_list(external["artifact_checks"], "external_work.artifact_checks")):
        check = require_object(raw, f"external_work.artifact_checks[{index}]")
        require_keys(check, {"id", "source_ref", "artifact_ref", "source_units", "verified_units", "state", "required", "evidence_ref"}, "artifact check")
        check_id = require_text(check["id"], "artifact check.id")
        if check_id in check_ids:
            raise RecordError(f"duplicate artifact check: {check_id}")
        check_ids.add(check_id)
        require_text(check["source_ref"], f"artifact check {check_id}.source_ref")
        require_text(check["artifact_ref"], f"artifact check {check_id}.artifact_ref")
        source_units = require_list(check["source_units"], f"artifact check {check_id}.source_units")
        verified_units = require_list(check["verified_units"], f"artifact check {check_id}.verified_units")
        for unit in source_units + verified_units:
            require_text(unit, f"artifact check {check_id}.unit")
        if len(source_units) != len(set(source_units)) or len(verified_units) != len(set(verified_units)):
            raise RecordError(f"artifact check {check_id} has duplicate source units")
        require_choice(check["state"], {"pending", "verified"}, f"artifact check {check_id}.state")
        if not isinstance(check["required"], bool):
            raise RecordError(f"artifact check {check_id}.required must be boolean")
        if check["state"] == "verified":
            require_text(check["evidence_ref"], f"artifact check {check_id}.evidence_ref")
            if not source_units or set(source_units) != set(verified_units):
                raise RecordError(f"artifact check {check_id} does not cover every source unit")
        if require_final and check["required"] and check["state"] != "verified":
            raise RecordError(f"required artifact check {check_id} is unverified")


def validate_record(
    payload: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
    source_root: Path | None = None,
    require_final: bool = False,
) -> None:
    """Validate one workflow record and its cross-section invariants."""

    reject_secrets(payload)
    require_keys(
        payload,
        {
            "schema_version",
            "record_kind",
            "record_id",
            "repository",
            "provenance",
            "applicability",
            "status",
        },
        "$",
    )
    if payload["schema_version"] != SCHEMA_VERSION:
        raise RecordError(
            f"schema_version must be {SCHEMA_VERSION}; migrate incompatible records explicitly"
        )
    if payload["record_kind"] not in RECORD_KINDS:
        raise RecordError("record_kind is not supported")
    require_text(payload["record_id"], "record_id")
    repository = require_object(payload["repository"], "repository")
    require_keys(
        repository,
        {"identity", "default_branch", "revision"},
        "repository",
    )
    require_text(repository["identity"], "repository.identity")
    source_revision = require_text(repository["revision"], "repository.revision")
    provenance = require_object(payload["provenance"], "provenance")
    require_keys(provenance, {"created_at", "sources"}, "provenance")
    validate_evidence_sources(provenance["sources"], source_root=source_root)
    validate_applicability(payload["applicability"])
    blocked_capabilities = [
        name
        for name, capability in payload["applicability"].items()
        if capability["state"] == "blocked"
    ]
    if blocked_capabilities and payload["status"] not in {"planned", "blocked"}:
        raise RecordError(
            "blocking capabilities prevent execution: "
            + ", ".join(sorted(blocked_capabilities))
        )
    if payload["record_kind"] == "repository_profile":
        require_keys(payload, {"capabilities", "environment_keys"}, "$")
        capabilities = require_object(payload["capabilities"], "capabilities")
        if "verification_costs" in capabilities:
            validate_verification_costs(capabilities["verification_costs"])
        for index, key in enumerate(
            require_list(payload["environment_keys"], "environment_keys")
        ):
            if not isinstance(key, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
                raise RecordError(f"environment_keys[{index}] is not a key name")
        return

    require_keys(
        payload,
        {
            "profile_ref",
            "task",
            "scope",
            "approvals",
            "resources",
            "validation",
            "failures",
            "sandboxes",
            "artifacts",
            "operations",
            "verification",
            "evidence",
        },
        "$",
    )
    profile_ref = require_object(payload["profile_ref"], "profile_ref")
    require_keys(profile_ref, {"record_id", "digest"}, "profile_ref")
    if profile is not None:
        validate_record(profile, source_root=source_root)
        if profile["record_kind"] != "repository_profile":
            raise RecordError("profile_ref target is not a repository profile")
        if profile_ref["record_id"] != profile["record_id"]:
            raise RecordError("task consumed a different capability profile")
        if profile_ref["digest"] != content_digest(profile):
            raise RecordError("task capability profile is stale")
        if profile["repository"]["identity"] != repository["identity"]:
            raise RecordError("task and capability profile repositories differ")
    task = require_object(payload["task"], "task")
    require_keys(task, {"issue", "objective", "worktree", "base_revision"}, "task")
    issue_url = require_text(task["issue"], "task.issue")
    require_text(task["objective"], "task.objective")
    require_text(task["worktree"], "task.worktree")
    planning_mode = task.get("planning_mode", "legacy")
    if planning_mode not in {"legacy", "github_issue"}:
        raise RecordError("task.planning_mode is unsupported")
    if planning_mode == "github_issue":
        if "plan" not in task:
            raise RecordError("GitHub issue planning requires task.plan")
        validate_plan_comment(
            task["plan"],
            issue_url=issue_url,
            source_revision=source_revision,
            task_status=payload["status"],
        )
    if task["base_revision"] != source_revision and payload["status"] == "planned":
        raise RecordError("planned task base revision differs from repository revision")
    if "delivery_contract" in payload:
        validate_delivery_contract(payload["delivery_contract"], require_final=require_final)
    validate_scope(payload["scope"])
    approved_plan = False
    reclamation_approval_ids: set[str] = set()
    fallback_approval_ids: set[str] = set()
    for index, approval_value in enumerate(require_list(payload["approvals"], "approvals")):
        approval = require_object(approval_value, f"approvals[{index}]")
        require_keys(approval, {"id", "kind", "state", "scope"}, f"approvals[{index}]")
        approval_id = require_text(approval["id"], f"approvals[{index}].id")
        if approval["state"] == "approved":
            if approval["kind"] == "implementation_plan":
                approved_plan = True
            elif approval["kind"] == "shared_resource_reclamation":
                reclamation_approval_ids.add(approval_id)
            elif approval["kind"] == "verification_fallback":
                fallback_approval_ids.add(approval_id)
    if payload["status"] not in {"planned", "blocked"} and not approved_plan:
        raise RecordError("execution requires an approved implementation plan")
    validate_resources(
        payload["resources"],
        reclamation_approval_ids,
        task_status=payload["status"],
    )
    steps = validate_steps(payload["validation"])
    if payload["validation"]["source_revision"] != source_revision:
        raise RecordError("validation results have stale source identity")
    if "verification_runs" in payload:
        costs = None
        if profile is not None:
            costs = validate_verification_costs(profile["capabilities"].get("verification_costs", []))
        validate_verification_runs(payload["verification_runs"], source_revision=source_revision, costs=costs)
    if "external_work" in payload:
        validate_external_work(payload["external_work"], require_final=require_final)
    validate_failures(payload["failures"], steps)
    validate_sandboxes(payload["sandboxes"])
    artifact_ids = validate_artifacts(payload["artifacts"], source_revision)
    validate_operations(payload["operations"], source_revision)
    satisfied_claims = validate_verification(
        payload["verification"],
        artifact_ids=artifact_ids,
        fallback_approval_ids=fallback_approval_ids,
    )
    validate_evidence(
        payload["evidence"],
        source_revision=source_revision,
        steps=steps,
        artifact_ids=artifact_ids,
        satisfied_claims=satisfied_claims,
        require_final=require_final,
    )


def state_directory(
    *,
    platform_name: str | None = None,
    environment: Any = None,
    home: Path | None = None,
) -> Path:
    """Resolve a scoped, cross-platform per-user workflow state directory."""

    selected_platform = platform_name or os.name
    selected_environment = environment if environment is not None else os.environ
    selected_home = home if home is not None else Path.home()
    def absolute_path(value: str, label: str) -> Path:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise RecordError(f"{label} must be an absolute path")
        return path

    explicit = selected_environment.get("AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR")
    if explicit:
        return absolute_path(explicit, "AGENTIC_WORKFLOWS_WORKFLOW_STATE_DIR")
    if selected_platform == "nt":
        base = selected_environment.get("LOCALAPPDATA")
        if base:
            return (
                absolute_path(base, "LOCALAPPDATA")
                / "Agentic Workflows"
                / "standard-development-workflow"
            )
    state_home = selected_environment.get("XDG_STATE_HOME")
    if state_home:
        return (
            absolute_path(state_home, "XDG_STATE_HOME")
            / "agentic-workflows"
            / "standard-development-workflow"
        )
    return (
        selected_home
        / ".local"
        / "state"
        / "agentic-workflows"
        / "standard-development-workflow"
    )


def summarize(payload: dict[str, Any]) -> str:
    """Return a concise human-readable record readback."""

    lines = [
        f"# {payload['record_kind'].replace('_', ' ').title()}",
        "",
        f"- Record: `{payload['record_id']}`",
        f"- Repository: `{payload['repository']['identity']}`",
        f"- Revision: `{payload['repository']['revision']}`",
        f"- Status: `{payload['status']}`",
    ]
    applicability = payload["applicability"]
    required = sorted(
        name for name, item in applicability.items() if item["state"] == "required"
    )
    blocked = sorted(
        name for name, item in applicability.items() if item["state"] == "blocked"
    )
    lines.append(f"- Required capabilities: {', '.join(required) if required else 'none'}")
    lines.append(f"- Blockers: {', '.join(blocked) if blocked else 'none'}")
    if payload["record_kind"] == "task_run":
        lines.extend(
            [
                f"- Issue: {payload['task']['issue']}",
                *(
                    [
                        f"- Plan: {payload['task']['plan']['comment_url']}",
                        f"- Plan state: `{payload['task']['plan']['state']}`",
                    ]
                    if payload["task"].get("planning_mode") == "github_issue"
                    else []
                ),
                f"- Objective: {payload['task']['objective']}",
                f"- Validation steps: {len(payload['validation']['steps'])}",
                f"- Open failures: {sum(not item['accepted'] for item in payload['failures'])}",
                f"- Evidence: `{payload['evidence']['status']}`",
            ]
        )
        if "delivery_contract" in payload:
            requirements = payload["delivery_contract"]["requirements"]
            outstanding = [item["id"] for item in requirements if item["state"] == "required" and item["status"] != "complete"]
            lines.append(f"- Outstanding deliverables: {', '.join(outstanding) if outstanding else 'none'}")
        if "verification_runs" in payload:
            runs = payload["verification_runs"]
            lines.append(f"- Verification runs: {len(runs)} ({sum(item['execution'] == 'reused' for item in runs)} reused)")
        if "external_work" in payload:
            next_step = next_external_step(payload["external_work"])
            lines.append(f"- Next external step: {next_step['id'] if next_step else 'none'}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("record", type=Path)
    validate_parser.add_argument("--profile", type=Path)
    validate_parser.add_argument("--source-root", type=Path)
    validate_parser.add_argument("--require-final", action="store_true")
    canonicalize_parser = subparsers.add_parser("canonicalize")
    canonicalize_parser.add_argument("record", type=Path)
    digest_parser = subparsers.add_parser("digest")
    digest_parser.add_argument("record", type=Path)
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("record", type=Path)
    contract_parser = subparsers.add_parser("contract-update")
    contract_parser.add_argument("record", type=Path)
    contract_parser.add_argument("update", type=Path)
    plan_parser = subparsers.add_parser("verification-plan")
    plan_parser.add_argument("record", type=Path)
    plan_parser.add_argument("--profile", required=True, type=Path)
    plan_parser.add_argument("--environment", required=True)
    plan_parser.add_argument("--platform", required=True)
    plan_parser.add_argument("--input-digests", required=True, type=Path)
    external_parser = subparsers.add_parser("next-external")
    external_parser.add_argument("record", type=Path)
    recovery_parser = subparsers.add_parser("source-recovery")
    recovery_parser.add_argument("record", type=Path)
    recovery_parser.add_argument("--target", required=True)
    recovery_parser.add_argument("--source-identity", required=True)
    profile_parser = subparsers.add_parser("profile-check")
    profile_parser.add_argument("samples", type=Path)
    subparsers.add_parser("state-dir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "state-dir":
            print(state_directory())
            return 0
        if args.command == "profile-check":
            print(json.dumps(profile_check(load_record(args.samples)), indent=2))
            return 0
        record = load_record(args.record)
        if args.command == "contract-update":
            if record["record_kind"] != "task_run":
                raise RecordError("contract updates require a task-run record")
            record["delivery_contract"] = reconcile_delivery_contract(
                record.get("delivery_contract", {"requirements": [], "changes": []}),
                load_record(args.update),
            )
            validate_record(record)
            sys.stdout.buffer.write(canonical_bytes(record))
            return 0
        if args.command == "verification-plan":
            profile = load_record(args.profile)
            validate_record(record, profile=profile)
            input_digests = load_record(args.input_digests)
            print(json.dumps(verification_plan(
                profile["capabilities"].get("verification_costs", []),
                record.get("verification_runs", []),
                source_revision=record["repository"]["revision"],
                environment=args.environment,
                platform=args.platform,
                input_digests=input_digests,
            ), indent=2))
            return 0
        if args.command == "next-external":
            validate_record(record)
            print(json.dumps(next_external_step(record.get("external_work", {
                "provider_steps": [],
            })), indent=2))
            return 0
        if args.command == "source-recovery":
            validate_record(record)
            print(json.dumps(source_recovery_plan(record.get("external_work", {
                "source_routes": [],
            }), target=args.target, source_identity=args.source_identity), indent=2))
            return 0
        if args.command == "canonicalize":
            sys.stdout.buffer.write(canonical_bytes(record))
            return 0
        if args.command == "digest":
            print(content_digest(record))
            return 0
        if args.command == "summary":
            validate_record(record)
            print(summarize(record), end="")
            return 0
        profile = load_record(args.profile) if args.profile else None
        validate_record(
            record,
            profile=profile,
            source_root=args.source_root,
            require_final=args.require_final,
        )
        print(f"Valid {record['record_kind']} record: {record['record_id']}")
        return 0
    except RecordError as error:
        print(f"Workflow record validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
