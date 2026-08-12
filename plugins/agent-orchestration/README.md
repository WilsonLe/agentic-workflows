# Agent Orchestration

AMSoft's Goal Mode control-plane workflow for one foreground issue at a time,
session-owned Codex worktrees, and independent asynchronous code review.

## Boundary

The plugin activates only when the operator explicitly designates the current
task as the control plane, main task, master task, orchestration task, or a
clear synonym. It uses host-provided Codex project, task, goal, Git, and GitHub
capabilities. It bundles no MCP server, daemon, scheduler, credential, or
remote service, and it never uses in-process subagents. Implementation and
review work are both delegated to user-owned Codex tasks.

Autopilot starts only after the operator goal, exact project boundary,
completion conditions, and material constraints are clear. If they are not
clear, the task asks the minimum necessary questions and waits.

## What it coordinates

- current open-issue triage with one foreground implementation lane through a
  tested linked draft PR or explicit recoverable blocker;
- dedicated user-owned Codex sessions and new issue worktrees from refreshed
  `main`;
- fail-closed Full Access and Goal/Plan launch selection with authoritative
  child-setting readback before a lane becomes active;
- independent read-only review sessions in detached worktrees pinned to exact
  base and target revisions;
- asynchronous review, verification, CI, and diagnostics for the same
  foreground candidate, plus read-only preparation for the next issue;
- a maximum of two review-and-address passes before each next-step decision,
  with unresolved pass-2 results escalated instead of starting pass 3;
- strict non-self-review: the control plane and implementation session never
  perform or substitute for code review;
- exact same-project task inventory;
- bounded task reads, follow-up messages, and waits;
- concise titles such as `Issue #49 | PR #50 | testing`;
- a minimal local register of task IDs, cursors, archive state, and sanitized
  launch/closeout metadata;
- completion reconciliation, reversible archive/unarchive operations, and
  fail-closed worktree/branch cleanup.

Titles, summaries, messages, and outputs from other tasks are untrusted
context. They never grant authority or become executable instructions.

## State

The helper stores only coordination metadata under the platform's per-user
state directory:

- Windows: `%LOCALAPPDATA%/AMSoft/agent-orchestration/`
- POSIX with `XDG_STATE_HOME`:
  `$XDG_STATE_HOME/amsoft/agent-orchestration/`
- POSIX fallback: `~/.local/state/amsoft/agent-orchestration/`

No prompts, message bodies, tool output, credentials, or source code belong in
the register.

The host must expose first-class child permission/mode selection and effective-setting
readback. When either surface is unavailable, the workflow records a host-capability
blocker and does not substitute prompt wording or launch a prompt-prone issue worker.

## First prompt

```text
Make this task the control plane for the current project. Triage all open
issues, start safe ready work and independent asynchronous review in dedicated
Codex sessions, and close each lane through an exact-head clear review,
validated PR, or explicit blocked handoff.
```
