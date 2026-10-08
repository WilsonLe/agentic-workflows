# Excalidraw browser scene workflow

Read [service browser operations](browser-selection.md). In Codex, use the
built-in browser and visible editor/management controls as the base.

1. Verify signed-in account/workspace and exact collection/scene URL for the
   current project. A local canvas/file and a saved Plus scene are different
   persistence targets; do not confuse them.
2. Preflight supported canvas interactions, import/export, backup, and save/reopen.
   Browser work needs no personal API key. Report missing required capabilities.
3. Preserve a protected UI export outside Git before an existing-scene change
   that needs recovery. Verify the export and exact scene association.
4. Make the smallest authorized canvas/metadata change. Preserve unrelated elements
   and concurrent edits. Use complete imports only for intentional replacement.
5. Inspect the actual canvas: layout, clipping, overlap, wrapping, connectors,
   bindings, frames, background, and image placement. Revise within scope.
6. Observe save completion and reopen the same saved scene; inspect the canvas
   again. For an intended local export, verify that exact file instead.

A screenshot/local preview does not prove persistence. Optional protected reads
or local rendering can supplement diagnosis/preparation but cannot replace live
save verification. Do not send page-script API requests or manipulate hidden state.
If the UI cannot complete the management action, disclose the exact gap and obtain
explicit user direction for a non-browser mutation. Unknown outcomes need readback
before retry; do not create duplicate scenes or force full replacement.
