# Stage contracts and approval gates

## Gate owner

These stage descriptions default to an ordinary human-gated task. When and only
when Agent Orchestration has authoritatively verified an active schema-v6
register for the same project/control-plane identity with
`decision_policy=autopilot`, one trusted authority envelope replaces repeated
human approval waits for ordinary in-goal delivery. Ordinary planning and implementation gates
can already be satisfied by the user's explicit task request or a prior exact authorization; they
do not require a new prompt at every stage. Record only material choices,
exceptions, merge, deployment, and terminal disposition; routine phases inherit
the activation decision.

This substitution never changes the declared goal or grants credentials,
external authority, destructive scope, weaker verification, self-review, a
third review pass, branch-protection bypass, or unsafe cleanup. Without the
verified register, all ordinary human gates below remain mandatory.

## Stage 1 — Isolated worktree ready

Deliver evidence of the feature branch and base revision, worktree path, instructions read,
prerequisites installed, environment-file presence and ignore safety, unique runtime identity,
non-overlapping port map, and local stack health when the task needs a running stack. Also identify
the repository capability-profile digest or the sections that were refreshed, required
verification-channel availability, and resource-budget applicability.

Do not continue if onboarding is incomplete.

## Stage 2 — Spec-ready issue and exhaustive plan

Every SDLC request requires at least one live tracking issue before implementation. Reuse or
create it with a concise scope and acceptance note; issue creation is never conditional on
repository habits or change size. Follow [delivery tracking](delivery-tracking.md).
When risk, ambiguity, repository policy, or a durable handoff warrants the full specification,
refine the tracking issue using `spec-ready.md` and post one canonical implementation plan comment.
Include
`<!-- standard-development-plan -->`, pin the comment, read it back, and retain its comment
ID and URL. Update this same comment in place; do not create competing plan comments.

The plan must include:

- objective, issue link, scope, non-goals, assumptions, and blocking decisions;
- repository findings and exact change surfaces;
- proposed architecture, data flow, interfaces, contracts, compatibility, and migration approach;
- consumed capability-profile identity, task execution contract, minimal correct path, expected
  change envelope, and material-expansion triggers;
- resource capacity/ownership, validation ladder, verification-channel claims, and conditional
  sandbox/artifact/operation requirements;
- file-by-file or component-by-component changes and their sequencing;
- for a pattern-wide request, discovered surface IDs, inclusion/exclusion reasons, shared points,
  and each included surface's planned verification;
- failure modes, edge cases, security, privacy, accessibility, performance, localization,
  observability, data integrity, and rollback where applicable;
- likely documentation, agent-instruction, and release-note consumers of the change, or a
  provisional reason no update appears warranted; revisit this after implementation;
- exact dependency and generated-artifact handling;
- a requirements-to-tests matrix mapping every acceptance criterion to planned automated and/or
  manual evidence;
- unit, integration, end-to-end, regression, manual, visual, browser/device, accessibility,
  performance, security, migration, and failure-path tests as applicable;
- test data, fixtures, mocks, environment, commands, URLs, port map, expected assertions, and
  evidence artifacts;
- CI parity and required checks;
- for UI changes, the complete request-image inventory and exported-PNG sketch inventory, with
  one-to-one issue-body image evidence and any upload blockers;
- draft PR structure, review evidence, merge readiness criteria, cleanup steps, staging deployment
  method, staging endpoint substitutions, and staging rollback;
- risks, mitigations, unresolved questions, and a precise definition of done.

In ordinary mode, a clear implementation request authorizes the routine plan and local execution.
Resolve implementation details from repository evidence and established user choices. Present only
unresolved material choices that change behavior, security, data handling, cost, or external impact,
or a plan the user explicitly asked to approve. In verified autopilot, resolve them from the
trusted goal and continue. Blocking unknowns remain visible.

## Stage 3 — Authorized implementation and local verification

Implement when the user's request or a later plan approval authorizes this scope. An issue-first,
plan-only, prototype-first, or stop-before-coding request still needs its reserved decision. At
implementation start, read back and reconcile any canonical pinned plan. Update that same comment
when material findings change status,
assumptions, decisions, risks, sequencing, or requirements-to-tests mappings. Keep the issue and
plan synchronized; mark the comment `reapproval_required` and re-open Stage 2 for material scope or
architecture changes that exceed existing authority.

Run only the focused portion of the fail-fast ladder while developing and preparing a draft PR.
Select tests for changed behavior and affected consumers, plus relevant static and generated
checks; record commands, selection reasons, and full-suite coverage deferred to Stage 5. Preserve and
classify first failures before changing code or tests. Isolate suite state, reuse only identity-bound
immutable artifacts, and checkpoint long operations when applicable. Exercise the live local stack
for user-visible or integration behavior. Capture proportionate rehearsal evidence without secrets.
Compare the final diff against the issue, plan, expected envelope, repository policy, and
unrelated-file boundary.
For a pattern-wide request, reconcile every discovered surface with final proof; for a runtime
defect, retain the correlated failing operation or the precise missing-trace limitation.
Compare the implemented behavior and review findings with the relevant user and agent guidance.
Update warranted instructions and maintained mirrors in the same candidate, or record why no
update is warranted. Follow [documentation impact](documentation-impact.md) for the decision.

Do not open the review gate with failing or unknown required focused tests, unexplained skipped coverage,
an unapproved scope expansion, a weaker verification substitute, stale operation/artifact state,
or known stale required guidance.

## Stage 4 — Draft pull request review

Freeze the committed candidate and finalize evidence before pushing the feature branch. Validate
the candidate evidence, then open a draft PR with at least one tracking issue. Read back every
issue–PR pair in both directions and validate the record with `--require-final` before handoff.
Every completed request has at least one issue and one PR; each delivered issue and every PR
needs at least one link. Use closing keywords only when this PR finishes the whole issue; use
`Refs` for partial delivery and ordinary references for dependencies or separate follow-up work.
The PR description must state what changed, why, scope/non-goals, design decisions, test commands
and results, manual evidence, screenshots or videos for visual changes, risks, migrations,
deployment and rollback notes, remaining limitations, and the documentation-impact result:
updated surfaces with applicable validation, or a concise reason no update was warranted.

Re-check remote checks and findings. In ordinary mode, automatically invoke the bundled
`engineering-review` skill once after opening the draft PR, address actionable feedback,
and revalidate before handoff. Follow [single draft-PR review](single-draft-pr-review.md)
for reviewer independence, candidate identity, resume behavior, and the stop condition.
The revised head does not trigger another automatic review. In verified
autopilot, continue using the repository's required review plus proportionate independent review
for high-risk or complex changes. Address findings, re-run affected tests, and update evidence.

The ordinary automatic cycle runs once only. The following ceiling applies to further
explicitly requested review or a verified control plane's own policy, not an automatic
second pass in ordinary mode.
Use at most two review-and-address passes before deciding the next workflow step. One pass consists
of review feedback on a stable candidate, disposition or authorized addressing of that feedback,
affected revalidation, and an updated evidence handoff. After pass 1, the revised candidate may be
presented for pass 2. Pass 2 is final: if the applicable review and evidence gates are clear, move
to the next authorized step; otherwise stop and report unresolved findings, candidate identity,
validation state, and residual risk for an explicit user decision.

Do not request or start pass 3 automatically.

Never interpret the cap as permission to dismiss feedback, weaken checks, merge, deploy, or bypass
another approval or safety gate.

## Stage 5 — Approval, squash merge, synchronization, and cleanup

On an explicit request to merge the branch/PR in ordinary mode, or the merge stage in verified
autopilot, use the [branch approval rule](../SKILL.md#approval-and-evidence-boundaries).
Approval authorizes in-scope fixes on that branch; a later commit alone does not require reapproval.
Approval and passing merge evidence are separate gates:

1. Run the full repository-required test suite and local CI on the merge candidate. If checks
   fail, diagnose and fix within the approved scope, commit/push, rerun affected checks and the
   full suite, and update PR evidence. Continue using the existing branch approval; reopen a
   decision only for a material scope/target change or an explicitly commit-limited approval.
   Confirm the target PR, base/head revisions, review state, required checks, unresolved threads,
   mergeability, repository policy, final evidence identity, and required verification channels.
   Split and track any unfinished implementation before merging a PR that completes an issue.
   Before that merge, apply [deployment-triggering merge readiness](merge-deployment-readiness.md).
   Verify changed target prerequisites or safe inactivity; a caveat after an auto-deploy is too late.
2. Mark the draft ready when required for merging.
3. Squash-merge by default. Use another strategy only when the user explicitly asks or repository
   policy makes squash unavailable; report the deviation before acting when a choice is needed.
4. Read back the PR's merged state and merge commit. For each implementation issue fully delivered by
   this PR, first verify all required linked PRs have merged and its acceptance criteria are met.
   Then check its live state, close it if still open even when the PR used `Refs`, and verify
   it is closed. Do not close dependency, parent, or follow-up issues merely because they were
   mentioned.
   Keep unverified deployment and field-evaluation work explicit without holding a merged
   implementation issue open for it.
5. Fast-forward the clean canonical checkout from its configured remote and base branch. Preserve
   unrelated files. Verify the canonical HEAD equals the merged revision.
6. Perform the targeted cleanup in `verification-deployment-cleanup.md`.
7. In verified autopilot, continue to the declared deployment target without a routine pause.

## Stage 6 — Declared-target deployment

In ordinary mode, deploy only after explicit approval. In verified autopilot, deploy the
synchronized merged revision to the target declared by the trusted goal; a direct “deploy”
instruction may use the repository's single unambiguous documented target. Follow the real runbook
and verify deployment identity before testing. Production must be directly named by the operator.

Repeat the applicable local verification matrix against staging, replacing local URLs, ports,
credentials, callbacks, storage, and environment assumptions with staging equivalents. Do not
claim parity for checks that cannot safely run in staging; explain the substitute evidence.

Report deployment revision, target endpoints, automated and manual results, observable evidence,
and rollback readiness. Never infer production authority from staging.
When reporting availability, read the active runtime revision and mode, then check the exact
target URL and relevant user flow. A completed deployment job alone is not live availability.
