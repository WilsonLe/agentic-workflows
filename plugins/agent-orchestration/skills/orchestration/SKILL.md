---
name: orchestration
description: Turn the current Codex task into a Goal Mode control plane when the operator explicitly calls it the control plane, main session, master session, orchestration session, or a clear synonym; clarify the goal, actively triage current project issues, run selected issue work in verified Full Access Goal or Plan Codex sessions with isolated worktrees, delegate independent asynchronous exact-head code review, and reconcile, archive, and safely clean up every terminal session.
---

# Agent Orchestration

Activate only after an explicit operator designation. A mention of the main branch,
a generic status request, or discussion about orchestration is not
activation.

Read [activation and Goal Mode](references/activation-and-goal-mode.md) first.
Do not inventory or coordinate peer tasks until the goal-clear gate passes.
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

Cap every review-and-address loop before its next workflow step at two review
passes. Pass 2 is final: proceed only on valid clearance; otherwise stop the
loop and escalate the unresolved state for an explicit operator decision. Never
start pass 3 automatically or treat the cap as permission to bypass a gate.
