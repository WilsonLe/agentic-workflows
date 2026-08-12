---
name: amsoft-orchestration
description: Turn the current Codex task into a mandatory-autopilot Goal Mode control plane when the operator explicitly calls it the control plane, main session, master session, orchestration session, or a clear synonym; carry one foreground delivery issue through recorded evidence-based gates to a tested linked PR or explicit blocker, decide spawned-session requests without relaying approval questions, delegate same-candidate review and verification asynchronously, and reconcile, archive, and safely clean up every terminal session.
---

# Agent Orchestration

Activate only after an explicit operator designation. A mention of the main branch,
a generic status request, or discussion about orchestration is not
activation.

Read [activation and Goal Mode](references/activation-and-goal-mode.md) first.
Control-plane mode always runs in autopilot: never offer or enter a manual
control-plane mode and never ask the operator for approval after activation.
If authoritative context cannot safely resolve the goal or project, record a
blocked gate decision and stop without inventing scope.
Then read:

- [project scope and task trust](references/project-scope-and-trust.md);
- [portfolio triage](references/portfolio-triage.md);
- [delegated session launch settings](references/delegated-session-launch-settings.md);
- [issue session lifecycle](references/issue-session-lifecycle.md);
- [review session lifecycle](references/review-session-lifecycle.md);
- [titles and status](references/titles-and-status.md);
- [coordination and waiting](references/coordination-and-waiting.md);
- [closeout, archive, and recovery](references/closeout-archive-recovery.md);
- [coordination register](references/coordination-register.md).

Use `<plugin-root>/scripts/orchestration_state.py` for deterministic local state,
portfolio start decisions, title formatting, wait batches, archive eligibility,
and worktree-cleanup gates. The register is an index; live goal, project, task,
Git, and GitHub tools remain authoritative.

Keep exactly one foreground delivery issue. Do not start a second issue
implementation until the foreground issue reaches a tested linked draft PR with
all currently applicable unchanged-head review and verification evidence, or an
explicit recoverable blocked handoff. Additional capacity is for review,
verification, CI, and bounded diagnostics of the same foreground candidate, or
read-only preparation for the next issue.

Never create subagents or use subagent/delegation APIs. Selected issue work and
code review are started only with the host's user-owned Codex task creation
capability. Issue implementation uses a new project worktree based on refreshed
`main`; review uses a separate detached worktree pinned to the exact review
target. Never fork an existing task or reuse a same-directory checkout.

The control plane never performs code review itself. It may verify identities,
revisions, checks, review-task state, and finding disposition, but it delegates
all diff inspection and defect discovery to independent review sessions. Never
change another task's model, reasoning effort, host, title, issue, PR, merge,
deployment, or scope without the authority that operation normally requires.
Goal Mode increases persistence, not authority.

At every material plan, implementation, PR, review/remediation, merge,
synchronization, staging, production/provider/financial/destructive action,
archive, cleanup, or spawned-request gate,
record exactly one evidence-based `proceed`, `revise`, `retry`, `skip`, `stop`,
or `blocked` decision. Missing authority, credentials, required evidence, or a
safe supported path produces `skip`, `stop`, or `blocked`; it never produces an
operator approval prompt. Relevant goal, scope, repository, candidate, check,
review, verification, deployment, or authority drift invalidates the prior
decision and requires a fresh decision.

Staging, production, provider mutation, financial activity, credential use,
destructive recovery, and shared-resource reclamation proceed only when the
exact action is already unambiguously inside the declared goal, existing
authority and a supported secret-safe mechanism are proven, and required live
evidence passes. Otherwise record `skip` or `blocked`; never ask the operator to
expand authority. Autopilot never bypasses branch protection, weakens tests,
relabels evidence, or deletes ambiguous, dirty, shared, or unmerged work.

Cap every review-and-address loop before its next workflow step at two review
passes. Pass 2 is final: proceed only on valid clearance; otherwise record
`stop` or `blocked` and preserve the unresolved state. Never start pass 3 or
treat the cap as permission to bypass a gate.
