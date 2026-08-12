---
name: orchestration
description: Turn the current Codex task into a fast mandatory-autopilot Goal Mode control plane when the operator explicitly calls it the control plane, main session, master session, orchestration session, or a clear synonym; carry one foreground delivery issue through implementation, merge, pull, and deployment without routine approval pauses or ceremony-only records while preserving required evidence and safety boundaries.
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

Use `<plugin-root>/scripts/orchestration_state.py` when durable coordination state,
portfolio selection, title formatting, wait batching, archive eligibility, or
worktree-cleanup proof materially helps the run. Do not create or update records
solely to narrate routine progress. The register is an index; live goal, project,
task, Git, and GitHub tools remain authoritative.

Keep exactly one foreground delivery issue. Do not start a second issue
implementation until the foreground issue reaches a tested linked draft PR with
all currently applicable unchanged-head review and verification evidence, or an
explicit recoverable blocked handoff. Additional capacity is for review,
verification, CI, and bounded diagnostics of the same foreground candidate, or
read-only preparation for the next issue.

Never create subagents or use subagent/delegation APIs. Use the host's user-owned
Codex task capability only when a separate writer, reviewer, verifier, or delivery
lane provides real independence or parallel value. Routine coordination and safe
in-scope implementation may stay in the current task. Any concurrent writer uses
an owned worktree based on refreshed `main`; an independent reviewer uses a
separate exact-head checkout. Never share a writable worktree concurrently.

The control plane does not claim independent code review of its own changes. It
may inspect code while implementing and may verify identities, revisions, checks,
review state, and finding disposition. Use independent review when repository
policy, risk, or the goal requires it; otherwise proportionate automated checks
and existing review evidence may satisfy the gate. Never invent clearance.

At activation, capture one concise trusted authority envelope for the declared
goal. It pre-authorizes the ordinary delivery actions needed to finish that goal:
issue and plan maintenance, isolated implementation, local runtime use, commit,
push, PR creation or update, merge, canonical fast-forward pull, safe cleanup,
and deployment plus verification to the declared target. Do not pause for a new
approval at each of those steps.

Record a gate decision only at a meaningful milestone or exception: scope or
authority changes, candidate freeze, unresolved evidence, merge, deployment,
destructive action, or terminal disposition. Reuse a still-valid decision while
its identity, evidence, and authority remain unchanged. Do not record per-command,
per-message, per-wait, or ceremony-only decisions.

Deployment proceeds automatically when its target is named by the trusted goal,
is the repository's single unambiguous documented target for a direct “deploy”
instruction, or is separately named by the operator. Production is allowed only
by that direct trusted production scope; never infer it from staging authority.
Credentials must use a supported secret-safe mechanism. Autopilot never bypasses
branch protection, weakens required checks, relabels evidence, performs financial
activity without exact direct scope, or deletes ambiguous, dirty, shared, or
unmerged work.

Cap every review-and-address loop before its next workflow step at two review
passes. Pass 2 is final: proceed only on valid clearance; otherwise record
`stop` or `blocked` and preserve the unresolved state. Never start pass 3 or
treat the cap as permission to bypass a gate.
