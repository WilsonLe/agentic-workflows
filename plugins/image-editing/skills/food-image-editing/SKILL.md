---
name: food-image-editing
description: Critically review, curate, report on, and non-generatively edit food photographs or food-video stills, including shortlist ranking, per-dish and main HTML curation reports, crop and composition, color and tone correction, duplicate-current adjustment layers, geometric masks, color-similarity masks, outline and alpha-mask previews, mask cleanup and combination, provenance, and visible verification. Use for setup or when the user asks to shortlist, curate, rank, report on, edit, improve, grade, mask, isolate by color, outline, composite, layer, crop, color-correct, prepare, or critique food images. Never use image generation, generative fill, object replacement, synthetic backgrounds, or outpainting.
---

# Food Image Editing

Produce a better food image without inventing a single pixel of scene content.
This skill is food-only in version 0.1. Read
[references/research-and-guardrails.md](references/research-and-guardrails.md)
before the first edit in a task or whenever choosing numeric targets.

For setup, onboarding, or first-use requests, read
[references/onboarding.md](references/onboarding.md), verify the prerequisites, and stop before
editing unless the user explicitly asks to continue.

For multi-image selection, shoot curation, candidate ranking, or HTML report
requests, read
[references/photo-curation-reporting.md](references/photo-curation-reporting.md)
before creating or changing the shortlist.

## Absolute boundary

- Never call an image-generation tool while using this skill.
- Never use generative fill, inpainting, outpainting, object replacement,
  synthetic steam, synthetic garnish, background generation, relighting models,
  face restoration, super-resolution models, or content-aware crop expansion.
- Allowed operations are deterministic transformations of input pixels: metadata
  orientation, rotate, crop, resize, white-balance gains, exposure, levels,
  contrast, saturation, local masked adjustments using the same source pixels,
  masked duplicate-layer stacks, denoise, and conventional sharpening.
- Keep the original unchanged. Write a new output and a JSON provenance sidecar.
- `rotate_deg` accepts any finite degree value. The helper normalizes full turns
  modulo 360, supports exact quarter-turns, auto-orients metadata before
  rotation, and crops only to source-supported pixels.
- If the photograph needs a different viewpoint, missing plate edge, different
  styling, moved prop, restored blown highlight, or sharper focus, say that it
  needs a reshoot. Do not fake the repair.

## Photo curation and reporting

Treat curation as an evidence-producing workflow, not a list of unexplained
favorites.

1. Establish the dish label and its confidence. Preserve `confirmed`,
   `probable`, `unconfirmed`, or `TBD` exactly as the supplied evidence supports.
2. Inventory every candidate and inspect the actual pixels. Group candidates by
   requested angle and keep uncertain angle assignments visible.
3. State the delivery aspect ratio and composition constraints before ranking.
   Reject a source that cannot satisfy them without inventing pixels or damaging
   the dish presentation.
4. Rank every candidate within its angle. Give each frame a concise,
   image-specific reason covering focus, food texture, plating, orientation,
   crop room, reflections, distractions, and redundancy where relevant.
5. Select the requested number per angle. Choose complementary editing sources,
   not merely the highest-scoring near-duplicates. Record approved rotations and
   unavailable angles explicitly.
6. Create or update one main HTML curation report for the whole shoot or menu.
   It is the navigation and current-selection surface: dish label, label status,
   selected frames by angle, and a link to the detailed dish report.
7. Create one detailed HTML report per reviewed dish. Show the selected set
   first, then every candidate grouped and ranked by angle with visible
   selection state, exact stem or filename, actual image, and reason.
8. Link the main report and each detailed report in both directions. Keep the
   main report concise; put candidate-by-candidate reasoning only in the dish
   report.
9. Update the machine-readable shortlist or manifest from the same selection
   source. Never hand-copy a second conflicting selection list.
10. Verify rendered layout when the local browser surface permits it. Always
    verify HTML/JavaScript syntax, reciprocal links, image existence, selected
    counts, unique assignments, recorded rotations, and manifest agreement.

Start from
[templates/photo-curation-main-report.html](templates/photo-curation-main-report.html)
and
[templates/photo-curation-dish-report.html](templates/photo-curation-dish-report.html)
when the repository does not already have an established report design.

## Required workflow

1. Establish the purpose. Record output use, aspect ratio, target dimensions,
   whether the still must match adjacent video shots, and any brand look. If the
   user only says “food video,” default to a 9:16 planning crop but do not crop
   until the hero food and motion/text-safe areas are identified.
2. Inspect the actual image visually before proposing edits. Use the local image
   viewer. Identify:
   - dish and truth-critical colors;
   - camera angle with confidence: `overhead`, `three-quarter`, `side`, or
     `macro/detail`;
   - hero food bounding box in normalized coordinates `[x, y, width, height]`;
   - plate/bowl boundary, tallest layer, garnish, gloss/steam cues, utensils,
     hands, clutter, and empty space;
   - lighting direction, mixed-light symptoms, clipped highlights, crushed
     shadows, color casts, focus failure, noise, and lens/perspective problems.
3. Measure the unedited file:

   `python3 scripts/food_image.py analyze INPUT --subject-bbox x,y,w,h --output analysis.json`

   A neutral-patch rectangle may be supplied only when a genuinely neutral object
   is visible:

   `--neutral-bbox x,y,w,h`

   A white plate is not automatically neutral; colored reflections and warm
   ceramic invalidate that assumption.
4. Write the critique before editing. Separate:
   - observed problems;
   - measured evidence;
   - proposed corrections with exact values;
   - angle-specific composition decision;
   - limitations requiring reshoot.
5. Copy [examples/recipe.json](examples/recipe.json) and change only justified
   fields. Use small first-pass moves. There is no universal food preset. Use an
   `adjustment_layers` stack only when one local zone is insufficient and every
   layer has a distinct food-specific purpose.
6. Preview every new mask before editing:

   `python3 scripts/food_image.py mask-preview INPUT --recipe recipe.json --layer LAYER_NAME --output-dir preview/`

   Inspect `binary-mask.png`, `outline.png`, `alpha-mask.png`, and `overlay.png`
   at normal size and 100%. Reduce the threshold, cleanup, or feathering when the
   selection leaks, breaks apart, crosses a truth-critical edge, or looks cut out.
7. Dry-run and inspect the exact command plan:

   `python3 scripts/food_image.py edit INPUT OUTPUT --recipe recipe.json --dry-run`

8. Apply the edit:

   `python3 scripts/food_image.py edit INPUT OUTPUT --recipe recipe.json --report OUTPUT.edit.json`

9. Measure and validate:

   `python3 scripts/food_image.py verify INPUT OUTPUT --recipe recipe.json --output OUTPUT.verify.json`

10. Visually inspect the output beside the original. Confirm believable food
   color, retained highlight texture, natural shadows, correct crop, clean plate
   edges, absence of mask seams or halos, coherent depth between layer zones, and
   consistency with the intended video sequence.
   Iterate once with smaller changes if any correction calls attention to itself.
11. Deliver the edited file, mask previews, recipe, edit report, verification report, and a
    concise explanation of what changed. Never claim “best” from metrics alone.

## Layering, masking, and composition

Layering is an advanced local-correction technique, not permission to build a
new scene. The tool implements a serial adjustment-layer stack. For each layer
it copies the current composite, applies bounded corrections to that copy, and
blends the copy back through a feathered mask. Layers are evaluated in recipe
order, so a later layer sees the result of the earlier layers.

Use the stack only when it solves a visible food-photography problem, such as:

- gently lowering a bright tabletop with an inverted mask while preserving the
  plated food;
- lifting the near-facing food at a three-quarter angle without flattening the
  background;
- protecting sauce gloss while adding restrained texture emphasis to a matte
  food zone;
- balancing separate food regions that are under genuinely different light.

Build the composition in this order:

1. Choose rotation and the canvas crop from the full photograph. Preserve plate
   geometry, food height, text-safe space, and the intended delivery ratio.
2. Apply global white balance and tone only far enough to establish a believable
   base.
3. Add broad background or negative-space layers first.
4. Add the hero-food layer next, using the smallest practical feathered mask.
5. Add garnish, gloss, or texture layers last and at lower opacity.
6. Inspect the complete stack at normal viewing size and at 100%. Reduce or
   remove any layer that creates a halo, flat cutout edge, false sharpness,
   implausible color separation, or competing focal point.

Every `adjustment_layers` entry must include:

- a unique `name` and a concrete `purpose`;
- `source: "duplicate_current"`; no external image or synthetic source;
- `opacity` from `0.05` to `1.0`;
- either a geometric mask or a previewed color-similarity mask;
- at least one non-neutral exposure, contrast, saturation, or sharpening
  correction.

All mask coordinates are normalized against `global_base`: the auto-oriented,
straightened, cropped image after global corrections but before local layers.
The tool derives every mask from that stable base before it evaluates the serial
layer stack, so an earlier color correction cannot silently change a later mask.

Use geometric masks for broad elliptical or rectangular zones. Use a
`color_similarity` mask only when a connected region has a defensible seed color
and can be constrained by an explicit ROI. The implementation uses ImageMagick
fuzz distance in Lab or Luv; it is not CIEDE2000 and cannot identify food
semantics.

A color-similarity mask must define:

- `type: "color_similarity"` and `basis: "global_base"`;
- normalized `seed` and `roi`, with the seed inside the ROI;
- `colorspace: "Lab"` or `"Luv"` and a reviewed `fuzz_percent`;
- bounded `cleanup` values for `open_px`, `close_px`, signed `grow_px`, and
  `feather_px`;
- optional ordered `combine` operations: `intersect`, `union`, or `subtract`
  with non-recursive geometric masks;
- optional final inversion.

Treat mask construction as:

1. select only similar pixels connected to the seed inside the ROI;
2. clean isolated noise with Open and small holes with Close;
3. grow or shrink only when the visible boundary justifies it;
4. intersect to constrain, union to add a known zone, or subtract to protect a
   rim, gloss, garnish, or other truth-critical region;
5. inspect the binary fill and morphological outline;
6. feather the filled selection into alpha and inspect the overlay;
7. apply layer opacity to the alpha mask, then composite the corrected duplicate.

Prefer broad feathering for tone and color transitions; use tighter masks only
when the real scene contains a clear edge such as a plate rim. Keep spill off
boundaries where it would change perceived doneness, freshness, sauce color, or
ingredient identity. An empty selection is an error. Large, fragmented,
high-fuzz, or ROI-touching selections require extra review; warnings do not prove
the mask is wrong or right.

Crop is a canvas-level composition operation and happens before the layer stack.
Do not crop, translate, scale, rotate, or mirror an individual layer to move food
or props. Do not use duplicate layers for cloning, object removal, plate repair,
fake depth of field, synthetic steam, repeated garnish, background replacement,
or reconstructing missing edges. Those changes require a reshoot.

## Angle-aware composition

### Overhead / 90 degrees

- Preserve complete circular plate geometry unless a deliberate close crop is
  stronger and no rim is clipped accidentally.
- Judge pattern, negative space, color blocks, utensil lines, and rotation.
- A 9:16 crop usually needs a vertical ingredient/plate arrangement; do not force
  a centered round plate into a weak narrow crop.
- Do not add perspective correction unless the table plane is visibly skewed.

### Three-quarter / roughly 30–60 degrees

- Preserve both top-surface information and the dish’s front edge.
- Put the sharpest, most textured food near the primary attention zone.
- Avoid cropping the bowl lip through a tangent or hiding the visible height that
  makes this angle useful.
- Use local lift sparingly on the near-facing food if it is readable but dark.

### Side / near eye level

- Preserve height, layers, drips, crumb, and the supporting baseline.
- Crop empty tabletop before sacrificing the vertical silhouette.
- Do not brighten shadows so far that stacked layers lose depth.

### Macro / detail

- Protect the intended focus plane and recognizable context.
- Conventional sharpening cannot repair missed focus or motion blur.
- Texture and specular highlights matter more than showing the whole plate; avoid
  clipping gloss on sauces, oils, fruit, and fresh vegetables.

## Numeric decision rules

Treat the values in the research reference as starting guardrails, not aesthetic
truth. In particular:

- Use percentile and clipping measurements, not histogram shape alone.
- Do not auto-neutralize the whole frame with gray-world assumptions; food scenes
  are often intentionally warm and color-biased.
- Prefer a real neutral patch for RGB gain suggestions. Cap automatic gain
  proposals to `0.80–1.25`; larger changes require visual review.
- Keep output highlight and shadow clipping below `0.5%` by default, and do not
  increase either by more than `0.25` percentage points unless the recipe records
  why specular or silhouette clipping is intentional.
- Begin global exposure changes within `±0.35 EV`, contrast within `±2.0`,
  saturation ratio within `0.90–1.15`, and sharpening amount at or below `1.0`.
  Exceeding those ranges requires explicit evidence in `notes`.
- Never use saturation to compensate for incorrect white balance.
- Prefer a subject-zone correction over a large global move when the background
  is already correct.
- Preserve recognizable dish color. Research supports the importance of
  saturation and luminance distribution to appetite and freshness, but does not
  establish one optimum numeric value for all foods.

## Recipe review

Every recipe must include:

- `purpose`, `angle`, `angle_confidence`, `hero_bbox`, and `notes`;
- a crop derived from actual composition, not aspect ratio alone; crop
  coordinates are relative to the image after straightening;
- all numeric changes, including values deliberately left neutral;
- local-zone coordinates after crop;
- layer order, names, purposes, opacity, and mask coordinates after crop when
  `adjustment_layers` is used;
- schema version `2` for color-similarity masks; schema-version `1` geometric
  recipes remain supported;
- output size and encoding.

Reject a recipe when it changes more controls than the critique justifies, when
two layers have the same purpose, or when a layer merely makes the stack look
more sophisticated.
