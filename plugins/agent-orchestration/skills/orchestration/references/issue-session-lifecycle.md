# Issue session lifecycle

## Start one issue-owned session

For every issue selected to start:

1. resolve the exact saved project and confirm it is the intended Git
   repository;
2. refresh and re-read the canonical `main` branch and its commit identity;
3. use the host's Codex task creation capability for that project with a new
   worktree starting from the verified `main` branch;
4. create or verify one issue-specific branch in that worktree based on the
   same `main` commit; never leave issue work detached or on a reused branch;
5. give the session one issue-scoped objective, normal approval boundaries,
   expected evidence, and a terminal handoff contract;
6. retain the exact task and optional host IDs plus verified issue, base
   revision, branch, and worktree identities in the coordination register; and
7. read the created task back before treating the lane as started.

Never use subagents, delegation APIs, an in-process worker, a fork of another
task, a same-directory session, a stale base, or an existing issue worktree.
If the host cannot prove a new worktree based on refreshed `main`, do not claim
the issue started.

## Coordinate to terminal handoff

Use bounded task reads, follow-up messages, and cursor-aware waits for status,
questions, evidence, review findings, and handoff. Preserve the created task's
model and reasoning settings. The parent control plane remains responsible for
issue selection, dependency and overlap decisions, verification, and the final
live issue/PR/`main` readback.

A terminal handoff is either completed work or an explicitly blocked result
that identifies the blocker and preserves all recoverable work. Read the final
result and reconcile it against the issue, PR, branch, verification, and
dependencies before closeout. Silence, an interrupted task, an unread final
response, or a transient needs-attention state is not terminal.

## Archive and clean up

Every terminal issue session enters closeout, including explicitly blocked
sessions:

1. record terminal verification, final read, reconciliation, archive intent,
   and exact task/host identity;
2. archive the exact Codex task and verify authoritative success;
3. preserve any PR, commit, patch, or unmerged branch evidence required to
   continue or review the issue;
4. prove the exact worktree is task-owned, inactive, and clean before removal;
5. remove only that exact worktree through Git or the host-supported lifecycle;
6. delete the exact issue branch only when it is merged or otherwise proven
   disposable and no retained evidence depends on it; and
7. re-read task, worktree, branch, issue, PR, and `main` state and record the
   cleanup result.

Never remove a dirty, active, shared, ambiguous, unrelated, or evidence-bearing
worktree. Never delete unmerged work. When safety prevents full cleanup, archive
the terminal session, retain the exact branch or worktree needed for recovery,
mark cleanup `preserved`, and report the limitation; do not claim it was
cleaned. Never use broad globs, global pruning, or destructive repository-root
commands.
