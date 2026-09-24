#!/usr/bin/env python3
"""Initialize, validate, and summarize transparent literature-review projects."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 1
REVIEW_TYPES = {
    "narrative",
    "integrative",
    "critical",
    "conceptual-theoretical",
    "state-of-the-art",
}
SYSTEMATIC_TYPES = {
    "systematic",
    "scoping",
    "rapid",
    "mapping",
    "umbrella",
    "meta-analysis",
    "meta-analytic",
    "prisma",
    "exhaustive",
}
STATUSES = {
    "planning",
    "searching",
    "synthesizing",
    "incomplete",
    "blocked",
    "complete",
}
CHECKS = {
    "counterevidence",
    "rival_explanations",
    "boundary_conditions",
    "seminal_work",
    "recent_work",
    "gaps",
    "stopping_rule_applied",
    "coverage_limits_reported",
}
REQUIRED_FILES = {
    "review-brief.md",
    "method-and-boundaries.md",
    "search-journal.csv",
    "source-decisions.csv",
    "concept-matrix.csv",
    "synthesis-map.md",
    "counterevidence-and-gaps.md",
    "citations.bib",
    "review-state.json",
}
REQUIRED_DIRECTORIES = {"papers", "metadata", "notes"}
CSV_HEADERS = {
    "search-journal.csv": [
        "search_id",
        "surface",
        "query_or_discovery_method",
        "searched_at",
        "limits",
        "result_count",
        "follow_up_route",
    ],
    "source-decisions.csv": [
        "decision_id",
        "source_id",
        "decision",
        "rationale",
        "reviewer_id",
        "decided_at",
        "method_phase",
    ],
    "concept-matrix.csv": [
        "concept_id",
        "concept",
        "source_id",
        "locator",
        "definition_or_theory",
        "method",
        "population_or_setting",
        "finding_or_argument",
        "disagreement_or_counterevidence",
        "limitation_or_boundary",
        "chronological_role",
        "gap_or_implication",
    ],
}
STATE_KEYS = {
    "schema_version",
    "review",
    "state_history",
    "sources",
    "claims",
    "unresolved_issues",
    "stage_approvals",
    "ai_contributions",
    "human_verification",
}
REVIEW_KEYS = {
    "id",
    "title",
    "review_type",
    "method_rationale",
    "review_type_details",
    "status",
    "purpose",
    "questions",
    "audience",
    "discipline",
    "integrity_policy",
    "coverage_limitations",
    "stopping_rule",
    "checks",
}
SOURCE_KEYS = {
    "id",
    "metadata_file",
    "note_file",
    "full_text_status",
    "pdf_file",
    "sha256",
    "bytes",
    "retrieved_at",
    "verification_sources",
}
CLAIM_KEYS = {
    "id",
    "statement",
    "interpretation_status",
    "supporting_source_ids",
    "contradicting_source_ids",
    "qualifications",
}
STATE_EVENT_KEYS = {"from_status", "to_status", "changed_at", "changed_by"}
ALLOWED_TRANSITIONS = {
    "none": {"planning"},
    "planning": {"searching", "blocked"},
    "searching": {"synthesizing", "incomplete", "blocked"},
    "synthesizing": {"complete", "incomplete", "blocked"},
    "incomplete": {"searching", "synthesizing", "blocked"},
    "blocked": {"planning", "searching"},
    "complete": {"incomplete"},
}
REVIEW_DETAIL_FIELDS = {
    "narrative": {
        "search_description",
        "evidence_level_approach",
        "endpoints",
    },
    "integrative": {
        "integration_purpose",
        "source_diversity",
        "framework_contribution",
    },
    "critical": {
        "evaluative_standpoint",
        "critique_target",
        "counterposition_method",
    },
    "conceptual-theoretical": {
        "constructs",
        "theory_relationship",
        "proposed_contribution",
    },
    "state-of-the-art": {
        "recency_boundary",
        "frontier_definition",
        "continuity_with_seminal_work",
    },
}
ID_PATTERNS = {
    "review": re.compile(r"^REV-[A-Z0-9][A-Z0-9-]{2,63}$"),
    "source": re.compile(r"^SRC-[A-Z0-9][A-Z0-9-]{2,63}$"),
    "claim": re.compile(r"^CLAIM-[A-Z0-9][A-Z0-9-]{2,63}$"),
    "search": re.compile(r"^SEARCH-[A-Z0-9][A-Z0-9-]{2,63}$"),
    "concept": re.compile(r"^CONCEPT-[A-Z0-9][A-Z0-9-]{2,63}$"),
    "decision": re.compile(r"^DECISION-[A-Z0-9][A-Z0-9-]{2,63}$"),
}
UNRESOLVED_MARKERS = (
    "CITATION NEEDED",
    "EVIDENCE REQUIRED",
    "STUDENT INPUT REQUIRED",
)
PROHIBITED_COMPLETION_PATTERNS = (
    re.compile(r"\bprisma[- ]compliant\b", re.IGNORECASE),
    re.compile(r"\bprisma compliance\b", re.IGNORECASE),
    re.compile(r"\bexhaustive (?:coverage|search)\b", re.IGNORECASE),
    re.compile(r"\bsystematic review (?:is )?complete\b", re.IGNORECASE),
    re.compile(r"\bcompleted (?:a )?systematic review\b", re.IGNORECASE),
    re.compile(r"\bmeta-analysis (?:is )?complete\b", re.IGNORECASE),
)
NOTE_HEADINGS = {
    "## Bibliographic identity",
    "## Selection rationale",
    "## Design and context",
    "## Author statements",
    "## Supported findings with locators",
    "## Limitations and boundary conditions",
    "## Reviewer interpretation",
    "## Planned synthesis use",
}
METADATA_KEYS = {
    "id",
    "title",
    "authors",
    "year",
    "identifier",
    "source_type",
    "source_url",
    "retrieved_at",
    "version",
    "verification_sources",
    "full_text_status",
    "pdf_file",
    "sha256",
    "bytes",
}


class ValidationError(Exception):
    """A deterministic project-contract error."""


def safe_relative(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValidationError(f"{label}: expected a non-empty relative path")
    candidate = root / value
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except ValueError as error:
        raise ValidationError(f"{label}: path escapes the project") from error
    if candidate.is_symlink():
        raise ValidationError(f"{label}: symbolic links are not allowed")
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"{label}: invalid JSON") from error


def require_exact_keys(record: object, expected: set[str], label: str) -> dict[str, object]:
    if not isinstance(record, dict):
        raise ValidationError(f"{label}: expected an object")
    actual = set(record)
    if actual != expected:
        missing = ",".join(sorted(expected - actual)) or "none"
        unexpected = ",".join(sorted(actual - expected)) or "none"
        raise ValidationError(
            f"{label}: fields differ (missing={missing}; unexpected={unexpected})"
        )
    return record


def parse_time(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise ValidationError(f"{label}: expected ISO-8601 text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValidationError(f"{label}: invalid ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ValidationError(f"{label}: timestamp must include a timezone")


def parse_date(value: str, label: str) -> None:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValidationError(f"{label}: expected YYYY-MM-DD") from error


def parse_csv(root: Path, name: str) -> list[dict[str, str]]:
    path = root / name
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != CSV_HEADERS[name]:
                raise ValidationError(f"{name}: header differs from schema v1")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        raise ValidationError(f"{name}: malformed CSV") from error
    if any(None in row for row in rows):
        raise ValidationError(f"{name}: row has too many columns")
    return rows


def validate_search_rows(rows: list[dict[str, str]], final: bool) -> None:
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        identifier = row["search_id"]
        if not ID_PATTERNS["search"].fullmatch(identifier) or identifier in seen:
            raise ValidationError(f"search-journal.csv:{index}: invalid or duplicate search_id")
        seen.add(identifier)
        for field in ("surface", "query_or_discovery_method", "searched_at", "limits", "follow_up_route"):
            if not row[field].strip():
                raise ValidationError(f"search-journal.csv:{index}: {field} is required")
        parse_date(row["searched_at"], f"search-journal.csv:{index}:searched_at")
        result_count = row["result_count"]
        if result_count != "unknown" and (
            not result_count.isdigit() or int(result_count) < 0
        ):
            raise ValidationError(
                f"search-journal.csv:{index}: result_count must be a count or unknown"
            )
    if final and not rows:
        raise ValidationError("search-journal.csv: a final review needs discovery provenance")


def validate_decision_rows(
    rows: list[dict[str, str]], source_ids: set[str], final: bool
) -> set[str]:
    decision_ids: set[str] = set()
    decided: set[str] = set()
    latest: dict[str, str] = {}
    latest_time: dict[str, datetime] = {}
    for index, row in enumerate(rows, start=2):
        decision_id = row["decision_id"]
        source_id = row["source_id"]
        if (
            not ID_PATTERNS["decision"].fullmatch(decision_id)
            or decision_id in decision_ids
        ):
            raise ValidationError(
                f"source-decisions.csv:{index}: invalid or duplicate decision_id"
            )
        decision_ids.add(decision_id)
        if not ID_PATTERNS["source"].fullmatch(source_id):
            raise ValidationError(
                f"source-decisions.csv:{index}: invalid source_id"
            )
        decided.add(source_id)
        if row["decision"] not in {"include", "exclude", "hold"}:
            raise ValidationError(f"source-decisions.csv:{index}: invalid decision")
        for field in ("rationale", "reviewer_id", "decided_at", "method_phase"):
            if not row[field].strip():
                raise ValidationError(f"source-decisions.csv:{index}: {field} is required")
        parse_time(row["decided_at"], f"source-decisions.csv:{index}:decided_at")
        decided_at = datetime.fromisoformat(row["decided_at"].replace("Z", "+00:00"))
        if source_id in latest_time and decided_at < latest_time[source_id]:
            raise ValidationError(
                f"source-decisions.csv:{index}: source decisions are not chronological"
            )
        latest_time[source_id] = decided_at
        latest[source_id] = row["decision"]
    missing = source_ids - decided
    if missing:
        raise ValidationError(
            f"source-decisions.csv: retained sources lack decisions: {','.join(sorted(missing))}"
        )
    if final and any(latest[source_id] != "include" for source_id in source_ids):
        raise ValidationError("source-decisions.csv: final retained sources must be included")
    return decided


def validate_concept_rows(
    rows: list[dict[str, str]], source_ids: set[str], final: bool
) -> None:
    seen: set[tuple[str, str]] = set()
    represented: set[str] = set()
    for index, row in enumerate(rows, start=2):
        concept_id = row["concept_id"]
        source_id = row["source_id"]
        key = (concept_id, source_id)
        if not ID_PATTERNS["concept"].fullmatch(concept_id) or key in seen:
            raise ValidationError(
                f"concept-matrix.csv:{index}: invalid or duplicate concept/source pair"
            )
        seen.add(key)
        if source_id not in source_ids:
            raise ValidationError(f"concept-matrix.csv:{index}: unknown source_id")
        represented.add(source_id)
        for field in ("concept", "locator", "finding_or_argument"):
            if not row[field].strip():
                raise ValidationError(f"concept-matrix.csv:{index}: {field} is required")
    if final and not rows:
        raise ValidationError("concept-matrix.csv: a final review needs concept evidence")
    if final and represented != source_ids:
        raise ValidationError("concept-matrix.csv: final source coverage is incomplete")


def validate_source(root: Path, source: object, seen: set[str]) -> str:
    record = require_exact_keys(source, SOURCE_KEYS, "review-state.json:source")
    source_id = record["id"]
    if (
        not isinstance(source_id, str)
        or not ID_PATTERNS["source"].fullmatch(source_id)
        or source_id in seen
    ):
        raise ValidationError("review-state.json: invalid or duplicate source id")
    seen.add(source_id)
    status = record["full_text_status"]
    if status not in {"available", "unavailable", "partial", "not-required"}:
        raise ValidationError(f"{source_id}: invalid full_text_status")
    parse_time(record["retrieved_at"], f"{source_id}:retrieved_at")
    verification = record["verification_sources"]
    if not isinstance(verification, list) or len(set(verification)) < 2:
        raise ValidationError(f"{source_id}: at least two verification sources are required")

    metadata_path = safe_relative(root, record["metadata_file"], f"{source_id}:metadata_file")
    note_path = safe_relative(root, record["note_file"], f"{source_id}:note_file")
    if not metadata_path.is_file() or not note_path.is_file():
        raise ValidationError(f"{source_id}: metadata and note files are required")
    metadata = require_exact_keys(
        load_json(metadata_path, f"{source_id}:metadata"),
        METADATA_KEYS,
        f"{source_id}:metadata",
    )
    for field in ("id", "retrieved_at", "full_text_status", "pdf_file", "sha256", "bytes"):
        if metadata[field] != record[field]:
            raise ValidationError(f"{source_id}: metadata {field} differs from state")
    if metadata["verification_sources"] != verification:
        raise ValidationError(f"{source_id}: metadata verification_sources differ from state")
    if metadata["id"] != source_id or not isinstance(metadata["authors"], list) or not metadata["authors"]:
        raise ValidationError(f"{source_id}: bibliographic identity is incomplete")

    note = note_path.read_text(encoding="utf-8")
    if source_id not in note:
        raise ValidationError(f"{source_id}: note does not identify its source")
    missing_headings = sorted(heading for heading in NOTE_HEADINGS if heading not in note)
    if missing_headings:
        raise ValidationError(f"{source_id}: note is missing required sections")
    if not re.search(r"\[Locator:\s*[^\]]+\]", note):
        raise ValidationError(f"{source_id}: note has no evidence locator")

    if status == "available":
        pdf_path = safe_relative(root, record["pdf_file"], f"{source_id}:pdf_file")
        if not pdf_path.is_file() or pdf_path.read_bytes()[:5] != b"%PDF-":
            raise ValidationError(f"{source_id}: available full text is not a PDF")
        if record["bytes"] != pdf_path.stat().st_size:
            raise ValidationError(f"{source_id}: PDF byte count differs")
        if record["sha256"] != sha256(pdf_path):
            raise ValidationError(f"{source_id}: PDF SHA-256 differs")
    elif record["pdf_file"] or record["sha256"] or record["bytes"] != 0:
        raise ValidationError(f"{source_id}: unavailable full text must not claim a PDF")
    return source_id


def validate_claim(claim: object, source_ids: set[str], seen: set[str]) -> None:
    record = require_exact_keys(claim, CLAIM_KEYS, "review-state.json:claim")
    claim_id = record["id"]
    if (
        not isinstance(claim_id, str)
        or not ID_PATTERNS["claim"].fullmatch(claim_id)
        or claim_id in seen
    ):
        raise ValidationError("review-state.json: invalid or duplicate claim id")
    seen.add(claim_id)
    if record["interpretation_status"] not in {
        "source-supported",
        "reviewer-interpretation",
        "proposal",
    }:
        raise ValidationError(f"{claim_id}: invalid interpretation_status")
    supporting = record["supporting_source_ids"]
    contradicting = record["contradicting_source_ids"]
    if not isinstance(supporting, list) or not supporting:
        raise ValidationError(f"{claim_id}: material claim has no supporting source")
    if not isinstance(contradicting, list):
        raise ValidationError(f"{claim_id}: contradicting_source_ids must be a list")
    referenced = set(supporting) | set(contradicting)
    if len(supporting) != len(set(supporting)) or len(contradicting) != len(set(contradicting)):
        raise ValidationError(f"{claim_id}: duplicate source mapping")
    if not referenced <= source_ids:
        raise ValidationError(f"{claim_id}: references an unknown source")
    if not isinstance(record["statement"], str) or not record["statement"].strip():
        raise ValidationError(f"{claim_id}: statement is required")
    if not isinstance(record["qualifications"], str) or not record["qualifications"].strip():
        raise ValidationError(f"{claim_id}: qualifications are required")


def validate_state_history(history: object, current_status: object) -> None:
    if not isinstance(history, list) or not history:
        raise ValidationError("review-state.json: state_history must not be empty")
    previous = "none"
    previous_time: datetime | None = None
    for index, event in enumerate(history):
        record = require_exact_keys(
            event,
            STATE_EVENT_KEYS,
            f"review-state.json:state_history:{index}",
        )
        from_status = record["from_status"]
        to_status = record["to_status"]
        if from_status != previous or to_status not in ALLOWED_TRANSITIONS.get(
            str(from_status), set()
        ):
            raise ValidationError(
                f"review-state.json: invalid state transition at history index {index}"
            )
        if not isinstance(record["changed_by"], str) or not record["changed_by"].strip():
            raise ValidationError(
                f"review-state.json: state history {index} needs changed_by"
            )
        parse_time(record["changed_at"], f"review-state.json:state_history:{index}")
        changed_at = datetime.fromisoformat(
            str(record["changed_at"]).replace("Z", "+00:00")
        )
        if previous_time is not None and changed_at < previous_time:
            raise ValidationError("review-state.json: state history is not chronological")
        previous_time = changed_at
        previous = str(to_status)
    if previous != current_status:
        raise ValidationError("review-state.json: state history does not match current status")


def scan_project_text(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValidationError(f"{path.relative_to(root)}: symbolic links are not allowed")
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".json",
            ".csv",
            ".bib",
            ".txt",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in UNRESOLVED_MARKERS:
            if marker in text:
                raise ValidationError(
                    f"{path.relative_to(root)}: unresolved marker remains visible: {marker}"
                )
        for pattern in PROHIBITED_COMPLETION_PATTERNS:
            if pattern.search(text):
                raise ValidationError(
                    f"{path.relative_to(root)}: prohibited systematic completion claim"
                )


def validate_project(root: Path, require_final: bool = False) -> dict[str, object]:
    if root.is_symlink() or not root.is_dir():
        raise ValidationError("project path must be a real directory")
    for name in sorted(REQUIRED_FILES):
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValidationError(f"{name}: required regular file is missing")
    for name in sorted(REQUIRED_DIRECTORIES):
        path = root / name
        if not path.is_dir() or path.is_symlink():
            raise ValidationError(f"{name}: required real directory is missing")

    state = require_exact_keys(
        load_json(root / "review-state.json", "review-state.json"),
        STATE_KEYS,
        "review-state.json",
    )
    if state["schema_version"] != SCHEMA_VERSION:
        raise ValidationError("review-state.json: unsupported schema_version")
    review = require_exact_keys(state["review"], REVIEW_KEYS, "review-state.json:review")
    review_id = review["id"]
    if not isinstance(review_id, str) or not ID_PATTERNS["review"].fullmatch(review_id):
        raise ValidationError("review-state.json: invalid review id")
    if not isinstance(review["title"], str) or not review["title"].strip():
        raise ValidationError("review-state.json: title is required")
    review_type = review["review_type"]
    if review_type in SYSTEMATIC_TYPES:
        raise ValidationError("review-state.json: systematic intent must route to the systematic plugin")
    if review_type not in REVIEW_TYPES:
        raise ValidationError("review-state.json: unsupported review_type")
    details = require_exact_keys(
        review["review_type_details"],
        REVIEW_DETAIL_FIELDS[review_type],
        "review-state.json:review_type_details",
    )
    if not isinstance(review["method_rationale"], str):
        raise ValidationError("review-state.json: method_rationale must be text")
    if any(not isinstance(value, str) for value in details.values()):
        raise ValidationError("review-state.json: review-type details must be text")
    if review["status"] not in STATUSES:
        raise ValidationError("review-state.json: invalid status")
    validate_state_history(state["state_history"], review["status"])
    checks = require_exact_keys(review["checks"], CHECKS, "review-state.json:checks")
    if any(not isinstance(value, bool) for value in checks.values()):
        raise ValidationError("review-state.json: closing checks must be booleans")
    if not isinstance(state["unresolved_issues"], list):
        raise ValidationError("review-state.json: unresolved_issues must be a list")

    source_records = state["sources"]
    if not isinstance(source_records, list):
        raise ValidationError("review-state.json: sources must be a list")
    source_ids: set[str] = set()
    source_statuses: dict[str, str] = {}
    for source in source_records:
        source_id = validate_source(root, source, source_ids)
        source_statuses[source_id] = source["full_text_status"]

    metadata_ids = {path.stem for path in (root / "metadata").glob("*.json")}
    note_ids = {path.stem for path in (root / "notes").glob("*.md")}
    pdf_ids = {path.stem for path in (root / "papers").glob("*.pdf")}
    if metadata_ids != source_ids or note_ids != source_ids:
        raise ValidationError("source, metadata, and note identifiers do not match exactly")
    expected_pdf_ids = {
        source["id"] for source in source_records if source["full_text_status"] == "available"
    }
    if pdf_ids != expected_pdf_ids:
        raise ValidationError("PDF and available-source identifiers do not match exactly")

    claims = state["claims"]
    if not isinstance(claims, list):
        raise ValidationError("review-state.json: claims must be a list")
    claim_ids: set[str] = set()
    for claim in claims:
        validate_claim(claim, source_ids, claim_ids)
        unavailable = {
            source_id
            for source_id in claim["supporting_source_ids"]
            if source_statuses[source_id] != "available"
        }
        if unavailable:
            raise ValidationError(
                f"{claim['id']}: supporting full text is unavailable: {','.join(sorted(unavailable))}"
            )

    search_rows = parse_csv(root, "search-journal.csv")
    decision_rows = parse_csv(root, "source-decisions.csv")
    concept_rows = parse_csv(root, "concept-matrix.csv")
    final = require_final or review["status"] == "complete"
    validate_search_rows(search_rows, final)
    validate_decision_rows(decision_rows, source_ids, final)
    validate_concept_rows(concept_rows, source_ids, final)

    if final:
        if review["status"] != "complete":
            raise ValidationError("review-state.json: --require-final needs complete status")
        if not source_ids or not claim_ids:
            raise ValidationError("review-state.json: final review needs sources and claims")
        if review["integrity_policy"].strip().lower() in {"", "unknown"}:
            raise ValidationError("review-state.json: final review has unknown integrity policy")
        if not review["method_rationale"].strip() or any(
            not value.strip() for value in details.values()
        ):
            raise ValidationError(
                "review-state.json: final review lacks review-type method details"
            )
        if not review["coverage_limitations"]:
            raise ValidationError("review-state.json: final review must state coverage limitations")
        if not review["stopping_rule"].strip():
            raise ValidationError("review-state.json: final review must state a stopping rule")
        if not all(checks.values()):
            missing = ",".join(sorted(key for key, value in checks.items() if not value))
            raise ValidationError(f"review-state.json: closing checks are incomplete: {missing}")
        if state["unresolved_issues"]:
            raise ValidationError("review-state.json: final review has unresolved issues")
        if any(status != "available" for status in source_statuses.values()):
            raise ValidationError("review-state.json: final review has unavailable full text")

    scan_project_text(root)
    return {
        "review_id": review_id,
        "review_type": review_type,
        "status": review["status"],
        "sources": len(source_ids),
        "claims": len(claim_ids),
        "searches": len(search_rows),
        "concept_rows": len(concept_rows),
    }


def template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "templates"


def init_project(destination: Path, title: str, review_type: str) -> dict[str, object]:
    normalized_type = review_type.strip().lower()
    if not title.strip():
        raise ValidationError("title is required")
    if normalized_type in SYSTEMATIC_TYPES:
        raise ValidationError("systematic intent must route to the Systematic Literature Review plugin")
    if normalized_type not in REVIEW_TYPES:
        raise ValidationError("unsupported review type")
    if destination.exists():
        if destination.is_symlink() or not destination.is_dir():
            raise ValidationError("destination must be a real directory")
        if any(destination.iterdir()):
            raise ValidationError("destination is not empty")
    else:
        destination.mkdir(parents=True)
    for name in REQUIRED_DIRECTORIES:
        (destination / name).mkdir()
    for source in template_root().iterdir():
        if source.is_file():
            shutil.copyfile(source, destination / source.name)
    state_path = destination / "review-state.json"
    state = load_json(state_path, "review-state.json")
    digest = hashlib.sha256(f"{title.strip()}|{normalized_type}".encode()).hexdigest()[:12].upper()
    state["review"]["id"] = f"REV-{digest}"
    state["review"]["title"] = title.strip()
    state["review"]["review_type"] = normalized_type
    state["review"]["review_type_details"] = {
        field: "" for field in sorted(REVIEW_DETAIL_FIELDS[normalized_type])
    }
    state["state_history"][0]["changed_at"] = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return validate_project(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("project_dir", type=Path)
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--review-type", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("project_dir", type=Path)
    validate_parser.add_argument("--require-final", action="store_true")
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("project_dir", type=Path)
    arguments = parser.parse_args()

    try:
        root = arguments.project_dir.expanduser().resolve()
        if arguments.command == "init":
            result = init_project(root, arguments.title, arguments.review_type)
            print(f"PASS: initialized {result['review_id']} ({result['review_type']})")
        else:
            result = validate_project(
                root,
                require_final=getattr(arguments, "require_final", False),
            )
            if arguments.command == "validate":
                print(
                    "PASS: "
                    f"{result['review_id']} status={result['status']} "
                    f"sources={result['sources']} claims={result['claims']}"
                )
            else:
                print(json.dumps(result, sort_keys=True))
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
