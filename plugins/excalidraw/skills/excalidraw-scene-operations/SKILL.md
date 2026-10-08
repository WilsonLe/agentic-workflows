---
name: excalidraw-scene-operations
description: Create, inspect, edit, back up, verify, replace, and delete one exact Excalidraw scene through the built-in Codex browser. Select the project account/workspace, use visible canvas and management controls, and verify saved state; local previews and optional read-only helpers supplement browser operation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Optional: Excalidraw account** — Sign in to the intended workspace for saved Plus scenes; local canvas/file work needs no account or API token.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.
- **Optional: Local scene preview tools** — Install Python 3, Node.js 18 or newer, npx, and Playwright Chromium only for local JSON previews.

<!-- catalog-prerequisites:end -->

# Excalidraw Scene Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.

Read [browser scene workflow](references/browser-scene-workflow.md) before canvas
work and [single-scene create/update](references/single-scene-create-update.md)
before writing. Use `excalidraw-api-operations` for workspace/account administration.

## Exact-scene workflow

1. Verify the project account/workspace and resolve the exact collection and
   scene URL. Do not choose the first result or confuse a local canvas with a
   saved Plus scene.
2. Inspect metadata and the actual rendered canvas. Preflight supported editing,
   import/export, backup, save, and reopen controls before changing it.
3. For an existing scene, preserve a protected UI export outside Git before a
   change that needs recovery. Read [backup and recovery](references/backup-restore-and-incidents.md).
4. Make the smallest authorized edit through visible canvas or management controls.
   Use a deliberate complete import only for an authorized replacement after backup.
5. Inspect layout, clipping, text wrapping, arrows, bindings, frames, and images.
6. Observe save completion, reopen the same saved scene, and inspect the canvas
   again. For a requested local export, verify the exact output file instead.
7. Report saved-state readback, visual result, exact target, and recovery status.

The user's exact-scene edit request covers ordinary editing and saving. Deletion,
sharing, and replacement require authority for their actual effects. Preserve
concurrent edits; do not overwrite unrelated elements to force a planned result.
An unknown save outcome needs readback before retry, never a duplicate creation.

## Local preparation and optional diagnostics

When authoring/importing scene JSON, read
[scene content schema](references/scene-content-schema.md) and
[render review loop](references/render-review-loop.md). Local validation/rendering
is preparation only; it does not prove the live scene was saved. Deliver remote
changes through browser import/editor controls and verify persistence there.
Protected helper reads can supply metadata/content only after independent identity
and target matching. They do not authorize REST writes. A missing browser control
must be reported; any non-browser mutation requires explicit user direction.

Keep private scene content and backups outside Git. Report structural assertions
that the UI cannot verify as limitations; never substitute a local PNG or API
acknowledgement for the requested live evidence.
