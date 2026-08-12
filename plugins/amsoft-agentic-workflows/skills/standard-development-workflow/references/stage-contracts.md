# Stage contracts and approval gates

## Gate owner

These stage descriptions default to an ordinary human-gated task. When and only
when Agent Orchestration has authoritatively verified an active schema-v6
register for the same project/control-plane identity with
`decision_policy=autopilot`, one trusted authority envelope replaces repeated
human approval waits for ordinary in-goal delivery. Record only material choices,
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

When risk, ambiguity, repository policy, or a durable handoff warrants it, create or refine the
GitHub issue using `spec-ready.md` and post one canonical implementation plan comment. Include
`<!-- amsoft-standard-development-plan -->`, pin the comment, read it back, and retain its comment
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
- failure modes, edge cases, security, privacy, accessibility, performance, localization,
  observability, data integrity, and rollback where applicable;
- documentation and release-note changes;
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

In ordinary mode, present material choices for approval. In verified autopilot, resolve them from
the trusted goal and continue. Blocking unknowns remain visible.

## Stage 3 — Approved implementation and local verification

Implement only after Stage 2 approval. At implementation start, read back and reconcile the
canonical pinned plan. Update that same comment regularly when material findings change status,
assumptions, decisions, risks, sequencing, or requirements-to-tests mappings. Keep the issue and
plan synchronized; mark the comment `reapproval_required` and re-open Stage 2 for scope or
architecture changes.

Run the fail-fast ladder while developing, then the complete planned local suite. Preserve and
classify first failures before changing code or tests. Isolate suite state, reuse only identity-bound
immutable artifacts, and checkpoint long operations when applicable. Exercise the live local stack
for user-visible or integration behavior. Capture proportionate rehearsal evidence without secrets.
Compare the final diff against the issue, plan, expected envelope, repository policy, and
unrelated-file boundary.

Do not open the review gate with failing or unknown required tests, unexplained skipped coverage,
an unapproved scope expansion, a weaker verification substitute, or stale operation/artifact state.

## Stage 4 — Draft pull request review

Freeze the committed candidate and finalize evidence before pushing the feature branch. Validate
the final record with `--require-final`. Open a draft PR linked with issue-closing keywords when
appropriate.
The PR description must state what changed, why, scope/non-goals, design decisions, test commands
and results, manual evidence, screenshots or videos for visual changes, risks, migrations,
deployment and rollback notes, and remaining limitations.

Re-check remote checks and findings. In ordinary mode, present the PR for review. In verified
autopilot, continue using the repository's required review plus proportionate independent review
for high-risk or complex changes. Address findings, re-run affected tests, and update evidence.

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

On explicit PR approval in ordinary mode, or merge readiness in verified autopilot:

1. Confirm the target PR, base/head revisions, review state, required checks, unresolved threads,
   mergeability, repository policy, final evidence identity, and required verification channels.
2. Mark the draft ready when required for merging.
3. Squash-merge by default. Use another strategy only when the user explicitly asks or repository
   policy makes squash unavailable; report the deviation before acting when a choice is needed.
4. Fast-forward the clean canonical checkout from its configured remote and base branch. Preserve
   unrelated files. Verify the canonical HEAD equals the merged revision.
5. Perform the targeted cleanup in `verification-deployment-cleanup.md`.
6. In verified autopilot, continue to the declared deployment target without a routine pause.

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
