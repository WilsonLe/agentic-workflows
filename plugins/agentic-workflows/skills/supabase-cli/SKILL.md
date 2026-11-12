---
name: supabase-cli
description: Use whenever inspecting or managing Supabase accounts, projects, resources, deployments, or incidents. Require the supabase CLI with tokens obtained from Infisical, verify identity and exact target, and read back results. Report missing tokens, permissions or CLI capabilities without connector or cached-login fallback.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Optional: Service CLI and Infisical access** — Required for remote operations only; install supabase and Infisical CLI, authenticate Infisical, and resolve the exact secret scope. Obtain SUPABASE_ACCESS_TOKEN from Infisical into a concealed child environment. Verify identity and target through read-only CLI commands; report missing access or CLI support without connector fallback.
- **Optional: Local Supabase development tools** — Use repository-required Supabase CLI commands for proven local-only development without a remote token.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Supabase Account Operations

Use the `supabase` CLI with `SUPABASE_ACCESS_TOKEN` obtained from Infisical under the
[shared provider channel contract](../agentic-workflows/references/service-browser-operations.md).
Load [Infisical Account Operations](../infisical-account-operations/SKILL.md) before
authentication or token delivery. Reuse its human-present profile or approved
machine identity; require a successful named-token fetch before launching the CLI.
Supply credentials only in the narrowly scoped child environment, capture both
output streams and return sanitized metadata. Never use token flags or cached
CLI login to fill a missing token. Do not use connected-app tools, dashboard
management or raw account HTTP/SDK calls as a fallback.

Resolve the exact organization, project ref, database branch and environment from the request and project evidence.
Verify provider identity/scope and stable target IDs with read-only CLI commands.
Inspect the installed version and exact command help; a CLI name or local link
establishes neither permission nor operation support. Missing/expired tokens,
permission denial, target mismatch and unsupported commands block dependent work.
Recover the exact access/capability gap through Infisical; never broaden credentials
or switch accounts automatically. Continue independent work where possible.

Before writes or secret handling, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).
Capture nonsecret pre-state, effect, cost/data/traffic impact, validation and recovery.
Reuse in-scope authority and preserve production, destructive, charge, communication
and enforced human-approval gates. Read back saved state, wait for asynchronous
terminal status and verify relevant live behavior. Unknown outcomes require
readback before retry. Report the sanitized command, verified target, result and
verification limits; a queued action or local preview is not remote success.

## Local development

The `supabase-cli` invocation remains compatible. Use repository-required CLI
commands for local stack startup, schema generation/diffs and local tests without
remote authentication. Verify they are local-only before running them. Remote
migrations, queries, functions, secrets and project operations require the
Infisical-backed management token and explicit project/branch selection. Application
publishable/anon/service-role keys are runtime configuration, not management tokens.
Local tests do not prove a hosted migration or deployment succeeded.
