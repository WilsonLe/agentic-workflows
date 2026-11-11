---
name: supabase-cli
description: Use whenever inspecting or managing Supabase accounts, projects, resources, deployments, or incidents. Use the configured Codex plugin/connected app, reuse Codex-managed authentication, and verify the exact target. Report missing connections or capabilities without local CLI tokens or dashboard fallback. Also covers repository-required local-only Supabase CLI development.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Optional: Connected Supabase app** — Required for remote operations only; use the configured Supabase plugin/connected app in Codex. Reuse Codex-managed authentication and verify the exact account/project/environment through tools. Recover missing connections through Codex and report unavailable operations or permissions without local CLI tokens or dashboard fallback.
- **Optional: Local Supabase development tools** — Use repository-required Supabase CLI commands only for proven local-only development; they do not authenticate remote connected-app operations.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Supabase Account Operations

Use the configured Supabase plugin/connected app through Codex under the
[shared provider channel contract](../agentic-workflows/references/service-browser-operations.md).
Codex owns authentication. Reuse an existing healthy connection and verify the
exact organization, project ref, database branch, and environment through read-only tools before
operations. Recover missing/expired connections through Codex; report unavailable
operations or permissions without CLI/token, raw account API, or dashboard fallback.
Never infer that this skill's installation establishes a connection.

Before writes or runtime-secret handling, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).
Capture nonsecret pre-state, effect, target, cost/data/traffic impact, validation,
and recovery. Reuse existing in-scope authority; a configured connection grants
none. Preserve production, destructive, charge, and enforced human-approval gates.

The `supabase-cli` skill name remains for existing invocations. Remote migrations,
queries, functions, secrets, and project operations use the connected Supabase
app's exposed capabilities and the repository runbook. Inspect the exact target
and requested effect; a local link does not select or isolate a hosted database.
Application publishable/anon/service-role keys are runtime configuration, not
agent account authentication. Avoid reading or returning connection secrets.

## Local development

Use the repository's supported local Supabase CLI only for local stack startup,
local schema generation/diffs, or other proven local-only commands. Remote login
is not a prerequisite for local-only work. Inspect current help/runbooks and
confirm a command does not contact hosted projects before running it. Local
migrations/tests do not prove a remote migration or deployment succeeded. Never
use CLI login or a local token store as a fallback for remote app operations.

## Execution and evidence

Execute the smallest supported connected-tool operation. Read back saved state,
wait for asynchronous completion, and verify relevant workload behavior. Unknown
write outcomes require readback before retrying. Keep query/log results bounded;
never expose tokens, authorization data, private records, or environment values.
Report the actual tool, verified identity/target, operation, observed result,
verification limits, and recovery status. Local previews or an acknowledgement
alone do not prove remote success.
