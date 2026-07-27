---
name: food-image-editing
description: Critically review and non-generatively edit food photographs or still frames for food videos, and onboard users to Food Image Editing. Use for setup or first-run guidance, or when the user asks to edit, improve, grade, crop, color-correct, prepare, or critique a food image. Inspect the actual image, measure it, account for overhead, 45-degree, side, or macro angles, apply only technical pixel transformations, and verify the visible result. Never use image generation, generative fill, object replacement, synthetic backgrounds, or outpainting.
---

# Food Image Editing

Produce a better food image without inventing a single pixel of scene content.
This skill is food-only in version 0.1. Read
[references/research-and-guardrails.md](references/research-and-guardrails.md)
before the first edit in a task or whenever choosing numeric targets.

For setup, onboarding, or first-use requests, read
[references/onboarding.md](references/onboarding.md), verify the prerequisites, and stop before
editing unless the user explicitly asks to continue.

## Absolute boundary

- Never call an image-generation tool while using this skill.
- Never use generative fill, inpainting, outpainting, object replacement,
  synthetic steam, synthetic garnish, background generation, relighting models,
  face restoration, super-resolution models, or content-aware crop expansion.
- Allowed operations are deterministic transformations of input pixels: metadata
  orientation, rotate, crop, resize, white-balance gains, exposure, levels,
  contrast, saturation, local masked adjustments using the same source pixels,
  denoise, and conventional sharpening.
- Keep the original unchanged. Write a new output and a JSON provenance sidecar.
- If the photograph needs a different viewpoint, missing plate edge, different
  styling, moved prop, restored blown highlight, or sharper focus, say that it
  needs a reshoot. Do not fake the repair.

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
   fields. Use small first-pass moves. There is no universal food preset.
6. Dry-run and inspect the exact command plan:

   `python3 scripts/food_image.py edit INPUT OUTPUT --recipe recipe.json --dry-run`

7. Apply the edit:

   `python3 scripts/food_image.py edit INPUT OUTPUT --recipe recipe.json --report OUTPUT.edit.json`

8. Measure and validate:

   `python3 scripts/food_image.py verify INPUT OUTPUT --recipe recipe.json --output OUTPUT.verify.json`

9. Visually inspect the output beside the original. Confirm believable food
   color, retained highlight texture, natural shadows, correct crop, clean plate
   edges, absence of halos, and consistency with the intended video sequence.
   Iterate once with smaller changes if any correction calls attention to itself.
10. Deliver the edited file, recipe, edit report, verification report, and a
    concise explanation of what changed. Never claim “best” from metrics alone.

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
- output size and encoding.

Reject a recipe when it changes more controls than the critique justifies.
