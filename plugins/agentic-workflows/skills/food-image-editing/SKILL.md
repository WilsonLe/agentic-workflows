---
name: food-image-editing
description: Inspect, curate, and improve food photographs by writing precise prompts for OpenAI image-editing tools, decomposing scenes into editable object roles, finding rights-appropriate real-object references online, and visually reviewing each result for source drift, food truthfulness, composition, light, colour, material, texture, object integration, and set consistency. Use when the user asks to shortlist, critique, edit, improve, reframe, relight, colour-correct, restyle, replace or add an object, or prepare food images or food-video stills.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: OpenAI image editing tool** — Connect the supported image editing tool and provide authorized source images.

<!-- catalog-prerequisites:end -->

# Food Image Editing

Use visual judgment and prompt craft to direct OpenAI's image-editing tool. This
skill contains instructions only. Do not run or create a custom image-processing
program, recipe engine, mask generator, or batch editor.

Read
[OpenAI image-editing prompt workflow](references/openai-image-editing-prompt-workflow.md)
before the first edit in a task and whenever an edit drifts from the source.

## Operating boundary

- Inspect the actual source image before proposing or performing an edit.
- Use the OpenAI/Codex image-editing tool for the edit itself.
- Keep the original file unchanged. Treat every result as a new AI-edited image.
- Do not promise pixel-perfect preservation. Image editing can change details
  outside the intended region, so inspect the complete result.
- Do not invent ingredients, garnish, steam, doneness, portions, packaging,
  branding, text, or background objects unless the user explicitly requests
  that generative change.
- Do not infer menu names, ingredients, dietary properties, allergens, prices,
  or preparation methods from appearance.
- Treat online image-search results as discovery leads. Open the source page and
  verify the object's identity, provenance, and reuse basis before supplying a
  reference image to the image-editing tool. A search thumbnail is not reuse
  permission.
- Use user-owned, public-domain, or appropriately licensed reference images for
  direct integration. Record the source URL and rights basis in the delivery.
- An inserted, removed, or replaced object makes the result generative. Obtain
  explicit user intent for that change and disclose that the result cannot
  prove the photographed dish, ingredient, portion, or presentation.
- Never present an AI-edited food image as documentary evidence of the original
  dish without disclosure.

## Required workflow

1. Establish the output purpose, target aspect ratio, dimensions when known,
   adjacent-image or video continuity, brand look, and whether generative
   additions or removals are permitted.
2. Inspect the source at useful detail. Record:
   - camera angle and confidence;
   - hero food, plate or bowl boundary, garnish, utensils, hands, props, and
     negative space;
   - lighting direction, colour cast, highlight and shadow texture, focus,
     reflections, clutter, and crop room;
   - truth-critical details that must not drift.
3. Build a semantic object map when the request changes or adds an object.
   Decompose the scene conceptually—do not claim automatic pixel segmentation—
   into the hero food, supporting food, vessel, garnish, utensil or hand,
   surface, background, light/reflection, and text/branding as applicable.
   Mark each object `preserve`, `modify`, `replace`, `remove`, or `add`.
4. If an object needs a real-world reference, search online using its identity,
   material, construction, viewpoint, lighting, and background. Shortlist two
   to four candidates for useful geometry and material evidence. Open each
   source page, verify provenance and reuse rights, and retain only references
   suitable for the intended use.
5. If the request is curation rather than editing, compare all candidates and
   recommend a complementary set. Prefer useful roles—`establishing`, `hero`,
   `detail`, and `alternate`—over a fixed image quota. Explain exclusions and
   near-duplicates. Do not call the image tool unless an edit is requested.
6. Convert the user's intent into one structured edit prompt using the framework
   below. Prefer one coherent pass with a small number of related changes.
   For a reference-object edit, identify Image 1 as the source and Images 2–N
   by object role and the exact form, material, texture, or construction cue to
   borrow. Never prompt only “match these.”
7. Invoke the image-editing tool with the source image, approved references, and
   the structured prompt. Include every target image through the tool's
   supported image-input mechanism; never substitute a visually similar file.
8. Inspect the complete output beside the source. Check both the requested
   change and every preservation constraint.
9. If the result drifts, issue a smaller corrective edit against the best
   current image. Restate all invariants; do not rely on “keep everything else”
   alone.
10. Stop after a strong result or when another edit would risk more drift than
   improvement. Report limitations and recommend a reshoot when focus, motion
   blur, missing geometry, or documentary truth cannot be recovered safely.

## Prompt framework

Write prompts with these sections:

```text
Goal:
[Where the image will be used and the intended visual outcome.]

Change:
- [Exact modification 1.]
- [Exact modification 2, only when tightly related.]

Preserve:
- [Dish identity, ingredient arrangement, portions, garnish, plate geometry.]
- [Camera angle, perspective, focal plane, lighting direction, unaffected regions.]

Composition:
- [Target aspect ratio, crop intent, hero placement, safe negative space.]

Light and colour:
- [White balance, tonal shape, highlight/shadow intent, material-specific colour.]

Realism:
- [Natural texture, gloss, steam already present, contact shadows, photographic integration.]

Object references:
- [Image number, object role, verified source, and exact visual cue to borrow.]
- [How scale, perspective, lighting, shadow, occlusion, depth of field, and grain must match Image 1.]

Do not:
- [No new ingredients, garnish, props, text, logos, watermarks, or geometry drift.]
- [No plastic texture, halos, oversharpening, clipped gloss, or artificial HDR.]

Output:
- [Aspect ratio, orientation, quality, background requirement, text requirement.]
```

Omit a section only when it truly does not apply. State the most important
change first. Use concrete visual language rather than software control names or
invented numeric slider values.

## Editor-derived priorities

Apply these ten priorities when writing and reviewing prompts:

1. **Quality-led curation** — retain only strong, non-redundant frames; never
   fill a quota with weaker images.
2. **Visual-set roles** — make establishing, hero, detail, and alternate images
   complementary in scale and information.
3. **Composition first** — settle aspect ratio, crop, rotation, focal hierarchy,
   and negative space before requesting colour or texture changes.
4. **White balance before saturation** — neutralize an unwanted cast without
   removing intentional food warmth.
5. **Restrained tonal shaping** — lift readable midtones, preserve highlight
   texture, and retain believable shadow depth.
6. **Material-specific colour** — describe sauce gloss, fried crust, herbs,
   ceramics, wood, and reflective metal separately when they need different
   treatment.
7. **Directional local light** — describe where light should be lifted or
   lowered and preserve the source's direction and contact shadows.
8. **Texture separate from sharpness** — request natural food texture and avoid
   crunchy edges, halos, or global oversharpening.
9. **Set consistency** — share the same tonal, colour, contrast, and realism
   vocabulary across a series while adapting composition to each frame.
10. **Small corrective iterations** — change one failure at a time and repeat
    the invariants on every edit.

## Reference-object integration gate

Before using an online reference in an edit, confirm all of the following:

- the source scene has an object map and only the approved target is marked
  `modify`, `replace`, `remove`, or `add`;
- the reference source page is open and the object's identity, provenance, and
  reuse basis are recorded;
- the reference is selected for named evidence such as silhouette, construction,
  surface texture, or material response—not as an ambiguous style target;
- the prompt identifies every image by number and states what must be borrowed
  and what must not be copied;
- the prompt preserves Image 1's viewpoint, lens perspective, scale, lighting
  direction, colour temperature, contact shadow, occlusion, depth of field,
  noise/grain, and unaffected objects;
- the output will be disclosed as AI-edited and not used as documentary proof.

## Review gate

Reject or revise an output when any of these appear:

- ingredient, garnish, portion, plate, utensil, hand, logo, or label drift;
- invented steam, sauce, crumbs, highlights, shadows, props, or background
  detail that was not requested;
- changed camera angle, perspective, focal plane, or dish geometry;
- clipped plate edges, awkward tangencies, weak crop balance, or lost safe
  space;
- grey whites, unnatural warmth, neon ingredients, colour contamination, or
  inconsistent doneness cues;
- plastic food, smeared texture, repeated patterns, halos, brittle sharpening,
  fake depth of field, or excessive HDR;
- mismatched object scale or viewpoint, floating objects, broken contact
  shadows, impossible occlusion, cutout edges, seams, copied reference
  backgrounds, or inconsistent grain;
- inconsistent grading or scale across images intended as one set.

Accept only after visual comparison. A fluent prompt and a plausible standalone
result are not sufficient evidence.

## Delivery

Return:

- the AI-edited image;
- the final prompt used;
- a short list of preserved elements and intentional changes;
- any remaining drift, uncertainty, or reshoot limitation;
- for reference-object edits, the object map, numbered reference roles, source
  URLs, reuse basis, and generative-edit disclosure;
- for a set, the role of each accepted frame and a concise consistency note.
