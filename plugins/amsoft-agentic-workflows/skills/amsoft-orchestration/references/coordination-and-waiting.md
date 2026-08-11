# Coordination and waiting

Classify exact same-project issue sessions and observed peers as active,
waiting, needs attention, blocked, completed, archived-known, or excluded.

For each relevant peer:

1. read the minimum recent state;
2. compare it with the clear goal, issue, pinned plan, acceptance criteria, and
   dependencies;
3. send a bounded follow-up only when it is within approved scope;
4. preserve the peer's current model and reasoning settings;
5. update the local register after meaningful live observations.

Use bounded waits:

- at most eight targets per `wait_threads` call;
- use one target for a single-task wait;
- preserve returned cursors;
- do not repeat already delivered final text;
- partition larger sets deterministically and rotate batches fairly;
- report meaningful transitions, not unchanged snapshots.

Create a user-owned Codex task only for issue work selected under the explicit
control-plane goal and the issue-session lifecycle. Never create a subagent,
fork a task, or use a same-directory task as an issue worker.
