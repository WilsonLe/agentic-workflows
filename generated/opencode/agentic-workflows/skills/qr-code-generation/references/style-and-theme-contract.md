# Style and theme contract

## Safe v1 surface

Version 1 uses square QR modules and deterministic colors. Themes may change:

- dark and light module colors;
- finder-pattern colors when they preserve the same contrast;
- the opaque QR field, frame, border, and surrounding background;
- optional bounded logo treatment when error correction is `H` and the final
  raster still decodes.

Non-square modules, transparent modules, arbitrary gradients, text inside the
QR field, and decorative overlays over modules are not v1 features. They need a
separate renderer and decoder-tested acceptance matrix.

## Built-in themes

| Theme | Module colors | Surrounding treatment | Image generation |
| --- | --- | --- | --- |
| `minimal` | near-black on white | none | no |
| `editorial` | ink green on paper | restrained frame | optional |
| `botanical` | forest green on warm paper | natural outer background | optional |
| `night` | navy on near-white QR field | dark outer background | optional |
| `festival` | plum on warm white | bold outer frame | optional |

The helper resolves each theme to explicit hex colors. It rejects malformed
colors, transparent QR modules, and an unsafe border below four modules.

## Contrast and geometry

- Keep a four-module quiet zone by default.
- Keep the QR safe area opaque and visually separate from generated artwork.
- Use bounded scale and canvas dimensions; do not create unbounded raster output.
- Keep finder, timing, alignment, format, version, and data modules under the
  encoder's control.
- If a custom style has insufficient contrast or the final decoder fails, reject
  it rather than weakening the verification gate.

## Logo treatment

A logo must be user-owned or appropriately licensed. It is optional, must use
error correction `H`, and is bounded to a small center area with a light patch
that does not move the QR or quiet zone. Logo output is accepted only after the
real decoder returns the exact payload. SVG logo composition is not supported
in v1; request PNG when a logo is required.
