# Coordination and waiting

Classify exact same-project peers as active, waiting, needs attention, blocked,
completed, archived-known, or excluded.

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

New missing work is not authority to create or fork a user-owned task. Ask the
operator when another task is necessary.
