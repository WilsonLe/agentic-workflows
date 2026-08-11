# Delegated session launch settings

Every issue-owned session requires two authoritative launch settings:

- permission profile `full_access`;
- execution mode `goal` or `plan`.

Full Access suppresses routine host sandbox and approval prompts for in-scope work. It does not
expand the operator-approved issue scope or authorize credentials, merges, releases, deployments,
unrelated external mutations, or destructive work.

## Select the execution mode

Use an explicit operator choice when present. Otherwise select a mode only when the approved issue
contract is unambiguous:

- `goal` persists toward a concrete terminal outcome;
- `plan` gathers evidence and produces a reviewable plan or handoff, then stops.

If neither source selects exactly one mode, report the lane as not started/needs attention, ask the
smallest necessary question, and do not create a launch record or child task.

In Goal mode, establish the objective, exact project boundary, completion conditions, and material
constraints before creating or resuming the child goal. Omit `token_budget` unless the operator
supplied one. Complete only on the actual terminal outcome; use blocked only after the required
repeated-blocker threshold.

In Plan mode, allow read-only inspection and the requested plan/handoff only. Do not implement,
commit, push, open a PR, merge, deploy, mutate a provider, or perform another unapproved write.

## Preflight before task creation

Inspect the live host task-creation and task-readback capabilities. Continue only when the host can:

1. request `full_access` at child creation;
2. request the selected `goal` or `plan` mode at child creation;
3. authoritatively report the effective permission profile; and
4. authoritatively report the effective execution mode.

If any capability is missing, record the launch `blocked` with `host_capability`, report the exact
missing fields, and do not create the child. Prompt text is not a permission or mode control plane
and must never be treated as proof of either setting.

## Creation and authoritative readback

After a successful preflight, create the project task in its new worktree and record the exact
thread and host IDs as `created`. Read the task back before sending implementation follow-ups or
classifying the lane active.

If worktree setup returns only a pending client identifier, remain `preflight_verified`; do not
bind or activate the launch until the host returns the real thread and host IDs.

- Missing authoritative settings block with `readback_unavailable`.
- An effective permission other than `full_access` blocks with `permission_mismatch`.
- An effective mode different from the requested mode blocks with `mode_mismatch`.
- Only exact matches transition the launch to `verified` and allow issue-session activation.

Do not retry by weakening the settings, switching to a same-directory task, or embedding claims in
the prompt. Preserve any created but unverified task for explicit reconciliation; do not assign it
issue work.

## Coordination state

Persist only the issue number, requested and effective setting tokens, selection source,
verification state, sanitized blocker category, exact optional child task identity, and observation
time. Never store prompts, message bodies, tool output, credentials, authorization data, or
environment values.
