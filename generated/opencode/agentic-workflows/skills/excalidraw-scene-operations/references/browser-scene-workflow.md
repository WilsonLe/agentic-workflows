# Browser scene workflow

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

Use this runbook only after the authenticated protected command-line client
cannot perform the requested canvas action or prove required live visual behavior.
Record that exact capability limitation first. Missing authentication is not a
fallback reason; use browser-assisted credential setup and verify the client.
Follow [channel selection](browser-selection.md), using the built-in Codex browser
for the justified fallback and only documented host/visible editor controls.
Never manipulate hidden application state or send page-script API requests.

1. Resolve the exact scene URL or local file, account/workspace when applicable,
   and requested change. Inspect that target in the selected browser. A local
   canvas and an Excalidraw Plus saved scene have different persistence targets;
   keep them distinct.
2. Preflight required canvas controls, import/export, backup, and save/readback
   capabilities before editing. For saved Plus scene fallback, the remote client
   must already be authenticated; a browser session alone does not prove its
   account matches. Explicitly local canvas/file work needs no remote account.
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

If a required browser interaction or assertion is unavailable too, report the
concrete blocker. Do not weaken evidence or overwrite hidden state. For later
operations supported by the authenticated client, return to CLI execution. Never
relabel local rendering as live verification or retry an unknown write outcome.
