# ADR-0010: Approve interactive SDLC plans and refresh stale review attempts

- Status: accepted
- Date: 2026-11-04
- Owner: Project maintainer and implementing agent within task authority
- Evidence: Maintainer approval of plan version 1 through the Codex interactive plan on 4 November 2026. [Tracking issue](https://github.com/WilsonLe/agentic-workflows/issues/91) and [preflight evidence](https://github.com/WilsonLe/agentic-workflows/issues/57#issuecomment-6617846200).
- Supersedes: 0005
- Superseded by: none

## Context

Planning and design had distinct stages, but an initial implementation request
could satisfy approval before the user saw the plan. An unrelated base change
also consumed the same review budget as a round of fixes for review findings.
The maintainer tested a plan with expandable detail and confirmed approval
through the chat interaction.

## Decision

Add a plan approval gate between design and implementation. The portable
Interactive Plan skill owns how to present, discuss, revise, and track a plan.
SDLC owns the gate and retains the issue, plan, and optional task record as
sources of authority. Use a short executive view and engineering details on
demand. Native controls send a user decision through the trusted conversation.
Use chat and plan checkboxes where the host lacks those controls. Bind approval
to the material plan contents and retain it through progress updates. Verified
autopilot may record a plan decision when the user delegated that authority for
the scope.

Keep the two-pass limit on review and remediation. Schedule the final pass
after known fixes, cheap checks, and a base refresh. With merge authority,
finish required full validation first where practical. When proven unrelated
work changes the candidate, retain the previous attempt and obtain fresh
independent review within its pass. The coordination register links the new
attempt to the archived prior review and attribution evidence. Changes made to
address findings after pass two still require a further decision. Exact current
base and head, reviewer independence, findings disposition, the coverage map,
and the self-contained final chat handoff carry forward from ADR-0005.

## Alternatives

A checklist alone would leave users unable to ask questions, revise the plan,
or make a versioned decision through its controls. A separate plan store would
duplicate issue and task-record authority. Counting every reviewer launch
would continue to block after unrelated work lands. Reusing stale clearance
would lose evidence for the combined candidate.

## Consequences

Plan approval is a visible milestone before source work. Existing task and
coordination records remain readable. A review refresh requires proven
attribution and a fresh independent result, even when remediation has exhausted
its budget. The agent still reconciles the actual plan, decision source, and
candidate provenance. Structural validation verifies their recorded identities
and relationships.

## Revisit

Revisit if user feedback repeatedly fails to reach the plan owner, if plan
version changes cause redundant approval prompts, or if unrelated changes
repeatedly invalidate a review before the authorized transition.
