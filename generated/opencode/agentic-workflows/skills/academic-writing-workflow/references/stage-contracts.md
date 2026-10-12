# Stage contracts

## Required workspace

```text
academic-project/
├── workflow-state.json
├── 00-task-sheet/
│   └── source-manifest.md
├── 01-execution-plan/
│   ├── execution-plan.md
│   └── REVIEW.md
├── 02-high-level-outline/
│   ├── high-level-outline.md
│   ├── research-plan.md
│   ├── assumptions-and-gaps.md
│   └── REVIEW.md
├── 03-research/
│   ├── papers/
│   ├── metadata/
│   ├── notes/
│   ├── paper-index.md
│   ├── integration-note.md
│   ├── validation-report.txt
│   └── REVIEW.md
├── 04-detailed-outline/
│   ├── detailed-outline.md
│   └── REVIEW.md
├── 05-first-draft/
│   ├── first-draft.md
│   ├── issues.md
│   └── REVIEW.md
└── 06-final/
    ├── final.md
    ├── source-audit.md
    └── unresolved-items.md
```

Keep the original task sheet and user-supplied material read-only.

## Approval record

Each `REVIEW.md` must contain:

```markdown
# Review

Status: pending
Approved by:
Approved at:
Decision evidence:
Requested changes:
```

Use `approved` only after an explicit user statement approving that stage. Quote or accurately summarize the approval in `Decision evidence`. A request to continue counts only when it clearly refers to the current stage.

## Stage 1 acceptance: execution plan

- The plan is a complete handoff artifact, not a short proposal or chat summary.
- It faithfully reconstructs every operative task-sheet requirement and clearly distinguishes quoted requirements, confirmed interpretations, assumptions, and unresolved questions.
- It inventories supplied inputs with durable identifiers or locations and explains what each input contributes.
- It contains the proposed thesis direction, provisional high-level outline, section word budget, and rubric or requirement coverage.
- It specifies the research questions, query families, databases, source targets, screening and quality rules, download and verification procedure, full-paper reading method, research-note contract, integration method, and saturation rule.
- It lists all workflow stages, outputs, approval gates, tools or skills, validation checks, risks, dependencies, student-owned inputs, and definition of done.
- It includes fresh-session startup instructions that do not rely on this conversation or hidden context.
- Its task-sheet coverage matrix shows where every requirement will be fulfilled and how final compliance will be checked.
- A fresh agent could execute the task from the plan without guessing any material requirement. Any remaining material uncertainty is a visible blocker or approval item.

## Stage 2 acceptance: high-level outline

- The outline answers the actual task verbs and rubric.
- Section word counts add to the required total; state whether references, tables, and appendices count.
- The thesis is a direction to test, not a finding invented before research.
- The plan includes search strings, databases, source types, inclusion/exclusion criteria, date scope, quality tests, and a saturation rule.
- Student-owned evidence and unresolved constraints are visible.

## Stage 3 acceptance: research

- Every retained paper has a PDF, metadata record, and research note.
- The exact paper version read is recorded.
- Metadata is checked against at least two scholarly sources where possible.
- Each note distinguishes the authors' claims from the researcher's interpretation.
- Findings have page, figure, table, or section locators.
- Limitations and unsafe-to-cite claims are recorded.
- The integration note maps sources to outline sections and identifies disagreements, weak coverage, and gaps.
- The bundle validator passes or all exceptions are explained.

## Stage 4 acceptance: detailed outline

- Every paragraph group has a purpose, evidence plan, citations, and word allocation.
- Planned citations point to verified research notes.
- The outline includes counterarguments, limitations, transitions, and rubric coverage.
- Student-owned material remains clearly marked.

## Stage 5 acceptance: first draft

- The draft follows the approved detailed outline or explains deviations.
- Material claims have supporting citations.
- No citation is used beyond what the underlying paper supports.
- No invented data, results, reflection, interviews, screenshots, or tool output appears.
- Word count and citation style are checked.
- The issues list is candid and actionable.

## Stage 6 acceptance: final version

- User feedback is resolved or listed as unresolved.
- The argument is coherent across the whole document.
- Citations, quotations, page locators, bibliography entries, and source audit agree.
- Required AI-use or authorship declarations remain truthful.
- There are no hidden placeholders or unsupported claims.
- The requested output format has been inspected, not merely generated.

## Reopening a stage

When a user changes the thesis, scope, evidence standard, or approved structure:

1. Mark the affected stage `reopened`.
2. Mark all downstream stages `stale`.
3. Revise and seek approval again.
4. Do not silently patch the final draft around a changed foundation.
