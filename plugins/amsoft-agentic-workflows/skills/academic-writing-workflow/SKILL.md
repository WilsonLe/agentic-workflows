---
name: academic-writing-workflow
description: Run gated, evidence-first academic writing from a task sheet and onboard users to the Academic Writing workflow. Use for setup or first-run guidance, essays, reports, literature reviews, and coursework that must begin with a context-complete execution plan for fresh-session handoff, then progress through an outline, research notes, detailed outline, first draft, and final version with explicit user review between phases.
---

# Academic Writing Workflow

Turn a task sheet into a traceable academic deliverable. Keep the user's argument, evidence, analysis, and institutional obligations visible at every phase.

For setup, onboarding, or first-use requests, read
[references/onboarding.md](references/onboarding.md), guide the user through it, and stop at the
onboarding boundary unless the user explicitly asks to begin Stage 1.

Read these references before starting:

- [references/stage-contracts.md](references/stage-contracts.md) for deliverables and approval rules.
- [references/execution-plan-template.md](references/execution-plan-template.md) for the mandatory fresh-session handoff plan.
- [references/humanization-and-integrity.md](references/humanization-and-integrity.md) for the mandatory prose and integrity pass.

Use the sibling `verified-literature-research` skill during Stage 3. In Hermes, also load the exact built-ins named in that skill.

## Start or resume

1. Locate and read the complete task sheet, rubric, submission instructions, supplied sources, and any existing work.
2. Determine the institution's AI-use rules before drafting. If AI-authored prose is prohibited, limit work to the permitted scope and tell the user.
3. Create a project workspace with `scripts/init_academic_project.py`, or reproduce its structure if scripts cannot run.
4. Read `workflow-state.json` and all approval records before resuming.
5. Never infer approval from silence, a request for status, or edits that do not explicitly approve the current gate.
6. If resuming from an approved execution plan in a fresh session, treat that plan as the portable working brief. Do not assume access to the earlier conversation. Cross-check the original task sheet when it is available, but do not block solely because it is absent if the approved plan passes the handoff-completeness test.

## Stage 1: Context-complete execution plan

Create `01-execution-plan/execution-plan.md` immediately after reading the task sheet. Follow the execution-plan template. Make the document exhaustive enough that a capable agent in a new session can complete the assignment without access to this conversation or unstated background.

The plan must reproduce or faithfully restate every operative task-sheet requirement, including:

- the exact task or question, action verbs, scope, audience, purpose, deliverable type, learning outcomes, rubric, required sections, and exclusions;
- the word-count rule and a proposed section budget;
- citation style, source requirements, formatting, submission format, deadline, and AI-use or integrity rules;
- supplied inputs and how to locate or identify them;
- required student-owned evidence, reflection, data, screenshots, experiments, or analysis;
- a proposed thesis direction and provisional high-level outline;
- a meticulous research blueprint, including questions, query families, databases, source targets, screening rules, verification, PDF retention, full-paper reading, note production, integration, and stopping criteria;
- every planned stage, artifact, review gate, validation check, risk, assumption, blocker, and definition of done;
- fresh-session startup instructions and a task-sheet coverage matrix.

Do not hide ambiguity behind an assumption. Put each uncertainty in the assumption and decision register, state its effect, propose a safe default, and mark whether user approval is required.

Run the humanization and integrity pass. Present only the completed plan, its blocking questions, and the explicit approval request. Stop. Do not create the formal high-level outline or conduct research until the plan is explicitly approved.

## Stage 2: High-level outline and research plan

Start only after explicit Stage 1 approval.

Use the approved plan as the source of execution context. Create:

- `02-high-level-outline/high-level-outline.md`: thesis direction, major sections, purpose of each section, rubric coverage, and section word counts that add to the target;
- `02-high-level-outline/research-plan.md`: research questions, search concepts and synonyms, databases, query families, date/discipline limits, inclusion and exclusion rules, evidence targets, verification method, and stopping criteria;
- `02-high-level-outline/assumptions-and-gaps.md`: confirmed facts, unresolved items, and student inputs still needed.

Explain and record every deviation from the approved execution plan. Run the humanization and integrity pass. Present this stage for review and stop.

## Stage 3: Verified literature research

Start only after explicit Stage 2 approval.

Load and follow `verified-literature-research`. Search broadly, then deepen from seed papers, citations, terminology, disagreements, and missing evidence. For every retained paper:

- download the exact PDF version;
- verify metadata in at least two independent scholarly sources when possible;
- retain the PDF, metadata, hash, and retrieval record;
- read the paper, not only its abstract;
- create one research note with page or section locators;
- record limitations and claims the source cannot support.

Create `integration-note.md` to map the paper notes into the high-level outline, including tensions, gaps, and sections that lack adequate support.

Run the research-bundle validator and the humanization and integrity pass. Present all notes plus the integration note for review and stop.

## Stage 4: Detailed outline

Start only after explicit Stage 3 approval.

Create `04-detailed-outline/detailed-outline.md`. Keep it an outline, not draft prose. For every planned paragraph or coherent paragraph group, specify:

- the point or claim;
- the reasoning and evidence to discuss;
- the paper note(s) to cite and why;
- any contrast, limitation, or transition;
- the approximate word allocation;
- student-owned evidence still required.

Use only verified sources from Stage 3 unless the user approves new research. Run the humanization and integrity pass. Present the outline for review and stop.

## Stage 5: First draft

Start only after explicit Stage 4 approval.

Draft from the approved detailed outline and verified notes. Cite the source that supports each claim. Do not cite a paper for a claim that appears only in another paper's summary of it unless clearly using a secondary citation.

Preserve `[STUDENT INPUT REQUIRED]`, `[EVIDENCE REQUIRED]`, or `[CITATION NEEDED]` markers rather than inventing content. Run claim-to-source, word-count, citation, rubric, and humanization checks. Present the first draft and an issues list for review, then stop.

## Stage 6: Final version

Start only after explicit Stage 5 approval.

Resolve the user's feedback, update the evidence map, and run a whole-document pass for argument flow, terminology, repetition, citation accuracy, rubric coverage, formatting, and word count. Apply the humanization skill without changing facts, quotations, data, citations, or required disclosures.

Deliver:

- the final version in the requested format;
- a source audit mapping material claims to verified notes;
- a short unresolved-items list, if anything still requires the user.

Do not call work final while placeholders, fabricated evidence, unverified citations, or material rubric gaps remain.

## State and approval rules

- Record only explicit approval in `workflow-state.json` and the stage's `REVIEW.md`.
- If the user requests changes, keep the stage pending until the revised artifact is explicitly approved.
- Later feedback may reopen an earlier stage. Mark downstream artifacts stale and update them only after the reopened stage is approved.
- Never overwrite source task sheets, supplied papers, or prior approved artifacts. Create a revised file or preserve version history.
- Treat approval of the execution plan as approval of the documented approach and safe defaults, not permission to invent missing facts or skip later gates.

## Humanization requirement

Before releasing every stage:

1. Load the installed Humanizer skill when available: `humanizer:humanizer` in Codex or `humanizer` in Hermes.
2. Apply it to explanations, outlines, notes, and drafts.
3. Preserve academic precision and the user's voice.
4. Record which humanizer was used. If none is available, use the fallback checklist in `references/humanization-and-integrity.md` and say so.

Humanization improves clarity and voice. It must never be used to evade academic-integrity rules, conceal prohibited AI authorship, or alter evidence.

## Included script

Initialize a safe workspace:

```bash
python scripts/init_academic_project.py PROJECT_DIR \
  --title "Assessment title" \
  --target-words 2500 \
  --citation-style "Harvard"
```

The script refuses to initialize a non-empty directory.
