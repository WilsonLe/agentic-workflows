# Browser single-scene create and update

Apply [browser scene workflow](browser-scene-workflow.md).

## Create

Verify account/workspace/collection, use the observed UI create control, record
the resulting scene URL, and edit/import through supported editor controls.
If creation succeeds but content population fails, preserve that scene and report
partial completion and recovery; do not auto-delete it or create another.

## Metadata and canvas updates

Open the exact scene, preserve a protected export when recovery is needed, and
use visible rename/move/pin/sharing or canvas controls. Moving/sharing can affect
access and needs exact-effect authority. Preserve unrelated and concurrent content.
Observe save completion, reopen the same scene, and compare metadata/canvas.

## Complete replacement

Use a supported UI import/replace only for an intentional complete replacement.
Validate/render local JSON when authored, verify backup, preview removal of omitted
content, and preserve existing task authority. A merge-import is not proof of full
replacement; inspect its actual behavior. If the UI cannot prove the required
replacement, report the gap before any explicitly directed alternative channel.

REST PATCH/PUT/POST is not the default scene workflow. Read-only helper authority
does not authorize a remote content write.
