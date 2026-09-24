# Excalidraw render and review loop

Use this read-only loop whenever a scene is generated or materially revised. It
keeps visual inspection local and reversible, before any Excalidraw REST write.

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

For a canonical remote scene, capture the read-only API response into the
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
6. For an existing remote scene, create the protected pre-change backup only
   after the candidate is ready for the write, then use the smallest sufficient
   PATCH or an intentional complete PUT.
7. Read the canonical scene back after the write and render that readback once
   more. Treat any difference as a write/readback issue, not as a reason to
   silently retry a write.

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

Rendering is a rehearsal/inspection step. The final scene operation still
follows the scene workflow: resolve the exact target, preserve the backup,
validate the complete or partial payload, execute the authorized REST method,
read back canonical content, compare IDs and counts, and report the recovery
state.
