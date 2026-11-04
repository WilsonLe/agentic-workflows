# Scene content schema

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate with the host's browser controls or a
user-completed login when needed, and use browser operations only for an
authenticated client capability gap.

A complete document contains:

- `type: "excalidraw"`
- numeric `version`
- string `source`
- `appState`
- `elements`
- `files`
- server-managed `sceneVersion` on reads

Persisted element types are rectangle, diamond, ellipse, embeddable, frame,
magicframe, iframe, image, text, line, arrow, and freedraw. `selection` is
editor-only.

Every element uses stable ID, geometry, style, ordering/reconciliation,
lifecycle, grouping/framing, and link fields. Treat IDs, indices, versions,
nonces, and `sceneVersion` as opaque canonical fields.

Important integrity rules:

- `frameId` points to a frame or magicframe; coordinates stay absolute.
- Shape labels are separate text elements linked through `containerId` and
  `boundElements`.
- Arrow/line bindings reference real bindable elements and use `inside`,
  `orbit`, or `skip`.
- Image `fileId` values reference records in `files`.
- Points and geometry contain finite numeric values.

The protected client and local renderer accept only `viewBackgroundColor` and
`lockedMultiSelections` in `appState`. Arrow and line bindings are objects with an
existing `elementId`, a `mode` of `inside`, `orbit`, or `skip`, an optional
`fixedPoint`, and a matching `boundElements` entry on the target. Files exported from
excalidraw.com may carry other `appState` keys such as `gridSize` or legacy
`focus`/`gap` bindings; preview a normalized temporary copy, never the user's file.

PATCH accepts any non-empty subset of elements, appState, and files. PUT
requires a complete document. `filesFailedToEmbed` is read-compatible but
ignored on writes.

Full official reference:
https://plus.excalidraw.com/docs/api/scene-content-schema
