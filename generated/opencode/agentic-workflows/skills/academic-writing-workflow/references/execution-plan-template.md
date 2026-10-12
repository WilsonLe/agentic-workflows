# Context-complete execution plan template

Write this plan for a competent agent who starts in a new session with no access to the original conversation. The plan must carry the task context, execution decisions, safeguards, and acceptance criteria forward by itself.

Do not replace substantive content with “see task sheet,” “as discussed,” or another reference to missing context. Preserve the original task sheet separately, but restate every operative requirement here.

```markdown
# Academic writing execution plan

## 1. Control block

- Project title:
- Plan version:
- Status: pending review
- Prepared at:
- Target deliverable:
- Target word count:
- Citation style:
- Due date and timezone:
- Original task-sheet source(s):
- Source version, date, or checksum:
- Approved by:
- Approval evidence:

## 2. Task-sheet reconstruction

### Exact task or question

[Quote the core task when permitted, then provide a faithful operational restatement.]

### Required actions

| Task verb or requirement | Operational meaning | Planned output | Final verification |
|---|---|---|---|

### Purpose, audience, scope, and exclusions

- Purpose:
- Intended audience:
- Required scope:
- Explicit exclusions:
- Discipline or module context:

### Learning outcomes and marking rubric

| Learning outcome or rubric criterion | Weight | What strong performance requires | Where it will be addressed | Evidence of completion |
|---|---:|---|---|---|

### Deliverable and formatting constraints

- Deliverable type:
- Required sections:
- Word-count inclusions and exclusions:
- Formatting:
- File format:
- Tables, figures, appendices, or evidence requirements:
- Submission rules:

### Source and citation constraints

- Minimum or expected source count:
- Permitted source types:
- Peer-review or recency requirements:
- Required readings:
- Citation and bibliography style:

### Academic-integrity and AI-use constraints

- Permitted assistance:
- Prohibited assistance:
- Required declaration:
- Student-owned reasoning or evidence:

## 3. Input and evidence inventory

| Input | Durable path, link, or identifier | What it contains | How it will be used | Availability to a fresh session |
|---|---|---|---|---|

List missing inputs separately. Do not invent their contents.

## 4. Proposed argument and high-level outline

### Provisional thesis or analytical direction

[State a direction to test through research, not an unresearched conclusion.]

### Proposed structure and word budget

| Section | Purpose | Main questions or claims | Expected evidence | Rubric coverage | Words |
|---|---|---|---|---|---:|

- Total planned words:
- Buffer or contingency:
- Rebalancing rule:

## 5. Research blueprint

### Research questions

1.

### Concepts, synonyms, and query families

| Concept | Synonyms or related terms | Example query families | Why needed |
|---|---|---|---|

### Search locations

| Database, repository, or source | Coverage sought | Search method | Access constraint |
|---|---|---|---|

### Evidence targets

| Outline need | Preferred evidence | Approximate source target | Quality threshold |
|---|---|---:|---|

### Screening and quality rules

- Inclusion criteria:
- Exclusion criteria:
- Date range:
- Discipline or population limits:
- Peer-review preference:
- Retraction and withdrawal checks:
- Preprint versus published-version rule:

### Verification, download, and reading procedure

1. Verify metadata in at least two scholarly sources where possible.
2. Download and retain the exact PDF version.
3. Record identifiers, retrieval URL, timestamp, byte size, and SHA-256.
4. Read the full paper, including relevant tables, figures, appendices, and limitations.
5. Create one page- or section-located research note per retained paper.
6. Record supported claims, unsupported claims, limitations, and outline relevance.
7. Validate the bundle before review.

### Synthesis and stopping rule

- Central integration-note structure:
- Counterevidence and disagreement handling:
- Gap-filling rounds:
- Search saturation threshold:
- Conditions that require additional research:

## 6. Execution stages and review gates

| Stage | Work | Required artifacts | Validation | Approval needed to continue |
|---|---|---|---|---|
| 1 | Context-complete execution plan | This plan and review record | Handoff-completeness test | Yes |
| 2 | High-level outline and research plan | Outline, research plan, gaps register | Word budget and rubric coverage | Yes |
| 3 | Verified research | PDFs, metadata, notes, index, integration note | Research-bundle validator | Yes |
| 4 | Detailed outline | Paragraph-level outline | Claim-source and word-budget audit | Yes |
| 5 | First draft | Draft and issues list | Citation, rubric, integrity, and humanization audit | Yes |
| 6 | Final version | Final document, source audit, unresolved items | Whole-document and rendered-output verification | Complete |

## 7. Tools, skills, and operating procedure

- Academic workflow skill:
- Paper-search and citation skills:
- PDF extraction or OCR:
- Humanizer:
- Document-generation or rendering tools:
- Required file locations:
- Fallbacks when a tool is unavailable:

Never claim a skill or tool was used unless it was actually loaded or run.

## 8. Assumption and decision register

| Item | Confirmed fact, assumption, or unresolved question | Proposed safe default | Effect if wrong | User decision required |
|---|---|---|---|---|

## 9. Risks and mitigations

| Risk | Likelihood or trigger | Impact | Mitigation | Escalation point |
|---|---|---|---|---|

Include source scarcity, access limits, ambiguous rubric wording, word-budget pressure, unavailable student evidence, extraction failures, contradictory research, and AI-policy restrictions where relevant.

## 10. Definition of done

- [ ] Every task-sheet requirement is represented in the coverage matrix.
- [ ] Every material claim is traceable to verified evidence or clearly marked as student reasoning.
- [ ] All required student-owned material is supplied or remains visibly unresolved.
- [ ] Word count, structure, citation style, rubric, formatting, and submission rules pass.
- [ ] The final artifact has been inspected in its delivery format.
- [ ] AI-use and authorship declarations are truthful.
- [ ] No fabricated citation, data, result, quotation, experience, or analysis remains.

## 11. Fresh-session startup instructions

1. Read this plan completely before acting.
2. Confirm that Stage 1 is explicitly approved.
3. Treat this plan as the portable execution brief. Do not rely on unseen chat history.
4. Inspect listed inputs when available. If an input is unavailable, use only the description recorded here and do not invent missing content.
5. Start at the first unapproved stage in `workflow-state.json`, or Stage 2 when only this approved plan is supplied.
6. Reproduce all later review gates. Do not interpret plan approval as approval of later artifacts.
7. Stop and ask when an unresolved item would materially change compliance with the task sheet.

Suggested fresh-session request:

> Execute the attached approved academic writing plan from its first uncompleted stage. Treat the plan as the complete handoff context, preserve every review gate, and do not assume access to the earlier task sheet conversation.

## 12. Task-sheet coverage matrix

| Requirement | Plan section | Delivery stage and artifact | Final verification method | Status |
|---|---|---|---|---|

## 13. Review request

Please either:

1. explicitly approve this execution plan;
2. request named changes; or
3. answer the blocking questions below.

Blocking questions:

- [List only questions whose answers materially affect compliance or approach.]
```

## Handoff-completeness test

Before presenting the plan, verify:

- A new agent can state the assignment, audience, output, word count, rubric, citation rules, source expectations, integrity limits, and deadline from the plan alone.
- A new agent knows what files or links exist, what each contains, and which may be unavailable.
- A new agent knows the proposed argument, structure, research method, stage sequence, validations, and approval gates.
- A new agent can identify every assumption, blocker, student-owned input, and definition-of-done check.
- No material instruction depends on “the conversation above.”

If any answer is no, revise the plan before requesting approval.
