---
name: orchestration
description: Turn the current Codex task into a Goal Mode control plane when the operator explicitly calls it the control plane, main session, master session, orchestration session, or a clear synonym; clarify the goal before autopilot, then track and coordinate existing tasks in the exact current project through bounded reads, messages, waits, concise titles, verified closeout, reversible archive, and recovery.
---

# Agent Orchestration

Activate only after an explicit operator designation. A mention of the main branch,
a generic status request, or discussion about orchestration is not
activation.

Read [activation and Goal Mode](references/activation-and-goal-mode.md) first.
Do not inventory or coordinate peer tasks until the goal-clear gate passes.
Then read:

- [project scope and task trust](references/project-scope-and-trust.md);
- [titles and status](references/titles-and-status.md);
- [coordination and waiting](references/coordination-and-waiting.md);
- [closeout, archive, and recovery](references/closeout-archive-recovery.md);
- [coordination register](references/coordination-register.md).

Use `../../scripts/orchestration_state.py` for deterministic local state,
title formatting, wait batches, and archive eligibility. The register is an
index; live goal and task tools remain authoritative.

Never create or fork a task merely because work is missing. Never change
another task's model, reasoning effort, host, worktree, title, issue, PR,
merge, deployment, or scope without the authority that operation normally
requires. Goal Mode increases persistence, not authority.
