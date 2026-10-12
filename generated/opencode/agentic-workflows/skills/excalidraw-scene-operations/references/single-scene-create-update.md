# Single-scene create and update runbook

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

## Create

1. Resolve the exact collection.
2. Prepare a metadata payload outside Git with `name`, `pinned`, and
   `collectionId`.
3. Preview `POST /scenes`; the user's explicit create request authorizes it.
4. Read back the returned scene ID.
5. If content is required, validate a complete scene document and execute
   `PUT /scenes/{sceneId}/content` without requesting another confirmation.
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
omitted-element removal and editor reload, then execute within the user's
explicit update request.
