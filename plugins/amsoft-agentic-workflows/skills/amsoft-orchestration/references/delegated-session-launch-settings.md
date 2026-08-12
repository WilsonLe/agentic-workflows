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

## Mandatory Luna/max profile for review and verification

Code-review tasks and test-and-verification tasks have two additional
authoritative launch settings:

- model `gpt-5.6-luna`;
- reasoning effort `max`.

Before creating either task, require host support for selecting and reading
back both settings. After creation, read the task back and require both exact
effective values before activating the lane. Unsupported selection, missing
readback, rejection, downgrade, or mismatch blocks the lane. Never fall back to
another model or effort unless the operator separately authorizes that change.

Review findings return to the original implementation session and worktree as
a new remediation turn explicitly invoked with `gpt-5.6-luna` and `max`.
Authoritatively verify those effective turn settings before any addressing
work begins. Do not change tracked files when the host cannot prove the exact
remediation profile.

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

Do not retry by weakening the settings or embedding claims in the prompt.
Same-directory reuse is allowed only for the serialized review and verification
handoffs defined by their lifecycle references. Preserve any created but
unverified task for explicit reconciliation; do not assign it issue work.
Do not claim settings the host did not prove or retry by weakening them or
embedding claims in the prompt. Preserve any created but unverified task for
explicit reconciliation; do not assign it issue work. Same-directory reuse is
allowed only for the serialized review and verification handoffs defined by
their lifecycle references. Missing metadata may be recorded once when the lane
can safely operate, but it blocks when required delivery or independence cannot
be proven.

## Coordination state

Persist only the issue number, requested and effective setting tokens, selection source,
verification state, sanitized blocker category, exact optional child task identity, and observation
time. Never store prompts, message bodies, tool output, credentials, authorization data, or
environment values.
