# Closeout, archive, and recovery

A managed task is archive-eligible only when live state proves all of the
following:

- terminal completed state, or an explicitly blocked terminal handoff;
- final result read;
- reconciliation against required deliverables and dependencies;
- no transient needs-attention state or unread user-input/review request;
- exact task and optional host IDs captured;
- archive intent recorded before mutation.

Archive eligible managed tasks automatically during requested closeout.
Archive is reversible; task deletion is never allowed. Do not archive running,
waiting, needs-attention, ambiguous, unrelated, or still-needed tasks. A
blocked issue session is archive-eligible only after its explicit terminal
handoff is read and reconciled; an ordinary blocked observed peer remains
ineligible.

For an issue-owned session, archival is followed by the exact safe worktree and
branch cleanup sequence in `issue-session-lifecycle.md`. Archive success does
not prove cleanup. Dirty, unmerged, active, shared, ambiguous, or
evidence-bearing resources are preserved and reported instead of deleted.

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
