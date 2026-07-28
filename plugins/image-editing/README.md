# Image Editing

A Codex plugin for evidence-backed curation, critical review, and
non-generative editing of food images.

The first release is deliberately narrow: food photographs and still frames used
in food videos. It does not generate, replace, reconstruct, extend, or invent
content. Every output is derived from pixels already present in the input through
crop, rotate, resample, tone, color, sharpening, and masked duplicate-layer
operations.

## What it does

1. Inventories and visually inspects every curation candidate, ranks each frame
   within its angle, and records an image-specific selection reason.
2. Produces one concise main HTML curation report for the shoot or menu plus a
   linked detailed report for each reviewed dish. The main report shows current
   selections; dish reports show every candidate and the full ranking evidence.
3. Visually inspects the source and identifies the food, camera angle, intended
   focal point, distractions, crop risks, and problems that cannot be repaired in
   post-production.
4. Builds an auditable composition brief, compares viable crop hypotheses, and
   uses angle, aspect-purpose, crop, and rotation/perspective decision matrices.
5. Measures luminance, clipping, RGB balance, saturation, edge energy, and nine
   composition zones.
6. Writes an explicit JSON recipe with bounded numeric changes.
   It also exposes a complete adjustment brief for lightness, contrast, warmth,
   tint, saturation, curves, eight-band HSL, fade, highlights, shadows, explicit
   color tint, hue, vignette, sharpen, Grain, and Film Grain, with an evidence-led
   combination guide.
7. Supports any finite canvas rotation, including exact quarter-turns, after
   metadata auto-orientation and without padding invented pixels.
8. Supports a schema-version-3 four-corner perspective crop for truthful planar
   rectification, followed by an ordinary delivery crop. It rejects concave,
   self-intersecting, misordered, non-finite, and out-of-bounds geometry.
9. Derives and previews geometric or seed-connected Lab/Luv color-similarity
   masks, including binary fill, outline, feathered alpha, overlay, morphology,
   and bounded mask combinations.
10. Applies the recipe with ImageMagick while preserving the original. Optional
   adjustment layers duplicate the current composite, apply one justified
   correction, and blend it back through a source-derived alpha mask.
11. Re-measures the output, records hashes, geometry, and commands in a sidecar, and requires
   visual before/after verification.

The plugin never uses seam carving, content-aware expansion, liquify, local or
mesh warping, or any technique that moves or reshapes food, plates, hands, or
props. A requested geometric change beyond global rotation and defensible planar
rectification requires another source frame or a reshoot.

## Requirements

- Codex image viewing
- ImageMagick 7 (`magick`)
- Python 3.10 or newer; no third-party Python packages

See `skills/food-image-editing/SKILL.md` for the agent workflow and
`skills/food-image-editing/references/adjustment-parameter-guide.md` for the
control vocabulary and Grain-versus-Film-Grain matrix. See
`skills/food-image-editing/references/composition-and-geometric-editing.md` for
composition, crop, aspect-ratio, and perspective-crop matrices. Reusable HTML
report templates are under `skills/food-image-editing/templates/`.
