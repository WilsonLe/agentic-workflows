---
name: engineering-review
description: Review a software diff against its originating request and repository standards, then summarize findings, evidence, and merge risk for a PR handoff.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering review

Use this skill for a branch, PR, or working diff review. It is an analysis method, not merge authority. Keep the repository's independent-review and exact-candidate requirements when they apply.
When invoked by the Standard Development Workflow after draft PR creation, act as
the read-only reviewer for its single automatic cycle using the caller-provided
review contract (the Standard Development Workflow is Codex-only).
Return findings to the implementing agent; do not edit the candidate, spawn another
reviewer, or schedule a second pass. A standalone review request retains its own scope.

## Review method

Find defects and unmet requirements that matter to users or maintainers. A useful
review explains a reachable failure and its consequence, not just a preferred way
to write the code. Read [what to look for](references/review-checklist.md) on every
review, select its applicable sections, and use its concrete probes. Repository
policy takes precedence over this generic method.

1. **Establish the candidate and scope.** Pin base and head SHAs, confirm both
   resolve, and capture the commit list, changed files, and full diff, including
   deletions. For Git, use `git diff --name-status <base> <head>` and
   `git diff <base> <head> -- <path>`. Verify whether the intended comparison is the
   PR merge base or another explicit base; do not silently choose. Read the request,
   every linked implementation issue, acceptance criteria, and local instructions.
   Treat PR descriptions and code comments as claims to verify. If requirements or
   the base are missing, state that limitation instead of inventing them.
2. **Map the behavior before judging details.** For each acceptance criterion, locate
   its implementation and evidence or record the gap. Identify entry points, changed
   contracts, callers, consumers, state owners, and external effects. Search for
   usages and read surrounding functions and relevant unchanged code. Read every
   human-authored changed hunk; check generated files against their source and
   generator. Prioritize authorization, destructive writes, migrations, shared APIs,
   and concurrent state. Prioritization is not permission to silently skip files.
3. **Trace concrete scenarios.** Follow a normal operation from input through
   validation, authorization, computation, persistence, and response. Then trace
   applicable boundaries and failures from the checklist: missing input, wrong owner,
   repeated request, partial write, timeout, stale result, and old consumer. For each
   plausible defect, identify the input or event order that reaches it and the
   invariant it violates. Follow guards and framework behavior before concluding
   that a check is missing. Verify unfamiliar API behavior against the installed
   version or official documentation; do not guess from its name.
4. **Review on two independent axes.** Keep **requested behavior** (missing, partial,
   incorrect, or unrequested behavior tied to a requirement) distinct from
   **engineering quality** (correctness, safety, compatibility, and concrete
   maintainability defects). Passing style checks cannot establish either axis.
   Distinguish a newly introduced defect from a pre-existing problem; report an
   existing problem as a PR finding only when this change makes it newly reachable
   or materially worse, explaining that connection.
5. **Challenge the tests and your own finding.** Inspect whether assertions observe
   the promised behavior and would fail for the suspected defect. Check fixtures,
   mocks, skips, and changed expectations; a green suite can exercise the wrong path.
   Run the smallest relevant safe check when practical. Use a synthetic counterexample
   or a specific control/data-flow proof when execution is unavailable. Seek evidence
   that disproves your concern: upstream validation, transaction guarantees, caller
   constraints, or an existing test. Do not alter the candidate, real customer data,
   or external services to prove a finding. Record which checks you ran and which
   evidence came from the author; do not imply you reran their suite.
6. **Report and finish.** Deduplicate findings by root cause, order required fixes by
   severity, and give each the smallest useful file/line range. Report review coverage,
   skipped or unavailable checks, documentation impact, and remaining risk. Re-read
   the candidate identity before finishing; head or base drift makes the report
   historical, not evidence for the new candidate. Follow the caller's review-cycle
   budget; this method never requests another pass or authorizes merge or deployment.

## Finding standard

Publish a required finding only when you can state all of these:

- **Where and what:** the changed line or relevant deletion, plus the broken behavior
  or repository rule. Anchor on the cause, not an arbitrary downstream symptom.
- **Trigger:** a concrete supported input, user role, configuration, or event sequence.
  Name conditional assumptions and verify that they are possible in this repository.
- **Consequence and evidence:** the observed or logically demonstrated result, its
  impact, and the violated requirement or invariant. Cite callers/tests when needed.
- **Correction:** the smallest feasible direction that restores the contract, and a
  focused verification scenario. Do not demand a speculative redesign.

If a crucial premise is unverified, label it an open question or verification gap,
not a confirmed defect. Static proof can be sufficient; a reproduction is helpful
but not mandatory. Avoid generic warnings, duplicate lint output, unrelated cleanup,
and unsupported performance claims. Missing tests alone are not a defect without a
specific uncovered risk or an explicit repository testing requirement.

Use the repository's severity scale if defined. Otherwise use:

| Priority | Meaning | How to justify it |
| --- | --- | --- |
| P0 | Critical; immediate stop | Demonstrated catastrophic loss, broad compromise, or complete outage on an unavoidable path; do not infer this from hypothetical conditions. |
| P1 | High; fix before merge | Reachable security/data-integrity failure or broken essential flow with substantial impact; state affected users and conditions. |
| P2 | Normal; actionable fix | A concrete defect under supported conditions with bounded impact, or a required contract/policy violation. |
| P3 | Low; minor defect | A demonstrated low-impact issue; keep optional taste or style suggestions separately labeled non-blocking. |

Severity describes impact and reachability, not how certain you sound. Explain the
reason for blocking under repository policy; a priority label is not merge authority.
Write about the code respectfully, explain why the change matters, and distinguish
required corrections from optional suggestions. Prefer a few substantiated findings
over filling a quota. If none qualify, explicitly say **no actionable findings**;
that does not prove the software has no defects.

## Review output

Use the repository's review format when one exists. Otherwise return:

1. **Candidate and coverage:** base/head, request/issues, inspected surfaces, and
   applicable checklist areas. List exclusions with reasons.
2. **Findings:** `[P1] Short action-oriented title` followed by file/line, axis,
   trigger, consequence, evidence, and correction. Separate optional suggestions and
   open questions from required findings. Say when either review axis has no findings.
3. **Verification and limits:** exact checks/results, author-supplied evidence,
   unavailable runtime or integration paths, and candidate drift if any.
4. **Handoff:** documentation-impact result, residual risks, and relevant rollback
   constraints. Do not claim approval, merged status, or deployed behavior from review.

For a UI change, inspect an available render or interaction when visual behavior is
part of the requirement; state when only source was inspected. Include a small flow
map only when it helps explain the findings. See the checklist's worked examples for
the level of precision expected in comments.
