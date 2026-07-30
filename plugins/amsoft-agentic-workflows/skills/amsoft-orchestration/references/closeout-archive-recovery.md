# Closeout, archive, and recovery

A peer is archive-eligible only when live state proves all of the following:

- terminal completed state or final response;
- final result read;
- reconciliation against required deliverables and dependencies;
- no blocker, user-input request, review, or unresolved dependency;
- exact task and optional host IDs captured;
- archive intent recorded before mutation.

Archive eligible managed peers automatically during requested closeout.
Archive is reversible; deletion is never allowed. Do not archive running,
waiting, blocked, needs-attention, ambiguous, unrelated, or still-needed
tasks.

Record archive success only from authoritative tool success/readback. Keep the
orchestration task unarchived until it has delivered the final coordination
readback. Self-archive only when explicitly requested or through a later safe
completion action.

To recover a known task:

1. resolve the exact project-scoped register;
2. match an exact task ID, or one unambiguous retained display title;
3. ask for clarification when multiple records match;
4. unarchive the exact ID;
5. read live state and return it to the managed set.

Never guess an archived task ID.
