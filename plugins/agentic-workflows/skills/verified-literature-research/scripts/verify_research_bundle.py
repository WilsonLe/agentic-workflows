#!/usr/bin/env python3
"""Validate the local evidence and note structure for a research bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


METADATA_FIELDS = {
    "id",
    "title",
    "authors",
    "source_url",
    "retrieved_at",
    "sha256",
    "bytes",
    "version",
    "verification_sources",
}

NOTE_HEADINGS = {
    "## Bibliographic record",
    "## Selection rationale",
    "## Research design and context",
    "## Findings with locators",
    "## Limitations and boundary conditions",
    "## Claims this paper can support",
    "## Claims this paper cannot support",
    "## Integration into the outline",
    "## Quality record",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("research_dir", type=Path)
    args = parser.parse_args()

    root = args.research_dir.expanduser().resolve()
    papers = root / "papers"
    metadata_dir = root / "metadata"
    notes = root / "notes"
    errors: list[str] = []

    for required in (papers, metadata_dir, notes):
        if not required.is_dir():
            fail(errors, f"missing directory: {required}")
    for required in (root / "paper-index.md", root / "integration-note.md"):
        if not required.is_file() or required.stat().st_size == 0:
            fail(errors, f"missing or empty file: {required}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    metadata_files = sorted(metadata_dir.glob("*.json"))
    if not metadata_files:
        fail(errors, "no metadata JSON files found")

    for metadata_path in metadata_files:
        try:
            record = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"{metadata_path.name}: invalid JSON: {exc}")
            continue

        missing = sorted(METADATA_FIELDS - record.keys())
        if missing:
            fail(errors, f"{metadata_path.name}: missing fields {', '.join(missing)}")
            continue

        research_id = str(record["id"])
        if metadata_path.stem != research_id:
            fail(errors, f"{metadata_path.name}: id must match filename stem")

        if not isinstance(record["authors"], list) or not record["authors"]:
            fail(errors, f"{research_id}: authors must be a non-empty list")
        sources = record["verification_sources"]
        if not isinstance(sources, list) or len(set(map(str, sources))) < 2:
            fail(errors, f"{research_id}: fewer than two verification sources")

        pdf = papers / f"{research_id}.pdf"
        if not pdf.is_file():
            fail(errors, f"{research_id}: missing PDF {pdf.name}")
        else:
            with pdf.open("rb") as handle:
                if handle.read(5) != b"%PDF-":
                    fail(errors, f"{research_id}: file is not a PDF")
            actual_bytes = pdf.stat().st_size
            if actual_bytes != record["bytes"]:
                fail(errors, f"{research_id}: byte size does not match metadata")
            actual_hash = sha256(pdf)
            if actual_hash.lower() != str(record["sha256"]).lower():
                fail(errors, f"{research_id}: SHA-256 does not match metadata")

        note = notes / f"{research_id}.md"
        if not note.is_file():
            fail(errors, f"{research_id}: missing note {note.name}")
        else:
            content = note.read_text(encoding="utf-8")
            for heading in sorted(NOTE_HEADINGS):
                if heading not in content:
                    fail(errors, f"{research_id}: note missing heading {heading}")
            if research_id not in content:
                fail(errors, f"{research_id}: note does not mention research ID")

    pdf_stems = {path.stem for path in papers.glob("*.pdf")}
    metadata_stems = {path.stem for path in metadata_files}
    note_stems = {path.stem for path in notes.glob("*.md")}
    if pdf_stems != metadata_stems:
        fail(errors, "PDF and metadata identifiers do not match exactly")
    if note_stems != metadata_stems:
        fail(errors, "note and metadata identifiers do not match exactly")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"\n{len(errors)} validation error(s)")
        return 1

    print(f"PASS: verified {len(metadata_files)} paper bundle(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
