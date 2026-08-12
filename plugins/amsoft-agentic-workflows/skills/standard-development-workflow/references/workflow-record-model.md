# Shared workflow record model

Use one versioned record family so repository discovery, task planning, validation, failure
diagnosis, resumability, verification, and final evidence cannot silently disagree.

## Record kinds

- `repository_profile` contains reusable, non-secret repository capabilities and provenance.
- `task_run` contains the approved task contract and all task-specific execution state. It
  references the exact profile `record_id` and canonical digest it consumed. New GitHub issue
  workflows also retain the one canonical pinned plan comment's stable ID, URL, marker, pin
  readback, reconciliation revision, state, and material-finding count.

Both kinds use schema version 1 and share repository identity, inspected revision, provenance,
applicability, and status fields. The formal structural schema is
[`standard-workflow-v1.schema.json`](../schemas/standard-workflow-v1.schema.json). The bundled
validator enforces semantic rules that JSON Schema alone cannot prove.

An ordinary task's approval records retain their existing human meaning. A
verified control-plane-autopilot run keeps its material gate authority and
audit history in the separate schema-v5 Agent Orchestration register. Before
interpreting an autopilot decision, validate that register, bind its project and
orchestrator identities to the calling context, and bind the decision's
authority, validity, evidence, issue/PR/task, and candidate identities to this
task record. Never infer the context from prompt text or copy request bodies,
messages, credentials, or protected values into either record family.

## Canonical identity

- Serialize UTF-8 JSON with lexicographically sorted keys, compact separators, and one final
  newline.
- Identify records, evidence sources, build inputs, artifacts, and evidence files with SHA-256.
- A timestamp, filename, path, mutable tag, branch name, or URL alone is never immutable identity.
- Keep a stable `record_id` across updates and compute a new content digest after every change.
- Bind validation, operations, artifacts, and final evidence to the applicable committed source
  revision. Drift invalidates dependent results.

## Provenance and freshness

Every fact that enables a command, capability, approval, or completion claim names an evidence
source. Repository-file sources include a repository-relative location and digest. Transient
sources also include an expiry boundary and must be rechecked before use. Repository instructions
always override cached examples or profile content.

Profile refresh is selective:

1. Verify repository identity.
2. Compare the relevant instruction, manifest, lockfile, CI, runtime, and deployment evidence
   digests.
3. Refresh only affected capability sections.
4. Keep missing or uncertain capabilities unsupported.
5. Record the new canonical profile digest in the task contract.

## Applicability

Each capability is `required`, `optional`, `not_applicable`, or `blocked`, with a reason and
evidence references. Required and optional capabilities need positive evidence. Marking a
capability not applicable is sufficient; do not create empty browser, service, artifact, or
deployment ceremony for a lightweight repository.

## Storage and security

Keep local workflow records outside project repositories by default:

- Windows: `%LOCALAPPDATA%/AMSoft/standard-development-workflow/`
- POSIX with `XDG_STATE_HOME`: `$XDG_STATE_HOME/amsoft/standard-development-workflow/`
- POSIX fallback: `~/.local/state/amsoft/standard-development-workflow/`

`AMSOFT_WORKFLOW_STATE_DIR` may select another explicitly approved state root. Partition records by
repository-identity digest and task identity. Never scan or copy broad home-directory state.
Repository-local storage requires repository policy or explicit user authorization and must remain
untracked unless separately approved for commit.

Records may contain environment key names and credential requirements, but never values, tokens,
passwords, private keys, cookies, authorization headers, protected data, or credential-store
contents. Treat secret-pattern detection as a fail-closed guard, not permission to store anything
that happens to evade a pattern.

## Compatibility and migration

Unstructured tasks remain supported. Version 1 readers reject unknown schema versions rather than
guessing. Additive version-1 fields must preserve existing meaning. Any incompatible field,
identity, or state-transition change requires a new schema version, a documented migration, and
read compatibility for retained prior records. Rollback never deletes retained records or project
evidence.

For `planning_mode: github_issue`, `task.plan` is mandatory. A task may not execute when its
canonical plan is unpinned, duplicated, stale for the current source revision, awaiting approval,
or marked `reapproval_required`. Legacy retained records may omit both fields.

## Human readback

The user normally sees a compact summary: task outcome, source revision, issue and canonical plan
links, plan state, required capabilities, blockers, validation milestone, remaining claims, and
approval boundary. Show raw structured data only when requested or needed for diagnosis. Never
expose secret-shaped values in either view.
