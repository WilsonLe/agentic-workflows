# Image generation and compositing

## Boundary

The host image capability may create visual material around a QR. It must not
draw a QR, encode payload text, or be used as verification. The helper owns the
QR pixels and the final composite.

Use a prompt like:

```text
Create a [THEME] background for a QR asset. Keep a clean, opaque, quiet visual
field in the center labelled [QR SAFE AREA]. Do not draw any QR code, barcode,
encoded text, logos, letters, numbers, or high-contrast square grid inside or
near that safe area. Use [PALETTE], [TEXTURE], and [FRAME] outside the safe
area only.
```

Never substitute a raw URL or secret payload for `[QR SAFE AREA]`. The prompt
may include the user's visual brief, but not the value being encoded.

## Workflow

1. Render and verify the deterministic baseline.
2. Generate or select the background with the host capability only when the user
   asks for it and the input/reference is authorized.
3. Inspect the returned image for unintended text, logos, grids, or a second QR.
4. Run `compose`; the helper crops the background to the requested canvas,
   places the unchanged QR PNG in the center, and draws any frame outside it.
5. Run `verify` on the composite. A decode mismatch is a rejected variant.

Generated artwork is a theme input, not a source of truth. Keep its prompt and
provenance separate from QR payload identity. If image generation is unavailable,
return a deterministic theme or an explicit `image_capability_unavailable`
status; do not claim the visual route ran.
