# Excalidraw

AMSoft's API-first Excalidraw Plus plugin for Codex.

## Boundary

This plugin uses the public REST API at
`https://api.excalidraw.com/api/v1`. It does not install, configure, or call
MCP.

The initial credential contract accepts only a user-confirmed **personal
MCP/API key**. Personal keys act as the member and can access that member's
private collection. Workspace keys are outside this release.

Never paste a key into chat or commit it. Onboarding accepts a local path,
installs a protected record at
`~/.config/amsoft/excalidraw/credentials.json`, verifies a bounded read-only
collections request, and only then archives the original source.

## Primary workflow

The focused workflow operates one exact scene:

1. Resolve its collection and scene ID from structured reads.
2. Read metadata and content.
3. Create a protected pre-change backup for an existing scene.
4. Preview the exact method, target, impact, verification, and recovery.
5. Treat the user's explicit request as authorization for the non-destructive
   write; do not ask for a typed token or second confirmation.
6. Prefer an incremental content `PATCH`; reserve authoritative `PUT` for a
   reviewed complete replacement.
7. Read back canonical metadata and content.

Writes with an unknown outcome are never blindly retried. Authoritative scene
replacement requires full validation and backup but no second confirmation.
Soft deletion retains a typed destructive approval.

## First prompt

```text
Use Excalidraw API Operations to onboard my personal API key from a local file.
Verify it read-only and do not create or change a scene.
```

The Excalidraw Plus API is in public beta. The skills link to the current
official documentation and fail closed when critical response shapes drift.
