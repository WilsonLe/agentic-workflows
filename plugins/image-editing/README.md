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
4. Measures luminance, clipping, RGB balance, saturation, edge energy, and nine
   composition zones.
5. Writes an explicit JSON recipe with bounded numeric changes.
6. Supports any finite canvas rotation, including exact quarter-turns, after
   metadata auto-orientation and without padding invented pixels.
7. Derives and previews geometric or seed-connected Lab/Luv color-similarity
   masks, including binary fill, outline, feathered alpha, overlay, morphology,
   and bounded mask combinations.
8. Applies the recipe with ImageMagick while preserving the original. Optional
   adjustment layers duplicate the current composite, apply one justified
   correction, and blend it back through a source-derived alpha mask.
9. Re-measures the output, records hashes and commands in a sidecar, and requires
   visual before/after verification.

## Requirements

- Codex image viewing
- ImageMagick 7 (`magick`)
- Python 3.10 or newer; no third-party Python packages

See `skills/food-image-editing/SKILL.md` for the agent workflow. Reusable HTML
report templates are under `skills/food-image-editing/templates/`.
