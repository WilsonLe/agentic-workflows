---
name: excalidraw-scene-operations
description: Create, inspect, update, back up, verify, replace, and soft-delete one exact Excalidraw scene, preferring the Codex in-app browser for supported canvas work and visual verification, with the REST helper for structured Excalidraw Plus operations. Never use MCP.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Optional: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Optional: Excalidraw API access** — Configure a scoped Excalidraw key in the protected local store when using REST operations; browser-only canvas work uses the authorized browser session.
- **Optional: Scene preview tools** — Install Node.js 18 or newer, npx, and Playwright Chromium when rendering local scene previews.

<!-- catalog-prerequisites:end -->

# Excalidraw Scene Operations

Prefer the Codex in-app browser for supported Excalidraw canvas work, including
viewing, creating, editing, and visually verifying a scene. Follow
[browser selection](references/browser-selection.md) and
[browser scene workflow](references/browser-scene-workflow.md). Use the bundled
REST helper when structured Excalidraw Plus operations are required or the browser
cannot safely complete the requested work. For REST content work, read
[scene-content-schema.md](references/scene-content-schema.md) before authoring
or changing content and
[single-scene-create-update.md](references/single-scene-create-update.md)
before any write. Read
[render-review-loop.md](references/render-review-loop.md) whenever scene JSON is
generated or materially revised for a REST write.

## Exact-scene REST workflow

1. Resolve the collection and scene ID from structured API reads. Do not choose
   the first result unless the user explicitly selected it.
2. Read scene metadata and content.
3. For an existing scene, create a protected pre-change backup outside Git.
4. Validate the proposed JSON locally, including element IDs, finite geometry,
   files, frames, text containers, and connector bindings.
5. Render the complete candidate to PNG and inspect the actual image. Repeat
   the render/review/revise loop until the visual candidate is acceptable.
6. Present the exact write. The user's request to create or change that exact
   scene authorizes the non-destructive operation; do not ask for a typed token
   or a second confirmation.
7. Prefer content PATCH for focused changes. Preserve omitted elements.
8. Use content PUT only for an intentional complete authoritative replacement.
9. Read back metadata and content, then compare exact fields and element IDs.

## Render and review

Use the separate read-only renderer from
[render-review-loop.md](references/render-review-loop.md) before every
material REST scene-content write. Rendering a PATCH fragment alone is invalid;
merge the candidate with the complete canonical scene first. After a successful REST write,
render the canonical readback once more so visual evidence is tied to the
content that Excalidraw actually stored.
For browser canvas work, inspect the actual rendered canvas and confirm saved
state through the browser scene workflow. A local PNG or API response alone
does not prove the live editor displays the intended result.

## REST create

Scene creation first creates empty metadata. Adding content is a second write.
If the second write fails, do not silently delete or retry the created scene;
report its canonical ID and offer recovery.

## REST update

For an existing element, start from the canonical GET object. Preserve opaque
fields, increment `version`, refresh `versionNonce` and `updated`, and patch the
complete changed element. Higher version wins; equal version uses nonce
tie-breaking. Mark `isDeleted: true` for an intentional element soft-delete.

## REST replacement and deletion

PUT removes omitted elements and forces connected editors to reload, so verify
the full payload and backup before writing, but do not request a second
confirmation. DELETE moves the scene to trash and retains the destructive
approval gate. Read
[backup-restore-and-incidents.md](references/backup-restore-and-incidents.md)
for recovery and unknown outcomes.

## Verification

For REST work, report the exact scene/collection IDs, metadata before/after, content operation,
element/file counts, protected backup path, canonical readback, and recovery
state. Do not dump private scene content unless the user asked to inspect it.
Record the actual browser/API channel and any fallback reason. For browser
work, report the observed URL or local file, saved-state readback, visual result,
and any fields that the supported UI cannot verify.
