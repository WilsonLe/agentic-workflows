---
name: excalidraw-scene-operations
description: Create, inspect, update, back up, verify, replace, and soft-delete one exact Excalidraw scene through the authenticated protected command-line client. Use the built-in Codex browser for missing personal-key authentication and only fall back to browser operations for unsupported client capabilities or live canvas verification.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Optional: Authenticated service CLI** — Use Protected Excalidraw command-line client; verify authentication and exact project account/target before remote operations. Local preparation needs no remote authentication.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.
- **Optional: Local scene preview tools** — Install Python 3, Node.js 18 or newer, npx, and Playwright Chromium for local scene previews; local preparation needs no account.

<!-- catalog-prerequisites:end -->

# Excalidraw Scene Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

For remote Plus scenes, apply `excalidraw-api-operations` for authentication and
exact account/workspace matching. Read [scene content schema](references/scene-content-schema.md),
[single-scene create/update](references/single-scene-create-update.md), and
[render review loop](references/render-review-loop.md) before material content writes.

## Exact-scene client workflow

1. Resolve the exact collection/scene from authenticated reads; do not choose the first result.
2. Read canonical metadata/content and preserve a protected pre-change backup outside Git.
3. Validate complete proposed content locally: IDs, geometry, files, frames, text,
   and bindings. Render the complete candidate and inspect the PNG; revise as needed.
4. Preview the exact write, impact, authority, readback, and recovery. Prefer focused
   PATCH; use authoritative PUT only for an intentional complete replacement.
5. Execute through the protected authenticated command-line client, read back
   canonical metadata/content, compare intended fields/IDs, and render saved content.
6. If scene creation succeeds but population fails, preserve the scene and report
   partial outcome/recovery; do not auto-delete or create a duplicate.

DELETE retains exact-resource destructive approval. Preserve opaque fields and
concurrent edits; unknown outcomes need readback before retry. Read
[backup and recovery](references/backup-restore-and-incidents.md) when needed.

## Browser capability fallback and local work

For unsupported canvas interactions or live editor verification that the client
cannot prove, record the exact capability reason and follow
[browser scene workflow](references/browser-scene-workflow.md). Verify the same
account/workspace/scene, use visible controls, observe save, and reopen the scene.
A local PNG or API acknowledgement alone is not live editor/persistence evidence.

Local JSON validation/rendering requires no account. For an explicitly local
canvas/file task with no remote client equivalent, document that capability scope
and use supported browser controls; verify the intended output/persistence target.


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
