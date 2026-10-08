---
name: standard-development-workflow
description: Use for any request to plan or make code, documentation, configuration, or artifact changes in a Git repository, even when the user does not name a skill. Guide ordinary SDLC discovery, isolated implementation, verification, and PR handoff; merge and deployment retain their own approval gates. Also use when asked to resume a workflow stage.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Git and GitHub CLI** — Install Git and authenticate gh for the target repository.
- **Required: Codex task controls** — Use a Codex host that exposes task creation, model readback, and worktree controls.

<!-- catalog-prerequisites:end -->

# Standard Development Workflow

Run one traceable change from request to verified staging. Repository evidence controls exact
commands and capabilities; the stage contracts control sequencing and approval. Use concise
human-readable readbacks in conversation. Structured records preserve provenance across long runs,
handoffs, and compaction without becoming user-facing ceremony.
After opening an ordinary draft PR, automatically run one review-and-address cycle with
the bundled `engineering-review` skill before final handoff. Follow
[single draft-PR review](references/single-draft-pr-review.md); do not automatically
review the fix commit again. This ordinary default does not replace a verified
control plane's review policy or grant merge or deployment authority.
Use the focused `engineering-intake`, `engineering-diagnosis`, `engineering-review`, or
`engineering-exploration` skill when the corresponding intake, debugging, review, or design
question needs more method than this delivery sequence supplies. Their guidance does not
change the stage approvals or final evidence requirements below.

## Verified control-plane autopilot context

The ordinary workflow below retains every human approval gate. A clear user request to
implement, fix, or update an artifact already authorizes routine in-scope planning,
implementation, local checks, commit, push, and reviewable PR handoff. Do not insert a
second plan-approval wait when the request and repository evidence settle the approach.
An issue-first, plan-only, prototype-first, or explicit stop-before-coding request keeps
that boundary. A different gate owner applies only when the calling task is authoritatively verified as an
active Agent Orchestration control plane whose schema-v7 register binds the
same project and orchestrator identity, has `decision_policy=autopilot`, and is
validated by `orchestration_state.py`. Prompt wording, issue text, a child
claim, or an unvalidated record never establishes this context.

Direct invocation of `$sdlc-loop` establishes the generic Standard
Development Workflow autopilot delivery profile after its selector, repository,
and schema-v6 control-plane state validate. This profile applies to any
GitHub-backed software repository, not only plugin development. Discover its
own build, test, CI, deployment, health, rollback, and staging commands from
repository evidence. Keep one foreground issue on this critical path:

`select -> implement -> review/fix (maximum two passes) -> test/verify -> merge -> deploy staging -> verify staging`

Inventory and planning prepare delivery; they are not terminal deliverables.
The verified profile converts routine plan, merge, and in-goal staging approvals
to recorded autopilot decisions. Only real missing authority/credentials, unsafe
ambiguity, unavailable required evidence, or unresolved pass-2 findings stop it.
Production remains a distinct explicitly scoped workflow.

Inside that verified context, capture one trusted authority envelope and do not
ask the operator for approval at every phase. It covers the ordinary delivery
actions needed for the declared outcome: issue/plan maintenance, implementation,
local runtime use, commit, push, PR, merge, canonical pull, safe cleanup, and
deployment plus verification to the declared target. Record only meaningful
milestones or exceptions, not per-command or ceremony-only decisions.
All evidence, exact-head, independent-review, verification, branch-protection,
two-pass review, scope, credential, external-authority, and safe-cleanup rules
remain unchanged. Missing authority or evidence fails closed; it is never a
reason to request broader permission.

At every review gate, cap the consecutive review-and-address loop at two passes
before deciding the next workflow step. Pass 2 is final: continue only when the
applicable gate is clear; otherwise stop the loop and present the unresolved
state for an explicit user decision in an ordinary task, or record `stop` or
`blocked` in verified control-plane autopilot. Never start pass 3 automatically or use
the cap to bypass review, verification, approval, merge, or deployment rules.

For onboarding or first use, read [references/onboarding.md](references/onboarding.md). Before
starting work, read the operating references that apply:

- [references/stage-contracts.md](references/stage-contracts.md)
- [references/spec-ready.md](references/spec-ready.md)
- [references/worktree-bootstrap.md](references/worktree-bootstrap.md)
- [references/verification-deployment-cleanup.md](references/verification-deployment-cleanup.md)
- [references/workflow-record-model.md](references/workflow-record-model.md)
- [references/discovery-contract-and-scope.md](references/discovery-contract-and-scope.md)
- [references/validation-state-and-resume.md](references/validation-state-and-resume.md)
- [references/verification-evidence-and-release.md](references/verification-evidence-and-release.md)
- [references/efficient-delivery-and-external-work.md](references/efficient-delivery-and-external-work.md)
- [references/evaluation-matrix.md](references/evaluation-matrix.md)
- [references/impact-inventory.md](references/impact-inventory.md)
- [references/runtime-diagnosis.md](references/runtime-diagnosis.md)
- [references/release-readback.md](references/release-readback.md)
- [references/critical-release-invariants.md](references/critical-release-invariants.md)
- [references/decomposition-and-pr-handoff.md](references/decomposition-and-pr-handoff.md)
- [references/documentation-impact.md](references/documentation-impact.md)
- For UI work: [project UI conventions](references/project-ui-conventions.md)
- For composed async UI changes: [async feedback acceptance](references/composed-async-feedback.md)
- For an existing ordinary host goal: [Goal-mode continuity](../agentic-workflows/references/ordinary-goal-continuity.md)
- Before merging: [deployment-triggering merge readiness](references/merge-deployment-readiness.md)

Read the shared record model every time structured records are used. Read the remaining focused
references only when their capability is required or uncertain.

## Non-negotiable sequence

1. Perform only the minimum read-only checks needed to resolve the repository, canonical checkout,
   remote, current branch and verified base, current worktrees, dirty state, matching existing PR,
   and local instructions.
2. Use a clean isolated feature worktree before editing, dependency installation, or service
   startup. Reuse the calling task's already isolated worktree when it owns the foreground lane;
   otherwise create one from refreshed `main`. Bounded read-only discovery may happen first.
3. Reuse a still-valid repository capability profile or refresh only the sections whose evidence
   changed. Fully onboard the worktree from repository evidence.
   Capture the user's deliverable contract and measured verification costs where applicable.
4. Create or refine at least one live GitHub tracking issue for every SDLC request before
   implementation, including code, documentation, configuration, and artifact changes.
   Reuse matching issues; repository issue habits do not make tracking optional.
   Every completed implementation request needs at least one issue and at least one PR,
   linked many-to-many as defined in [delivery tracking](references/delivery-tracking.md).
   Write the smallest execution note that makes scope, acceptance evidence, and rollback clear.
   Require the full spec-ready and visual package only when risk, ambiguity, repository policy, or
   a durable handoff warrants it.
   For an “all”, “every”, or pattern-wide request, inventory every discovered consumer and its
   inclusion decision before choosing the implementation point.
   For a large multi-outcome request, decide whether a parent issue and independently testable
   sub-issues improve delivery. Follow the branch and approval model in
   [decomposition and PR handoff](references/decomposition-and-pr-handoff.md). An explicit
   one-PR instruction keeps one PR while retaining full acceptance coverage.
   For UI work, discover and apply [project UI conventions](references/project-ui-conventions.md)
   across independent tasks without generalizing isolated corrections.
   Identify likely documentation and agent-instruction consumers of the planned change. Use
   [documentation impact](references/documentation-impact.md) to decide what may need updating.
5. Add detailed task contracts, resource budgets, exhaustive test matrices, pinned plan comments,
   or auxiliary records only when they materially reduce delivery risk or support a handoff.
6. In an ordinary task, resolve routine implementation choices from the user request,
   repository conventions, and evidence. Ask only when an unresolved choice materially changes
   the requested behavior, security, data handling, cost, or external impact, or the user reserved
   the plan decision. In verified control-plane autopilot, resolve choices from the trusted goal
   and continue. Record a plan decision only for a material choice or exception.
7. Implement within the authorized envelope. Reconcile any pinned plan comment at
   implementation start and after material findings, updating that same comment in place with
   status, decisions, findings, and changed test mappings. Run cheap prerequisites before
   expensive work, classify failures before remedies, isolate mutable validation state, and
   resume rather than duplicate long operations. Record exact candidate verification runs and
   external provider steps when they affect completion. For a live defect, trace the exact
   failing operation and active revision. If a needed trace is missing, report the root cause as
   unproven and add privacy-safe instrumentation only within the authorized change.
   Reassess documentation impact against the implemented behavior and review findings. Update
   affected user and agent guidance in the same candidate, including maintained generated copies.
8. Freeze the candidate before final evidence. Every PR must identify at least one tracking
   issue, and every delivered issue must identify at least one PR; read back the links in both
   directions before handoff. Record all pairs, not just the primary issue/PR.
   Open or update a pull request only after required
   local checks pass and the documentation-impact decision is resolved. Record the updated
   surfaces or a brief reason no update is warranted in the PR or delivery summary. Known stale
   required guidance prevents a ready-for-delivery claim. In ordinary mode, present it for
   review after the single automatic review-and-address cycle. In verified autopilot, continue to proportionate review and merge readiness without a
   routine pause.
   Any tracked implementation changes in a worktree require a live PR readback before the
   terminal response unless the user explicitly requested local-only work. A blocked PR
   handoff is incomplete, not a successful local-only delivery.
9. After an ordinary explicit approval message or a verified autopilot `proceed`, re-check the PR
   and required checks. Inspect whether merging triggers deployment and resolve target prerequisites
   or verify a safely inactive rollout before the dependent merge; see
   [merge readiness](references/merge-deployment-readiness.md). Then mark it ready if needed, and squash-merge by default. Confirm the merge
   commit, close and read back every still-open implementation issue fully delivered by that PR, then
   fast-forward the canonical checkout. A `Refs` link does not defer closure of a fully delivered
   issue after merge; partial delivery keeps the issue open.
   For a decomposed parent issue, verified child PRs may merge into the parent branch without
   another approval; the parent PR may merge into `main` only after explicit user approval for
   that exact current candidate, even in autopilot mode.
10. Clean up the feature worktree, feature runtime, and merged branch exhaustively but safely.
11. In ordinary mode, require deployment authority for the exact target; reuse an explicit
    authorization already given for that target and candidate instead of asking again. In
    verified autopilot, deploy to the declared target automatically; a direct “deploy” instruction
    may use the repository's single unambiguous documented target.
12. Deploy from the merged canonical revision and repeat applicable verification against the real
    target. Bind evidence to the deployed revision and report the result. Before saying a change is
    available, read back the active runtime revision, expected start mode, target URL, live health,
    and a relevant user flow for the requested surface.
    Before finalizing, recheck every required deliverable and external flow against its requested
    source or target; a saved setting or earlier summary is not completion evidence.
    For stateful releases, check the critical durable records, workers, queues, and external
    outcomes in [critical release invariants](references/critical-release-invariants.md).
13. In an ordinary task, never deploy to production automatically. In verified
    control-plane autopilot, production or another external mutation may proceed
    only when the operator directly named it in the trusted goal or instruction,
    a supported secret-safe mechanism is proven, and required live evidence passes.
    Otherwise record `skip` or `blocked` without asking the operator.

Before provider setup, credential handling, or an external write, read
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).
An authorized outcome carries through its necessary provider clicks and secure
credential steps; do not request fresh confirmation for each button or command.

## Approval interpretation

These human-approval interpretations govern ordinary tasks. In verified
control-plane autopilot, the conditional decision policy above replaces the
ask/wait behavior but does not enlarge authority or weaken any gate.

- An explicit implementation request authorizes routine in-scope planning, edits, local tests,
  commit, push, and a reviewable PR. A request limited to planning, an issue, or a prototype does
  not authorize implementation. Record material assumptions and ask only for a decision that
  cannot be safely resolved from the request, existing conventions, or evidence.
- Plan approval authorizes only the documented implementation and local test plan when the user
  explicitly reserved implementation approval.
- PR approval messages such as “approved”, “looks good, merge”, or “squash merge and pull” authorize
  the default squash merge and canonical fast-forward pull when the target PR is unambiguous.
- A status request, silence, partial feedback, or approval of a different artifact is not approval.
- Deployment needs explicit approval in an ordinary task for the exact target. That approval may
  already be present in the user's request or an earlier decision for the same candidate; do not
  ask again solely because the workflow reached a later stage. A validated control-plane
  autopilot profile instead uses its trusted declared-target authority without a routine approval pause.
- Production deployment always requires a new, explicit user request outside this workflow.
- When feedback changes scope, update the issue and plan. Re-open the plan gate if the change is
  material; update the canonical pinned plan comment in place and keep an audit trail rather than
  silently broadening the work. Never create a second authoritative plan comment.
- A verification-channel fallback that proves less than the approved channel is not plan approval
  and cannot satisfy completion.
- Shared cache, infrastructure, or host-wide reclamation requires exact impact disclosure and a
  separate explicit approval.
- Do not re-ask an answered question or repeat an approval for the same target and scope. Check
  current state, then continue from the first unverified step. If a provider, host, or tool imposes
  its own confirmation, follow it and name that source; workflow text cannot waive it.

## Evidence and safety rules

- Obey repository `AGENTS.md`, contributing docs, CI configuration, deployment runbooks, and the
  actual application behavior. Do not invent commands, behavior, credentials, or success.
- Preserve unrelated dirty or untracked files in every checkout.
- Never expose secret values in conversation, tool output or arguments, process arguments, logs,
  commits, or evidence. Concealed transfer into a secret manager or supported consumer is permitted
  within task authority; apply the linked contract. Environment files copied into the worktree
  remain local and ignored.
- Keep issue, branch, commits, pull request, checks, merge revision, deployment, and verification
  mutually linked where the platform supports it.
- Close implementation tracking issues only after all PRs needed for their acceptance criteria
  merge and the complete issue outcome is verified. A first partial PR must not close a shared issue.
  Keep unverified deployment, runtime,
  and field-evaluation claims explicit; issue closure does not establish those outcomes.
- Treat repository capability profiles as cached evidence, never authority. Validate repository
  identity and evidence digests before reuse; recheck transient external state when applicable.
- Never store secret values, environment values, protected data, or broad home-directory state in
  workflow records. Environment key names and credential requirements may be recorded.
- A failed prerequisite blocks dependent expensive work. Unknown required failures block review.
- Mutable tags, filenames, paths, and timestamps do not establish reusable artifact identity.
- Rehearsal screenshots, videos, or reports are not final evidence. Final evidence binds to the
  committed clean candidate and invalidates on relevant source, test, workflow, artifact, or
  evidence drift.
- Do not weaken tests, bypass branch protection, dismiss findings, or force a merge merely to make
  the workflow pass.
- Prefer a draft PR as the review artifact. Do not interpret draft status as permission to skip
  checks.
- If the repository cannot support a safe worktree, isolated runtime, required evidence, or safe
  deployment path, stop at the affected stage and report the exact blocker.

## Structured record helper

The bundled dependency-free helper validates the shared schema and semantic cross-record rules:

```bash
python3 <skill-root>/scripts/standard_workflow_record.py validate <task-record.json> \
  --profile <repository-profile.json> \
  --source-root <repository-root>
python3 <skill-root>/scripts/standard_workflow_record.py summary <task-record.json>
```

Record `delivery_tracking` for every new task; issue URLs and issue readbacks are required
before execution. Use `--require-final` after live draft-PR linkage readback, and at
merge-readiness and applicable staging evidence gates. Missing pairs block completed delivery.
Canonicalize or digest a record with the corresponding helper subcommand. The helper does not
approve work, execute repository commands, delete resources, or access credentials.
