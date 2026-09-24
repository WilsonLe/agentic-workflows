# Scene content schema

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

PATCH accepts any non-empty subset of elements, appState, and files. PUT
requires a complete document. `filesFailedToEmbed` is read-compatible but
ignored on writes.

Full official reference:
https://plus.excalidraw.com/docs/api/scene-content-schema
