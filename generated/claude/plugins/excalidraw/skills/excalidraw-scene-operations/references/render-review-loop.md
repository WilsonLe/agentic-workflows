# Excalidraw render and review loop

Use this read-only loop whenever scene JSON is generated or materially revised
for a browser import or other explicitly directed write. It keeps visual inspection local and reversible before that
write. For supported canvas work and live visual verification, prefer the Codex
in-app browser via [browser scene workflow](browser-scene-workflow.md) and
[browser selection](browser-selection.md). The headless renderer below remains
the local PNG export path; it does not replace live browser evidence.

## Boundary

- The renderer accepts one complete Excalidraw scene document or the JSON
  envelope printed by `<plugin-root>/scripts/excalidraw_api.py scene-content`.
- A PATCH fragment is not renderable by itself. Start from the canonical scene,
  apply the proposed patch locally, and render the resulting complete document.
- Rendering does not create, update, replace, or delete a remote scene.
- A PNG proves only the rendered candidate. It does not prove that a remote
  scene contains the same content.
- Keep candidate JSON, embedded files, and preview PNGs in a protected
  task-owned temporary directory outside Git. Do not paste private scene data
  into chat or commit generated previews unless separately requested.

## Prerequisites

The default renderer is the pinned npm package excalidraw-export-cli@1.0.0. It
uses headless Chromium and requires Node.js 18 or newer, `npx`, and a local
Playwright Chromium installation:

```bash
npx --yes playwright install chromium
```

For frequent iterations, install the same pinned package once and use its
executable directly. This avoids repeated npm package resolution:

```bash
npm install --global excalidraw-export-cli@1.0.0
python3 <plugin-root>/scripts/excalidraw_render.py \
  /path/to/candidate.json \
  /path/to/preview.png \
  --renderer-bin excalidraw-export
```

If a compatible locally installed renderer is preferred, pass its executable
with `--renderer-bin`. It must accept the input `.excalidraw` path and output
PNG path as its two positional arguments.

## Render a candidate

The helper validates element IDs, geometry, frames, text containers, bindings,
image file references, and the complete top-level scene shape before invoking
the external renderer. It never prints the scene document.

```bash
python3 <plugin-root>/scripts/excalidraw_render.py \
  /path/to/candidate.json \
  /path/to/preview.png
```

If an optional protected read-only diagnostic independently matches the browser
identity and target, capture its scene response into the
protected temporary directory and let the helper extract the `result` object:

```bash
work_dir="$(mktemp -d /tmp/excalidraw-review.XXXXXX)"
candidate="$work_dir/scene-response.json"
preview="$work_dir/scene-preview.png"

python3 <plugin-root>/scripts/excalidraw_api.py scene-content \
  --scene-id "$SCENE_ID" > "$candidate"
python3 <plugin-root>/scripts/excalidraw_render.py "$candidate" "$preview"
```

The helper prints a small JSON summary containing only element/file counts and
the output path. Inspect the actual PNG with the available visual review
capability before deciding that the candidate is acceptable.

## Repeatable revision loop

1. Generate or edit one complete candidate document outside Git.
2. Run the renderer and inspect the PNG at its actual output dimensions.
3. Check layout, clipping, overlap, text wrapping, arrow direction and
   bindings, frame membership, background, image placement, and overall visual
   hierarchy.
4. Classify the smallest required correction, update only that candidate, and
   render again.
5. Repeat until the visual review is acceptable. A successful command without
   visual inspection is not a completed review.
6. For an existing remote scene, preserve a protected UI export before editing.
   Import/edit through supported browser controls using the smallest intended change.
7. Reopen the saved browser scene and inspect its canvas. Render a verified UI
   export when needed; treat differences as persistence issues, not permission to retry.

## Failure handling

- Invalid or partial JSON stops before the renderer starts.
- A missing `npx`, browser, renderer, or network dependency is a local preview
  blocker; report it and do not substitute API output for visual evidence.
- Renderer timeout or non-zero exit stops the loop. Do not write the remote
  scene from an unrendered candidate.
- A PNG that cannot be read as PNG is a failed render even when the process
  exits successfully.
- Renderer and browser diagnostics may be retained for local diagnosis, but
  must remain outside Git and free of credentials or private scene content.

## Final write boundary

Rendering is preparation only. Perform remote creation, editing, replacement,
and recovery through supported browser controls, then reopen and verify the exact
saved scene. Report missing UI capabilities; use a non-browser mutation only under
explicit user direction after explaining that gap. Optional helper reads and local
PNGs do not prove live persistence or authorize API writes.
