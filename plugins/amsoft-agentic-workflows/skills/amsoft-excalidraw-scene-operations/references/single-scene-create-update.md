# Single-scene create and update runbook

## Create

1. Resolve the exact collection.
2. Prepare a metadata payload outside Git with `name`, `pinned`, and
   `collectionId`.
3. Preview and approve `POST /scenes`.
4. Read back the returned scene ID.
5. If content is required, validate a complete scene document and separately
   approve `PUT /scenes/{sceneId}/content`.
6. Read metadata and content back. If population fails, preserve the empty
   scene and report recovery; do not auto-delete it.

## Metadata update

Use `PATCH /scenes/{sceneId}` with only intended `name`, `pinned`, or
`collectionId`. Moving collections may affect access. Back up first and verify
each field through GET.

## Content patch

Use `PATCH /scenes/{sceneId}/content` for additions, focused element updates,
element soft deletion, app-state changes, or file additions. Omitted elements
and files remain. Concurrent editor activity may temporarily diverge; always
read back canonical content.

## Content replacement

Use PUT only for a complete restore or deliberate authoritative generation.
Validate the complete document, preserve a protected backup, warn about
omitted-element removal and editor reload, and obtain replacement approval.
