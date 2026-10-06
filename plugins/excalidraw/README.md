# Excalidraw

Agentic Workflows Excalidraw plugin, preferring the Codex in-app browser for
supported canvas work and visual verification, with REST helpers for structured
Excalidraw Plus operations.

The scene workflow includes a read-only local render/review loop so generated
content can be inspected as a PNG and revised before a remote write.

## Boundary

Browser steps, including canvas viewing/editing, account setup, and credential
creation, follow the shared [browser selection](skills/excalidraw-scene-operations/references/browser-selection.md)
preference. Explicit browser choices take precedence. The
[browser scene workflow](skills/excalidraw-scene-operations/references/browser-scene-workflow.md)
requires a protected backup, visual inspection, and saved-state readback.

Structured operations use the public REST API at
`https://api.excalidraw.com/api/v1`. It does not install, configure, or call
MCP.

The REST credential contract accepts only a user-confirmed **personal
MCP/API key**. Personal keys act as the member and can access that member's
private collection. Workspace keys are outside this release.

Never paste a key into chat or commit it. Onboarding accepts a local path,
installs a protected record at
`~/.config/agentic-workflows/excalidraw/credentials.json`, verifies a bounded read-only
collections request, and only then archives the original source.

## Primary workflow

For supported canvas work, use the Codex browser workflow linked above.
The REST workflow operates one exact Excalidraw Plus scene:

1. Resolve its collection and scene ID from structured reads.
2. Read metadata and content.
3. Create a protected pre-change backup for an existing scene.
4. Validate and render the complete candidate, then inspect and revise it until
   the visual review is acceptable.
5. Preview the exact method, target, impact, verification, and recovery.
6. Treat the user's explicit request as authorization for the non-destructive
   write; do not ask for a typed token or second confirmation.
7. Prefer an incremental content `PATCH`; reserve authoritative `PUT` for a
   reviewed complete replacement.
8. Read back canonical metadata and content, then render the canonical readback
   once more.

## Local scene preview

Install Playwright Chromium once on the host:

```bash
npx --yes playwright install chromium
```

Render a complete scene document or the JSON response produced by the
read-only `scene-content` operation:

```bash
python3 scripts/excalidraw_render.py \
  /protected/tmp/scene-response.json \
  /protected/tmp/scene-preview.png
```

The helper validates the complete scene, extracts API-helper envelopes, invokes
the pinned `excalidraw-export-cli@1.0.0` renderer, verifies the PNG signature,
and prints only a secret-free count/path summary. Keep candidate JSON, embedded
files, and previews outside Git. See
[render-review-loop.md](skills/excalidraw-scene-operations/references/render-review-loop.md)
for the full revision loop, the one-time global install option for faster
iterations, and the final-write boundary.

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
