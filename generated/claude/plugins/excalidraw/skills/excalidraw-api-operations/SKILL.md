---
name: excalidraw-api-operations
description: Inspect and manage Excalidraw Plus with the authenticated protected command-line REST client. Use the built-in Codex browser to obtain a missing personal key for the project account, then verify the client. Browser operations are fallback only for unsupported authenticated client actions; covers workspaces, collections, scenes, users, invites, and logs.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected Excalidraw command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# Excalidraw Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

Use the bundled command-line client at `<plugin-root>/scripts/excalidraw_api.py`.
It is the supported CLI interface to the REST service; do not invent an official
Excalidraw CLI or configure MCP as a substitute. For first use read
[onboarding](references/onboarding.md) and [credential contract](references/credential-contract.md).
Accept only the supported personal MCP/API key; retain provenance and protected
storage checks. Browser-assisted acquisition does not change token-type constraints.

Verify authentication with a bounded read of collections, then independently
resolve workspace/account and exact resource from supported reads and project
metadata. List access alone does not prove every permission or identity; stop
if account/resource matching remains unproven.

Read [resource map](references/api-resource-map.md) for supported client actions,
[change management](references/change-management.md) before writes, and
[errors](references/errors-and-rate-limits.md) for uncertain outcomes. Use
`excalidraw-scene-operations` for one scene's content, backups, rendering, and recovery.

Default supported operations to the authenticated client. If that client cannot
perform the requested action or prove required live editor behavior, record the
capability gap and use visible browser controls on the same account/scene. Keep
exact resource authority and destructive-operation guards; do not retry unknown writes.


## Execution and evidence

Before writes, capture relevant pre-state, exact target, effect, task authority,
verification, and recovery. Inspection/planning authorize reads only. Match
production, destructive, communication, and cost effects to existing authority;
do not ask again for routine in-scope steps. Keep enforced provider approvals.

Run the smallest supported operation through the authenticated client, read back
saved state, observe asynchronous completion, and verify relevant live behavior.
An unknown write outcome requires readback before retrying. Report client/version,
verified identity/scope, sanitized operation and result, readback, and recovery.
If browser fallback is needed, report its concrete CLI capability reason, verify
the same account/target in the UI, use visible controls, and reopen saved state.
Never expose keys, tokens, authorization data, environment values, or unreviewed logs.
