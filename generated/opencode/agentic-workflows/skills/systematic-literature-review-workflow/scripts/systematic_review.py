#!/usr/bin/env python3
"""Deterministic, standard-library structural tooling for systematic-review projects."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
FORMULA_PREFIXES = ("=", "+", "-", "@")
FINAL_STATES = {"complete", "update_due", "superseded"}
REVIEW_STATES = {
    "feasibility_draft",
    "protocol_draft",
    "protocol_approved",
    "search_in_progress",
    "screening_in_progress",
    "extraction_in_progress",
    "appraisal_in_progress",
    "synthesis_in_progress",
    "reporting_in_progress",
    "blocked",
    *FINAL_STATES,
}
FORWARD_STATES = [
    "feasibility_draft",
    "protocol_draft",
    "protocol_approved",
    "search_in_progress",
    "screening_in_progress",
    "extraction_in_progress",
    "appraisal_in_progress",
    "synthesis_in_progress",
    "reporting_in_progress",
    "complete",
]
REQUIRED_PATHS = {
    "review-charter.md",
    "protocol/protocol.md",
    "protocol/protocol-state.json",
    "protocol/amendments.csv",
    "searches/search-run-ledger.csv",
    "searches/raw-exports/manifest.csv",
    "records/records.csv",
    "records/reports.csv",
    "records/studies.csv",
    "records/identity-links.csv",
    "dedup/dedup-decisions.csv",
    "screening/title-abstract-decisions.csv",
    "screening/full-text-decisions.csv",
    "screening/conflicts.csv",
    "screening/excluded-full-text.csv",
    "extraction/extraction-form.json",
    "extraction/extraction-values.csv",
    "extraction/conflicts.csv",
    "extraction/transformations.csv",
    "appraisal/appraisal-plan.md",
    "appraisal/appraisal-decisions.csv",
    "synthesis/synthesis-plan.md",
    "synthesis/synthesis-data.csv",
    "synthesis/synthesis-report.md",
    "reporting/flow-counts.json",
    "reporting/applicable-checklist.md",
    "reporting/review-report.md",
    "reporting/limitations-and-deviations.md",
    "citations.bib",
    "audit/review-state.json",
    "audit/contributor-actions.csv",
    "audit/automation-log.csv",
    "audit/validation-report.txt",
}
ALLOWED_TRANSITIONS = {
    (left, right)
    for index, left in enumerate(FORWARD_STATES)
    for right in FORWARD_STATES[index + 1 : index + 2]
} | {
    (state, "blocked") for state in REVIEW_STATES - {"blocked", "superseded"}
} | {
    ("blocked", state) for state in FORWARD_STATES
} | {
    ("complete", "update_due"),
    ("complete", "superseded"),
    ("update_due", "search_in_progress"),
    ("update_due", "superseded"),
}


class ReviewError(ValueError):
    """A safe, user-facing contract violation."""


def _inside(root: Path, target: Path) -> Path:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError as error:
        raise ReviewError("path escapes the selected review project") from error
    return resolved_target


def project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ReviewError("review project root must not be a symbolic link")
    return path.resolve()


def _atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_text(path: Path, content: str) -> None:
    _atomic_bytes(path, content.encode("utf-8"))


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ReviewError(f"invalid JSON at {path.name}: {error}") from error


def _rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as error:
        raise ReviewError(f"invalid delimited ledger at {path.name}: {error}") from error


def _write_rows(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        encoding="utf-8",
        prefix=f".{path.name}.",
        dir=path.parent,
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _safe_cell(value: Any) -> str:
    text = "" if value is None else str(value).replace("\x00", "")
    if text.startswith(FORMULA_PREFIXES):
        return f"'{text}"
    return text


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _require_id(value: str, label: str) -> None:
    if not ID_PATTERN.fullmatch(value):
        raise ReviewError(f"{label} is not a valid stable identifier")


def initialize(destination: Path) -> list[str]:
    source = Path(__file__).resolve().parents[1] / "templates" / "project"
    if destination.exists():
        if not destination.is_dir() or any(destination.iterdir()):
            raise ReviewError("initialization destination must be absent or an empty directory")
    destination.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ReviewError("initialization destination must not be a symbolic link")
    created: list[str] = []
    try:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            target = _inside(destination, destination / relative)
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                _atomic_bytes(target, path.read_bytes())
                created.append(relative.as_posix())
    except Exception:
        if not any(destination.iterdir()):
            destination.rmdir()
        raise
    return created


def _parse_delimited(path: Path, delimiter: str) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ReviewError("delimited import has no header")
        return [{str(key): _safe_cell(value) for key, value in row.items()} for row in reader]


def _parse_json_records(path: Path) -> list[dict[str, str]]:
    payload = _json(path)
    if isinstance(payload, dict):
        payload = payload.get("records")
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ReviewError("JSON import must be an array or an object with a records array")
    return [
        {str(key): _safe_cell(value) for key, value in item.items()}
        for item in payload
    ]


def _parse_ris(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, list[str]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        match = re.match(r"^([A-Z0-9]{2})  -(?: (.*))?$", line)
        if match is None:
            raise ReviewError("RIS import contains an unsupported line")
        tag, value = match.groups()
        value = value or ""
        if tag == "TY" and current:
            raise ReviewError("RIS record starts before the prior record ends")
        if tag == "ER":
            if not current.get("TY"):
                raise ReviewError("RIS record is missing TY")
            records.append(
                {
                    "title": _safe_cell((current.get("TI") or current.get("T1") or [""])[0]),
                    "authors": _safe_cell("; ".join(current.get("AU", []))),
                    "year": _safe_cell((current.get("PY") or current.get("Y1") or [""])[0][:4]),
                    "doi": _safe_cell((current.get("DO") or [""])[0]),
                    "external_id": _safe_cell((current.get("AN") or [""])[0]),
                    "record_type": _safe_cell(current["TY"][0]),
                }
            )
            current = defaultdict(list)
        else:
            current[tag].append(value)
    if current:
        raise ReviewError("RIS final record is missing ER")
    return records


def _parse_bibtex(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    entries = re.findall(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", text, flags=re.DOTALL)
    if not entries and text.strip():
        raise ReviewError("BibTeX import contains no supported entries")
    records: list[dict[str, str]] = []
    for entry_type, citekey, body in entries:
        fields = {
            key.lower(): value.strip().strip("{}\"")
            for key, value in re.findall(
                r"(?im)^\s*(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"),?\s*$",
                body,
            )
        }
        records.append(
            {
                "title": _safe_cell(fields.get("title", "")),
                "authors": _safe_cell(fields.get("author", "")),
                "year": _safe_cell(fields.get("year", "")),
                "doi": _safe_cell(fields.get("doi", "")),
                "external_id": _safe_cell(citekey),
                "record_type": _safe_cell(entry_type),
            }
        )
    return records


def parse_import(path: Path, format_name: str | None = None) -> tuple[str, list[dict[str, str]]]:
    selected = (format_name or path.suffix.lstrip(".")).lower()
    parsers = {
        "csv": lambda: _parse_delimited(path, ","),
        "tsv": lambda: _parse_delimited(path, "\t"),
        "json": lambda: _parse_json_records(path),
        "ris": lambda: _parse_ris(path),
        "bib": lambda: _parse_bibtex(path),
        "bibtex": lambda: _parse_bibtex(path),
    }
    if selected not in parsers:
        raise ReviewError("unsupported import format; use CSV, TSV, JSON, RIS, or BibTeX")
    records = parsers[selected]()
    if not records:
        raise ReviewError("import contains no records")
    return selected, records


def import_records(
    project: Path,
    source_path: Path,
    *,
    search_run_id: str,
    source_name: str,
    format_name: str | None = None,
) -> dict[str, Any]:
    _require_id(search_run_id, "search run ID")
    project = project_path(project)
    source_path = source_path.resolve()
    selected_format, parsed = parse_import(source_path, format_name)
    content = source_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    export_batch_id = _stable_id("export", search_run_id, digest)
    raw_name = f"{export_batch_id}.{selected_format if selected_format != 'bibtex' else 'bib'}"
    raw_relative = f"searches/raw-exports/{raw_name}"
    raw_target = _inside(project, project / raw_relative)
    if raw_target.exists() and raw_target.read_bytes() != content:
        raise ReviewError("existing raw export path has different bytes")

    records_path = project / "records" / "records.csv"
    manifest_path = project / "searches" / "raw-exports" / "manifest.csv"
    existing_records = _rows(records_path)
    manifest = _rows(manifest_path)
    normalized: list[dict[str, str]] = []
    for index, record in enumerate(parsed, start=1):
        source_record_id = _stable_id("record", export_batch_id, str(index))
        normalized.append(
            {
                "source_record_id": source_record_id,
                "search_run_id": search_run_id,
                "export_batch_id": export_batch_id,
                "source_name": source_name,
                "source_row": str(index),
                "title": _safe_cell(record.get("title") or record.get("Title") or ""),
                "authors": _safe_cell(record.get("authors") or record.get("author") or ""),
                "year": _safe_cell(record.get("year") or ""),
                "doi": _safe_cell(record.get("doi") or record.get("DOI") or "").lower(),
                "external_id": _safe_cell(record.get("external_id") or record.get("id") or ""),
                "record_type": _safe_cell(record.get("record_type") or record.get("type") or ""),
                "report_id": "",
                "status": "imported",
            }
        )
    manifest_entry = {
        "export_batch_id": export_batch_id,
        "search_run_id": search_run_id,
        "source_name": source_name,
        "interface": "",
        "strategy_file": "",
        "run_timestamp": "",
        "returned_count": "",
        "exported_count": str(len(normalized)),
        "limits": "",
        "relative_path": raw_relative,
        "format": selected_format,
        "bytes": str(len(content)),
        "sha256": digest,
        "importer_version": f"systematic-review-v{SCHEMA_VERSION}",
        "update_status": "initial",
    }

    raw_target.parent.mkdir(parents=True, exist_ok=True)
    if not raw_target.exists():
        _atomic_bytes(raw_target, content)
    _write_rows(records_path, list(normalized[0]), [*existing_records, *normalized])
    _write_rows(manifest_path, list(manifest_entry), [*manifest, manifest_entry])
    return {
        "export_batch_id": export_batch_id,
        "records_imported": len(normalized),
        "raw_export": raw_relative,
        "sha256": digest,
    }


def _normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def dedup_candidates(project: Path) -> list[dict[str, Any]]:
    records = _rows(project_path(project) / "records" / "records.csv")
    candidates: list[dict[str, Any]] = []
    for index, left in enumerate(records):
        for right in records[index + 1 :]:
            reasons: list[str] = []
            score = 0.0
            left_doi = left.get("doi", "").strip().lower()
            right_doi = right.get("doi", "").strip().lower()
            if left_doi and left_doi == right_doi:
                reasons.append("exact_doi")
                score = 1.0
            else:
                left_title = _normalized_text(left.get("title", ""))
                right_title = _normalized_text(right.get("title", ""))
                title_score = SequenceMatcher(None, left_title, right_title).ratio()
                same_year = bool(left.get("year")) and left.get("year") == right.get("year")
                left_author = _normalized_text(left.get("authors", "")).split(" ")[0]
                right_author = _normalized_text(right.get("authors", "")).split(" ")[0]
                same_author = bool(left_author) and left_author == right_author
                if title_score >= 0.92 and (same_year or same_author):
                    reasons.append("fuzzy_title_author_year")
                    score = round(title_score, 6)
            if reasons:
                candidates.append(
                    {
                        "candidate_id": _stable_id(
                            "candidate",
                            left["source_record_id"],
                            right["source_record_id"],
                        ),
                        "record_ids": sorted(
                            [left["source_record_id"], right["source_record_id"]]
                        ),
                        "reasons": reasons,
                        "score": score,
                        "action": "human_review_required",
                    }
                )
    return sorted(candidates, key=lambda item: item["candidate_id"])


def derive_counts(project: Path) -> dict[str, int]:
    project = project_path(project)
    records = _rows(project / "records" / "records.csv")
    reports = _rows(project / "records" / "reports.csv")
    studies = _rows(project / "records" / "studies.csv")
    full_text = _rows(project / "screening" / "full-text-decisions.csv")
    exclusions = _rows(project / "screening" / "excluded-full-text.csv")
    included_reports = {
        row["report_id"] for row in full_text if row.get("decision") == "include"
    }
    unavailable = {
        row["report_id"]
        for row in full_text
        if row.get("decision") == "awaiting_full_text"
    }
    included_studies = {
        row.get("study_id", "")
        for row in reports
        if row.get("report_id") in included_reports and row.get("study_id")
    }
    return {
        "source_records": len(records),
        "unique_reports": len(reports),
        "studies": len(studies),
        "reports_sought": len({row.get("report_id", "") for row in full_text if row.get("report_id")}),
        "reports_unavailable": len(unavailable),
        "reports_assessed": len(
            {
                row.get("report_id", "")
                for row in full_text
                if row.get("decision") not in {"", "awaiting_full_text"}
            }
        ),
        "full_text_exclusions": len({row.get("report_id", "") for row in exclusions}),
        "included_reports": len(included_reports),
        "included_studies": len(included_studies),
    }


def _validate_transitions(state: dict[str, Any], errors: list[str]) -> None:
    transitions = state.get("transitions", [])
    if not isinstance(transitions, list):
        errors.append("review-state transitions must be a list")
        return
    prior: str | None = None
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            errors.append(f"transition {index + 1} is not an object")
            continue
        old = transition.get("from")
        new = transition.get("to")
        if old not in REVIEW_STATES or new not in REVIEW_STATES:
            errors.append(f"transition {index + 1} uses an unknown state")
        elif (old, new) not in ALLOWED_TRANSITIONS:
            errors.append(f"invalid transition: {old} -> {new}")
        if prior is not None and old != prior:
            errors.append(f"transition {index + 1} does not continue prior state")
        if transition.get("actor_type") not in {
            "human",
            "ai_assistant",
            "automation_tool",
            "external_service",
        }:
            errors.append(f"transition {index + 1} has invalid actor type")
        for field in ("actor_id", "timestamp", "basis"):
            if not transition.get(field):
                errors.append(f"transition {index + 1} is missing {field}")
        prior = new if isinstance(new, str) else prior
    if transitions and prior != state.get("current_state"):
        errors.append("current state differs from the final transition")


def _human_gate(
    rows: list[dict[str, str]],
    *,
    identity_field: str,
    item_field: str,
    required: int,
) -> bool:
    by_item: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if (
            row.get("contributor_type") == "human"
            and row.get("independent") == "true"
            and row.get("qualified") == "true"
            and row.get(identity_field)
            and row.get(item_field)
        ):
            by_item[row[item_field]].add(row[identity_field])
    return bool(by_item) and all(len(reviewers) >= required for reviewers in by_item.values())


def validate_project(project: Path) -> dict[str, Any]:
    project = project_path(project)
    errors: list[str] = []
    blockers: list[str] = []
    for relative in sorted(REQUIRED_PATHS):
        path = project / relative
        if not path.is_file():
            errors.append(f"missing required artifact: {relative}")
        elif path.is_symlink():
            errors.append(f"required artifact must not be a symbolic link: {relative}")
    for directory in ("searches/search-strategies", "full-text", "metadata", "notes"):
        if not (project / directory).is_dir():
            errors.append(f"missing required directory: {directory}")
    if errors:
        return {"schema_version": SCHEMA_VERSION, "status": "blocked", "errors": errors, "blockers": []}

    protocol = _json(project / "protocol" / "protocol-state.json")
    state = _json(project / "audit" / "review-state.json")
    if protocol.get("schema_version") != SCHEMA_VERSION:
        errors.append("protocol state schema version is invalid")
    protocol_status = protocol.get("protocol_status")
    if protocol_status not in {
        "prospective_unregistered",
        "prospective_registered",
        "prospective_published",
        "amended",
        "retrospective_reconstructed",
    }:
        errors.append("protocol status is invalid")
    if protocol_status in {"prospective_registered", "prospective_published"}:
        evidence = protocol.get("registration_or_publication")
        if not isinstance(evidence, dict) or not all(
            evidence.get(field) for field in ("provider", "identifier", "url", "verified_at")
        ):
            errors.append("registered/published protocol lacks exact verification evidence")
    if protocol_status == "amended" and not _rows(
        project / "protocol" / "amendments.csv"
    ):
        errors.append("amended protocol lacks append-only amendment evidence")

    current_state = state.get("current_state")
    if current_state not in REVIEW_STATES:
        errors.append("review current state is invalid")
    _validate_transitions(state, errors)
    blockers.extend(
        str(value)
        for value in state.get("blockers", [])
        if isinstance(value, str) and value.strip()
    )

    manifest = _rows(project / "searches" / "raw-exports" / "manifest.csv")
    search_runs = _rows(project / "searches" / "search-run-ledger.csv")
    search_by_id = {row.get("search_run_id", ""): row for row in search_runs}
    batches: set[str] = set()
    for row in manifest:
        relative = row.get("relative_path", "")
        target = _inside(project, project / relative)
        if not target.is_file():
            errors.append(f"raw export is missing: {relative}")
            continue
        content = target.read_bytes()
        if str(len(content)) != row.get("bytes") or hashlib.sha256(content).hexdigest() != row.get("sha256"):
            errors.append(f"raw export hash/size drift: {relative}")
        batches.add(row.get("export_batch_id", ""))
        search = search_by_id.get(row.get("search_run_id", ""))
        if search is None:
            blockers.append(
                f"raw export lacks search-run ledger: {row.get('export_batch_id', '')}"
            )
        elif current_state == "complete":
            for field in (
                "source_name",
                "interface",
                "strategy_file",
                "run_timestamp",
                "returned_count",
                "exported_count",
                "update_status",
            ):
                if not row.get(field) or not search.get(field):
                    blockers.append(
                        f"complete search evidence lacks {field}: "
                        f"{row.get('search_run_id', '')}"
                    )
            strategy_file = search.get("strategy_file", "")
            if strategy_file and not _inside(project, project / strategy_file).is_file():
                blockers.append(
                    f"exact search strategy file is missing: "
                    f"{row.get('search_run_id', '')}"
                )

    records = _rows(project / "records" / "records.csv")
    reports = _rows(project / "records" / "reports.csv")
    studies = _rows(project / "records" / "studies.csv")
    record_ids = {row.get("source_record_id", "") for row in records}
    report_ids = {row.get("report_id", "") for row in reports}
    study_ids = {row.get("study_id", "") for row in studies}
    if "" in record_ids | report_ids | study_ids:
        errors.append("record/report/study identity is missing")
    if len(record_ids) != len(records) or len(report_ids) != len(reports) or len(study_ids) != len(studies):
        errors.append("record/report/study IDs must be unique")
    for row in records:
        if row.get("export_batch_id") not in batches:
            errors.append(f"record has missing export lineage: {row.get('source_record_id', '')}")
        if row.get("report_id") and row.get("report_id") not in report_ids:
            errors.append(f"record links to unknown report: {row.get('source_record_id', '')}")
    for row in reports:
        if row.get("study_id") and row.get("study_id") not in study_ids:
            errors.append(f"report links to unknown study: {row.get('report_id', '')}")
    records_by_batch: dict[str, int] = defaultdict(int)
    for row in records:
        records_by_batch[row.get("export_batch_id", "")] += 1
    for row in manifest:
        exported_count = row.get("exported_count", "")
        if exported_count.isdigit() and int(exported_count) != records_by_batch.get(
            row.get("export_batch_id", ""), 0
        ):
            errors.append(
                f"export count differs from normalized record lineage: "
                f"{row.get('export_batch_id', '')}"
            )

    identity_links = _rows(project / "records" / "identity-links.csv")
    for row in identity_links:
        if row.get("source_record_id") not in record_ids:
            errors.append("identity link references an unknown source record")
        if row.get("report_id") not in report_ids:
            errors.append("identity link references an unknown report")
        if row.get("study_id") and row.get("study_id") not in study_ids:
            errors.append("identity link references an unknown study")

    dedup = _rows(project / "dedup" / "dedup-decisions.csv")
    active_candidates: set[str] = set()
    decision_ids = {row.get("decision_id", "") for row in dedup}
    for row in dedup:
        if row.get("decision") not in {"merge", "do_not_merge", "split", "unmerge"}:
            errors.append("dedup decision uses an invalid action")
        if row.get("reviewer_type") != "human":
            blockers.append("dedup decision lacks a real human reviewer")
        if row.get("decision") in {"split", "unmerge"} and row.get(
            "prior_decision_id"
        ) not in decision_ids:
            errors.append("reversal decision lacks valid prior lineage")
        if row.get("active") == "true":
            candidate = row.get("candidate_id", "")
            if candidate in active_candidates:
                errors.append("dedup candidate has multiple active decisions")
            active_candidates.add(candidate)

    for relative in (
        "screening/conflicts.csv",
        "extraction/conflicts.csv",
    ):
        if any(row.get("status") not in {"resolved", "not_applicable"} for row in _rows(project / relative)):
            blockers.append(f"unresolved conflicts in {relative}")

    appraisal = _rows(project / "appraisal" / "appraisal-decisions.csv")
    design_by_study = {
        row.get("study_id", ""): row.get("study_design", "") for row in studies
    }
    if any(row.get("universal_quality_score", "").strip() for row in appraisal):
        errors.append("unsupported universal quality score is present")
    if any(
        not all(row.get(field) for field in ("instrument", "instrument_version", "domain", "judgment", "support", "source_locator"))
        for row in appraisal
    ):
        blockers.append("appraisal decisions lack instrument-specific support")
    if any(
        row.get("study_id") in design_by_study
        and row.get("study_design") != design_by_study[row.get("study_id", "")]
        for row in appraisal
    ):
        errors.append("appraisal study design differs from the study identity ledger")

    synthesis = _rows(project / "synthesis" / "synthesis-data.csv")
    for row in synthesis:
        if row.get("pooling_compatible") == "false" and row.get("method") == "meta_analysis":
            errors.append("meta-analysis is recorded for incompatible evidence")
        if row.get("external_statistics") == "true" and not all(
            row.get(field)
            for field in (
                "tool",
                "tool_version",
                "code_reference",
                "input_sha256",
                "output_sha256",
                "run_environment",
                "human_verifier_id",
            )
        ):
            blockers.append("external statistics lack complete provenance and human verification")
        if row.get("method") == "no_meta_analysis" and not row.get("explicit_method"):
            blockers.append("synthesis without meta-analysis lacks an explicit method")

    if state.get("certainty_applicable") is True:
        certainty = project / "certainty" / "certainty-decisions.csv"
        if not certainty.is_file() or not _rows(certainty):
            blockers.append("applicable certainty decisions are missing")
        elif any(
            not all(row.get(field) for field in ("framework", "outcome_or_finding", "judgment", "reasons", "human_decision_maker_id"))
            for row in _rows(certainty)
        ):
            blockers.append("certainty decisions are incomplete")

    full_text = _rows(project / "screening" / "full-text-decisions.csv")
    included_report_ids = {
        row.get("report_id", "") for row in full_text if row.get("decision") == "include"
    }
    report_by_id = {row.get("report_id", ""): row for row in reports}
    for report_id in sorted(included_report_ids):
        report = report_by_id.get(report_id)
        if report is None:
            errors.append(f"included decision references unknown report: {report_id}")
            continue
        full_text_path = report.get("full_text_path", "")
        if not all(
            report.get(field)
            for field in (
                "full_text_path",
                "full_text_bytes",
                "full_text_sha256",
                "metadata_path",
                "notes_path",
                "retrieval_version",
            )
        ):
            blockers.append(
                f"included report lacks verified evidence lineage: {report_id}"
            )
            continue
        full_text_file = _inside(project, project / full_text_path)
        if not full_text_file.is_file():
            blockers.append(f"included full text is missing: {report_id}")
        else:
            full_text_bytes = full_text_file.read_bytes()
            if (
                str(len(full_text_bytes)) != report.get("full_text_bytes")
                or hashlib.sha256(full_text_bytes).hexdigest()
                != report.get("full_text_sha256")
            ):
                errors.append(f"included full-text hash/size drift: {report_id}")
        for field in ("metadata_path", "notes_path"):
            evidence_file = _inside(project, project / report[field])
            if not evidence_file.is_file():
                blockers.append(f"included report lacks {field}: {report_id}")
    required_reviewers = int(state.get("required_independent_humans", 1))
    if required_reviewers > 1 and not _human_gate(
        full_text,
        identity_field="contributor_id",
        item_field="report_id",
        required=required_reviewers,
    ):
        blockers.append("required independent qualified human full-text decisions are absent")
    if any(row.get("contributor_type") != "human" and row.get("independent") == "true" for row in full_text):
        errors.append("non-human contributor is marked independent")

    extraction = _rows(project / "extraction" / "extraction-values.csv")
    if state.get("require_duplicate_extraction") is True and not _human_gate(
        extraction,
        identity_field="contributor_id",
        item_field="data_item_key",
        required=2,
    ):
        blockers.append("required independent duplicate extraction is absent")

    expected_counts = derive_counts(project)
    stored_counts = _json(project / "reporting" / "flow-counts.json")
    if stored_counts != expected_counts:
        errors.append("stored flow counts drift from authoritative ledgers")

    combined_reporting = "\n".join(
        (project / relative).read_text(encoding="utf-8")
        for relative in (
            "reporting/review-report.md",
            "reporting/limitations-and-deviations.md",
            "reporting/applicable-checklist.md",
        )
    ).lower()
    for marker in ("search currency", "automation", "funding", "conflict", "limitation", "deviation"):
        if marker not in combined_reporting:
            blockers.append(f"final reporting omits {marker}")

    if current_state == "complete":
        unresolved = []
        for relative in REQUIRED_PATHS:
            if Path(relative).suffix in {".md", ".json", ".csv", ".txt"}:
                text = (project / relative).read_text(encoding="utf-8", errors="replace")
                if re.search(r"\[(?:TBD|UNRESOLVED|UNKNOWN)\]", text, re.IGNORECASE):
                    unresolved.append(relative)
        if unresolved:
            blockers.append("complete state conceals unresolved markers")

    blockers = sorted(set(blockers))
    errors = sorted(set(errors))
    if errors:
        status = "blocked"
    elif blockers or current_state == "blocked":
        status = "blocked"
    elif current_state == "complete":
        status = "complete"
    else:
        status = "incomplete"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "review_id": state.get("review_id", ""),
        "current_state": current_state,
        "errors": errors,
        "blockers": blockers,
        "counts": expected_counts,
    }


def redacted_summary(project: Path) -> dict[str, Any]:
    result = validate_project(project)
    return {
        "schema_version": result["schema_version"],
        "review_id": result.get("review_id", ""),
        "status": result["status"],
        "current_state": result.get("current_state", ""),
        "error_count": len(result["errors"]),
        "blockers": result["blockers"],
        "counts": result.get("counts", {}),
    }


def _print(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("project")
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("project")
    import_parser.add_argument("source")
    import_parser.add_argument("--search-run-id", required=True)
    import_parser.add_argument("--source-name", "--source", dest="source_name", required=True)
    import_parser.add_argument("--format", choices=("csv", "tsv", "json", "ris", "bib", "bibtex"))
    for command in ("dedup-candidates", "counts", "validate", "summary"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("project")
        if command == "validate":
            command_parser.add_argument("--require-final", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "init":
            _print({"created": initialize(project_path(arguments.project))})
        elif arguments.command == "import":
            _print(
                import_records(
                    project_path(arguments.project),
                    Path(arguments.source),
                    search_run_id=arguments.search_run_id,
                    source_name=arguments.source_name,
                    format_name=arguments.format,
                )
            )
        elif arguments.command == "dedup-candidates":
            _print(dedup_candidates(project_path(arguments.project)))
        elif arguments.command == "counts":
            _print(derive_counts(project_path(arguments.project)))
        elif arguments.command == "validate":
            result = validate_project(project_path(arguments.project))
            _print(result)
            if arguments.require_final and result["status"] != "complete":
                return 2
            if result["errors"]:
                return 1
        else:
            _print(redacted_summary(project_path(arguments.project)))
    except (OSError, ReviewError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
