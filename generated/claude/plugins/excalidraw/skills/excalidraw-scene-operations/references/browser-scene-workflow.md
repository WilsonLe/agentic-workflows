# Browser scene workflow

Use [browser selection](browser-selection.md) for Excalidraw canvas work. In
Codex, prefer the in-app browser whenever its supported controls can complete
the requested interaction and verification. Honor an explicit browser or tab
choice. Use only documented host controls and observed editor controls; do not
manipulate hidden application state or send API requests from page scripts.

1. Resolve the exact scene URL or local file, account/workspace when applicable,
   and requested change. Inspect that target in the selected browser. A local
   canvas and an Excalidraw Plus saved scene have different persistence targets;
   keep them distinct.
2. Preflight required canvas controls, import/export, backup, and save/readback
   capabilities before editing. Browser work does not require an API key unless
   a necessary structured operation uses the REST helper.
3. Preserve a protected pre-change export or API backup outside Git for an
   existing scene. If no supported backup path exists, report that limitation
   before making a change that requires the backup. Keep unrelated tabs and
   scenes untouched.
4. Make the smallest authorized change through visible editor controls. The
   user's exact-scene create/update request covers ordinary editing and saving;
   replacement and deletion retain their existing backup and approval rules.
5. Inspect the rendered canvas for layout, clipping, overlap, text wrapping,
   arrows, bindings, frames, background, and image placement. Revise within the
   requested scope until the visual result is acceptable.
6. Confirm persistence at the intended target: observe save completion and
   reopen the same saved scene, or export and verify the intended local file.
   Inspect the canvas again after readback. A screenshot or an earlier editor
   state alone does not prove the result was saved.

If a required interaction or structural assertion is unavailable, record the
capability gap and use the REST workflow or local renderer where it proves the
same claim. Preserve exact IDs, JSON validation, backup, canonical readback,
and render/review requirements for that route. Never relabel local rendering
as live browser verification, silently weaken a required claim, or retry a
write with an unknown outcome. Report unavailable proof as a limitation.
