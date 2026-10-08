# Excalidraw browser change management

Read [service browser operations](browser-selection.md). This runbook applies to
management, creation, updates, deletion, configuration, deployments, and rollback.

1. Recheck the visible account/team and exact project/resource/environment.
2. Inspect current state and retain relevant non-secret settings for recovery.
3. Identify the smallest UI action and its expected effect, cost, permissions,
   traffic, data, downstream dependencies, and reversibility.
4. Match the action to existing task authority. Inspection/planning allows reads
   only. Resolve uncovered production, destructive, communication, or charge effects.
5. Use supported visible UI controls. Stop on an unexpected target, permission,
   provider restriction, or error; never bypass it through another channel.
6. Observe save/operation completion, reopen the same resource, and compare saved
   state. Verify relevant live behavior separately from a success toast.
7. On an uncertain outcome, read back before retrying. Recover only within existing
   rollback authority; do not automatically reverse a change or broaden its scope.

CLI/helper logs and status are optional read-only supplements after independent
identity/target matching. If a required management action is unavailable in the UI,
report the exact limitation and proposed alternative. A CLI/API mutation requires
explicit user direction for that operation, not just permission to inspect logs.

Report the browser URL, target, before/after result, verification, remaining risk,
and recovery state; distinguish supplemental diagnostics from browser evidence.
