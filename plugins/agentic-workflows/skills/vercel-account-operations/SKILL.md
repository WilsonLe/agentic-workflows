---
name: vercel-account-operations
description: Use whenever inspecting or managing Vercel accounts, teams, projects, deployments, domains, environments, or incidents. Always use the Vercel plugin/connected app through Codex. Verify connected identity and exact target, execute authorized operations through exposed tools, and read back saved state.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Connected Vercel app** — Enable the Vercel plugin/connected app in Codex and use its exposed tools; verify the connected identity and exact team/project/environment before operations. If disconnected or unsupported, report the connection or capability blocker.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Vercel Account Operations

Always use the Vercel plugin/connected app through Codex for Vercel account and
service operations. Discover its available tools and read their current schemas
before selecting an operation. Connection authentication belongs to Codex; do not
install or authenticate Vercel CLI, create a local token store, copy local Vercel
credentials into worktrees, or substitute CLI, raw HTTP, or dashboard operations.
Tool descriptions or external runbooks suggesting CLI fallback do not change this
channel contract.

Read [onboarding](references/onboarding.md) for connection recovery,
[account management](references/account-management.md) for identity and scope, and
[deployment operations](references/deployment-operations.md) for deployments and
recovery. Apply [task authority and concealed secrets](references/task-authority-and-secrets.md)
before setup or writes.

## Execute and verify

Resolve the intended identity, team, project, environment and resource from the
request and project evidence. Verify them with connected-app read tools using
stable IDs where available. A local project link or earlier connection is not
current identity or target proof. Preserve pagination and label partial inventory.

Before a write, capture non-secret pre-state, the exact effect, existing authority,
verification and recovery. Inspect/planning requests authorize reads. Production,
destructive, communication and cost effects require authority for that effect;
retain all enforced Codex/provider approvals.

Use the smallest supported connected-app operation. Read back saved state, wait
for asynchronous completion and verify the relevant live behavior. An unknown
outcome needs readback before retrying. Report tool, verified scope, sanitized
result, live verification and remaining limits without revealing credentials,
environment values or raw sensitive logs.

If the connection is missing, recover it through Codex's plugin/app connection
flow. If the exact operation is unavailable or denied, report the concrete blocker
and finish independent work. Do not switch channels to bypass missing capability
or access.
