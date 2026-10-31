---
name: engineering-review
description: Use when reviewing a software diff or PR; adversarially challenge correctness against the request and affected contracts, then report actionable findings, evidence, and review limits.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Engineering review

Adversarially review a branch, PR, or working diff: actively try to disprove
correctness and find material failures across the full change and affected contracts.
Use risk-appropriate depth, including acceptance requirements, surrounding call sites,
integrations, edge cases, invalid inputs, failure/recovery paths, regressions,
security/data handling, concurrency/state ownership where relevant, and meaningful
test gaps. Complete coverage of relevant changes; explicitly record unreviewed areas
and limits rather than claiming exhaustive proof. Adversarial means skeptical and
evidence-seeking, not hostile or a quota of defects.
Keep independent-review and exact-candidate requirements. This method grants no
merge authority. In the Codex Standard Development Workflow's single automatic cycle,
use the caller's bounded contract as a read-only reviewer: return findings without
editing, spawning another reviewer, or scheduling another pass. When called to
re-review after material fixes, review the final changed state and affected contracts,
using prior findings/dispositions and verification without assuming earlier clearance.
Standalone reviews retain their requested scope. The delivery owner evaluates and
addresses findings; the reviewer supplies independent evidence.

## Review method

Read [the review checklist](references/review-checklist.md) every time and apply its
relevant probes. Repository policy takes precedence. Find reachable failures and
unmet requirements, not preferred coding styles.

1. **Pin scope.** Resolve base/head SHAs, comparison basis (PR merge base or explicit
   base), commits, and full diff including deletions. Read the originating request,
   every linked implementation issue, acceptance criteria, and local instructions.
   PR descriptions/comments are claims to verify; name missing requirements or base.
2. **Map behavior.** Locate implementation and evidence for each criterion. Trace
   entry points, contracts, callers, consumers, state owners, and external effects.
   Read surrounding code and every human-authored changed hunk; verify generated
   changes against source/generator. Prioritize high-impact boundaries without
   silently skipping other files. Apply the checklist's existing-abstraction-first
   method to responsibility, dependencies, and schemas.
3. **Trace scenarios.** Follow input through validation, authorization, computation,
   persistence, and response; then relevant failure/event-order cases from the
   checklist. Identify a supported trigger and violated invariant. Check guards,
   callers, and installed framework behavior before claiming a defect; verify
   unfamiliar APIs from installed code or official docs.
4. **Separate axes.** Assess **requested behavior** (missing, partial, incorrect, or
   unrequested outcome) separately from **engineering quality** (correctness, safety,
   compatibility, concrete maintainability costs). Style checks prove neither.
   Report pre-existing problems as PR defects only when the change makes them
   newly reachable or materially worse, explaining how.
5. **Challenge evidence.** Check independent expected values, fixtures, mocks, skips,
   and changed assertions: would the suspected wrong behavior fail the test? Run
   the smallest safe check or give a synthetic counterexample/control-flow proof.
   Seek disproof in upstream validation, transactions, caller constraints, and tests.
   Do not edit the candidate, customer data, or external services. Separate reviewer
   checks from author-supplied evidence.
6. **Finish.** Deduplicate by cause, order by severity, and anchor precise file/lines.
   Report coverage, gaps, documentation impact, and risk. Review and passing tests
   are distinct evidence. Re-read base/head: drift makes review historical; bind the
   result to the final candidate actually inspected. Respect the caller's cycle budget; do not initiate
   another review or infer approval, merge, or deployment.

## Findings and severity

A required finding needs a changed cause or relevant deletion, a verified supported
trigger, its consequence and violated contract, evidence, and a smallest feasible
correction with focused verification. Static proof may suffice. An unverified premise
is an open question or evidence gap. Omit generic warnings, duplicate lint, taste,
unrelated cleanup, and unsupported performance claims. Missing tests need a concrete
uncovered risk or an explicit repository requirement to qualify.

Use repository severity, otherwise:

| Priority | Required evidence |
| --- | --- |
| P0 — stop | Demonstrated catastrophic loss, broad compromise, or complete outage on an unavoidable path; hypothetical conditions do not suffice. |
| P1 — before merge | Reachable security/data-integrity failure or broken essential flow with substantial impact; state affected users and conditions. |
| P2 — actionable | Supported concrete defect with bounded impact, or required contract/policy violation. |
| P3 — minor | Demonstrated low-impact defect; label optional style/taste suggestions separately. |

Severity reflects impact and reachability, not confidence or merge authority. Explain
blocking rationale under repository policy. Write respectfully; prefer substantiated
findings over quotas. Say **no actionable findings** when none qualify, without
claiming defect-free software.

## Output

Use repository format, otherwise return:

1. Candidate, request/issues, inspected surfaces/checklist areas, and exclusions
   with reasons.
2. Findings: `[P1] Action-oriented title`, file/line, axis, trigger, consequence,
   evidence, correction. Separate optional suggestions and open questions; state
   when either axis has no findings.
3. Exact reviewer checks/results, author evidence, unavailable paths, and any drift.
4. Documentation impact, residual risks, and rollback constraints. No approval or
   merged/deployed claim follows from review.

Inspect a render/interaction for visual requirements when available; otherwise
state source-only coverage. Add a small flow map only when useful. The checklist's
worked examples show comment precision and restraint.
