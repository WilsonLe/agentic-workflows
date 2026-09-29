---
name: session-reflection
description: Review past Codex sessions across projects, find recurring workflow improvements, and deduplicate tracking issues against live GitHub work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Codex session history** — Use a host that can list and read the relevant sessions; report unavailable hosts.
- **Required: GitHub CLI** — Authenticate gh with read access to the target issue repository; issue write access is needed only when requested.

<!-- catalog-prerequisites:end -->

# Session reflection

Use when the user asks to learn from past sessions or create workflow improvement trackers. This is a retrospective review, not an automatic background monitor. Read [review-contract.md](references/review-contract.md) before reviewing. Use [dedup-evaluations.md](examples/dedup-evaluations.md) to check difficult dispositions. Use [reflection_state.py](scripts/reflection_state.py) for a compact local coverage ledger; GitHub remains authoritative.

## Run

1. Set a bounded date window, projects, target issue repository, and requested finding count from the user. If omitted, choose a small recent window and disclose it. Confirm read access; issue writing is authorized only when requested.
2. Inventory session history through the host's list/read APIs, including pagination, archives, and connected hosts where available. Record stable session IDs, project, dates, and complete/unavailable coverage. Do not infer history from titles alone. Use memory only as a locator.
   Check the current session `updatedAt` against the local complete-coverage ledger with
   `reflection_state.py session-check <id> --source-updated-at <updatedAt>`. Skip a full
   trace only on an exact match; still refresh live GitHub state. A partial, unavailable,
   or changed session must be read.
   Project each fetched page to bounded user corrections, final outcomes, turn IDs, cursors,
   and failure markers **before printing it to the model**. Do not emit whole command/tool
   arrays for first-pass triage. If the host result is captured as JSON in a private local
   file, run `python3 <skill-root>/scripts/session_evidence.py triage <page.json>
   --requested-cursor <cursor>`; use
   `python3 <skill-root>/scripts/session_evidence.py detail <page.json> --item-id <id>` only for causal
   evidence that a candidate needs. The helper
   is an output filter, not an alternative history source. Record unread and truncated pages.
   After all pages are read, record complete coverage with the same source `updatedAt`;
   do not mark partial coverage complete to gain a skip on the next run.
3. Group repeated observations into workflow candidates. Keep user corrections, failed work, rework, verification cost, and outcomes as evidence. Exclude one-off product bugs and unsupported speculation. Rank by impact, recurrence, and breadth; state uncertainty.
4. For each target repository, page through **all open and closed issues and in-flight PRs once** with the authenticated GitHub API. Include body, state, labels, update time, and links in the working index. Search synonyms within that index, then read likely matches live. Compare the problem, cause, proposed change, and acceptance criteria; title similarity is only a lead. Classify as `covered by open work`, `already delivered`, `regression of prior work`, `partially covered`, `new`, or `uncertain`.
   Keep the full index for comparison but print only counts and likely matches; do not dump
   unrelated bodies. Reopen likely matches and make a fresh live pre-write check.
5. Consult the local ledger for already reviewed session IDs and candidate-to-issue links. Reuse it to avoid rescanning unchanged history, but refresh live GitHub state. Treat #121–#126 as known examples of existing workflow trackers, not fresh proposals. For partial coverage, isolate the missing scope. For a closed issue, inspect delivered work before calling it a regression.
6. If issue writing is authorized, make a fresh live search/read just before every write to catch races. Add useful new evidence to an existing tracker when appropriate; only create a new issue for genuinely uncovered scope. Include a redacted evidence summary, mechanism, implementation plan, measurable acceptance criteria, and related links. Read the created or updated issue back. Do not place raw transcripts, secrets, credentials, or unrelated private project facts in GitHub.
7. Report the window, projects, session counts, gaps, ranked candidates, dispositions, actions, links, and uncertainty. Never silently edit skill code, memory, or project work as a result of reflection.

If the host cannot expose session history or GitHub state, report the gap and stop the affected action. Do not claim that a cached index proves current coverage.
