---
name: excalidraw-scene-operations
description: Create, inspect, update, back up, verify, replace, and soft-delete one exact Excalidraw Plus scene through the REST API. Use when a task targets a single scene or its metadata, elements, files, app state, frames, text, arrows, bindings, or collection assignment. Never use MCP.
---

# Excalidraw Scene Operations

Operate one exact scene through the bundled REST helper. Read
[scene-content-schema.md](references/scene-content-schema.md) before authoring
or changing content and
[single-scene-create-update.md](references/single-scene-create-update.md)
before any write.

## Exact-scene workflow

1. Resolve the collection and scene ID from structured API reads. Do not choose
   the first result unless the user explicitly selected it.
2. Read scene metadata and content.
3. For an existing scene, create a protected pre-change backup outside Git.
4. Validate the proposed JSON locally, including element IDs, finite geometry,
   files, frames, text containers, and connector bindings.
5. Present the exact write and obtain its confirmation.
6. Prefer content PATCH for focused changes. Preserve omitted elements.
7. Use content PUT only for an intentional complete authoritative replacement.
8. Read back metadata and content, then compare exact fields and element IDs.

## Create

Scene creation first creates empty metadata. Adding content is a second write.
If the second write fails, do not silently delete or retry the created scene;
report its canonical ID and offer recovery.

## Update

For an existing element, start from the canonical GET object. Preserve opaque
fields, increment `version`, refresh `versionNonce` and `updated`, and patch the
complete changed element. Higher version wins; equal version uses nonce
tie-breaking. Mark `isDeleted: true` for an intentional element soft-delete.

## Replacement and deletion

PUT removes omitted elements and forces connected editors to reload. DELETE
moves the scene to trash. Both require their stronger approvals. Read
[backup-restore-and-incidents.md](references/backup-restore-and-incidents.md)
for recovery and unknown outcomes.

## Verification

Report the exact scene/collection IDs, metadata before/after, content operation,
element/file counts, protected backup path, canonical readback, and recovery
state. Do not dump private scene content unless the user asked to inspect it.
