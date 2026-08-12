# Delegated session launch settings

When the control plane creates a separate issue-owned session, request these
launch settings when the host supports them:

- permission profile `full_access`;
- execution mode `goal` or `plan`.

Full Access suppresses routine host sandbox and approval prompts for in-scope work. The trusted
control-plane authority envelope, not the permission profile, authorizes ordinary commit, push,
merge, pull, and declared-target deployment actions.

## Select the execution mode

Use a mode already fixed by authoritative control-plane context when present. Otherwise select a
mode only when the issue contract is unambiguous:

- `goal` persists toward a concrete terminal outcome;
- `plan` gathers evidence and produces a reviewable plan or handoff, then stops.

If neither source selects exactly one mode, default to `goal` for a concrete delivery outcome and
`plan` for an explicitly planning-only outcome. Never ask the operator to select a mode during
autopilot.

In Goal mode, establish the objective, exact project boundary, completion conditions, and material
constraints before creating or resuming the child goal. Omit `token_budget` unless the operator
supplied one. Complete only on the actual terminal outcome; use blocked only after the required
repeated-blocker threshold.

In Plan mode, allow read-only inspection and the requested plan/handoff only. Do not implement,
commit, push, open a PR, merge, deploy, mutate a provider, or perform another unapproved write.

## Proportionate launch preflight

Inspect the live host task-creation and task-readback capabilities. Prefer a host that can:

1. request `full_access` at child creation;
2. request the selected `goal` or `plan` mode at child creation;
3. authoritatively report the effective permission profile; and
4. authoritatively report the effective execution mode.

Missing metadata or readback is not by itself a delivery blocker. Reuse the current task when safe,
or create the lane with the strongest supported settings and record the limitation once. Block
only when the separate lane is required for safety or independence and the host cannot establish
that boundary. Prompt text is not proof of an unavailable host setting.

Use the existing sanitized compatibility categories when a limitation is material:
`host_capability`, `readback_unavailable`, `permission_mismatch`, or `mode_mismatch`.

## Creation and authoritative readback

After a successful preflight, create the project task in its new worktree and record the exact
thread and host IDs as `created`. Read the task back before sending implementation follow-ups or
classifying the lane active.

If worktree setup returns only a pending client identifier, remain `preflight_verified`; do not
bind or activate the launch until the host returns the real thread and host IDs.

- Exact readback transitions the launch to `verified`.
- Missing readback records `readback_unavailable` and continues only if the lane can safely operate
  under the observed host controls.
- A permission or mode mismatch blocks only when it prevents the lane's required in-scope work or
  invalidates a required independence claim; otherwise adapt the lane and record the limitation.

Do not claim settings the host did not prove. Preserve any created but unusable task for explicit
reconciliation, but do not let metadata ceremony stall work that can safely remain in the current
task.

## Coordination state

Persist only the issue number, requested and effective setting tokens, selection source,
verification state, sanitized blocker category, exact optional child task identity, and observation
time. Never store prompts, message bodies, tool output, credentials, authorization data, or
environment values.
