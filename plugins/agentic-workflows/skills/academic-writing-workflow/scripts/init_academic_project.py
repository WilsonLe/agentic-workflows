#!/usr/bin/env python3
"""Initialize a gated academic-writing project without overwriting files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


STAGES = {
    "01-execution-plan": ["execution-plan.md", "REVIEW.md"],
    "02-high-level-outline": [
        "high-level-outline.md",
        "research-plan.md",
        "assumptions-and-gaps.md",
        "REVIEW.md",
    ],
    "03-research": ["paper-index.md", "integration-note.md", "REVIEW.md"],
    "04-detailed-outline": ["detailed-outline.md", "REVIEW.md"],
    "05-first-draft": ["first-draft.md", "issues.md", "REVIEW.md"],
    "06-final": ["final.md", "source-audit.md", "unresolved-items.md"],
}


def review_template() -> str:
    return """# Review

Status: pending
Approved by:
Approved at:
Decision evidence:
Requested changes:
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--target-words", type=int, required=True)
    parser.add_argument("--citation-style", required=True)
    args = parser.parse_args()

    if args.target_words <= 0:
        parser.error("--target-words must be positive")

    root = args.project_dir.expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        parser.error(f"refusing to initialize non-empty directory: {root}")
    root.mkdir(parents=True, exist_ok=True)

    task_sheet = root / "00-task-sheet"
    task_sheet.mkdir()
    (task_sheet / "source-manifest.md").write_text(
        "# Task Sheet Source Manifest\n", encoding="utf-8"
    )
    for stage, files in STAGES.items():
        stage_dir = root / stage
        stage_dir.mkdir()
        for name in files:
            content = review_template() if name == "REVIEW.md" else f"# {name[:-3].replace('-', ' ').title()}\n"
            (stage_dir / name).write_text(content, encoding="utf-8")

    research = root / "03-research"
    for subdir in ("papers", "metadata", "notes"):
        (research / subdir).mkdir()

    state = {
        "schema_version": 2,
        "title": args.title,
        "target_words": args.target_words,
        "citation_style": args.citation_style,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "current_stage": "01-execution-plan",
        "stages": {
            stage: {"status": "pending", "approved_at": None, "decision_evidence": None}
            for stage in STAGES
        },
    }
    (root / "workflow-state.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
