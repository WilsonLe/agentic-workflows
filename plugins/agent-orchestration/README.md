# Agent Orchestration

AMSoft's Goal Mode control-plane workflow for existing Codex tasks.

## Boundary

The plugin activates only when the operator explicitly designates the current
task as the control plane, main task, master task, orchestration task, or a
clear synonym. It uses host-provided Codex task and goal tools. It bundles no
MCP server, daemon, scheduler, credential, remote service, or task-creation
authority.

Autopilot starts only after the operator goal, exact project boundary,
completion conditions, and material constraints are clear. If they are not
clear, the task asks the minimum necessary questions and waits.

## What it coordinates

- exact same-project task inventory;
- bounded task reads, follow-up messages, and waits;
- concise titles such as `Issue #49 | PR #50 | testing`;
- a minimal local register of task IDs, cursors, archive state, and sanitized
  closeout metadata;
- completion reconciliation and reversible archive/unarchive operations.

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

## First prompt

```text
Make this task the control plane for the current project. The goal is to close
issue #49 through a validated draft PR, coordinating only existing tasks.
```
