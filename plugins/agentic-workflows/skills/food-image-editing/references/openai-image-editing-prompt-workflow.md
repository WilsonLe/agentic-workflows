# OpenAI image-editing prompt workflow

Use this reference to turn a food-photo critique into a precise OpenAI
image-edit prompt. It is a prompting guide, not executable software.

## Research basis

OpenAI's current image workflow allows a user to upload or select an existing
image and describe the desired edit. The editor can also target a selected
region, but edits may extend beyond that selection, so whole-image review
remains necessary:

- [Images in ChatGPT](https://help.openai.com/en/articles/11084440-images-in-chatgpt)
- [GPT Image Generation Models Prompting Guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)

The OpenAI prompting guide recommends structured prompts, explicit constraints,
and small iterative changes. It repeatedly separates what may change from what
must remain invariant and restates invariants during later edits. Use those
principles without assuming that any prompt guarantees exact preservation.

## Prompt-writing rules

1. Name the source image's role: establishing, hero, detail, alternate, or
   standalone.
2. Describe the intended change before the aesthetic language.
3. Name preserved facts individually. “Do not change anything else” is a useful
   final constraint, not a substitute for an invariant list.
4. Describe relationships: “lift the near-facing food while keeping the
   background darker,” not “increase exposure.”
5. Anchor realism to the source: same camera, lens perspective, lighting
   direction, shadows, material response, and focal plane.
6. Use negative constraints for likely drift. Do not create an indiscriminate
   list of every imaginable failure.
7. Make the first pass restrained. Correct one visible failure per follow-up.
8. When using multiple references, identify each image's role and the exact
   feature to borrow. Never say only “match these.”
9. If text is required, provide the exact copy in quotation marks, say it must
   appear once, and specify placement and legibility.
10. Inspect the result at normal viewing size and at useful detail before
    accepting it.

## Object decomposition and online reference workflow

When an edit changes an object rather than only colour, light, or crop:

1. Make a semantic object map of the source. List the hero food, supporting
   food, vessel, garnish, utensil or hand, surface, background,
   light/reflection, and text/branding that are actually visible. This is a
   visual planning step, not a claim that the image has been pixel-segmented.
2. Assign each object one decision: `preserve`, `modify`, `replace`, `remove`,
   or `add`. Confirm generative additions, removals, and replacements with the
   user when they were not explicit in the request.
3. Write narrow image-search queries using the target object's identity,
   material, construction, viewpoint, lighting, and background. For example,
   search for a real ceramic bowl at the source camera angle rather than a
   generic “beautiful bowl.”
4. Shortlist two to four candidates based on useful geometry, texture, material
   response, and viewpoint. Do not choose only by overall mood.
5. Open the original source page for every candidate. Verify what the object is,
   who or what published it, and whether the intended reuse is supported. A
   search-result thumbnail is not a reusable source asset.
6. Use user-owned, public-domain, or appropriately licensed images for direct
   reference integration. Record the source URL and rights basis. If rights are
   unclear, use the page only for research and translate the observation into
   words; do not supply or download its image for the edit.
7. Attach Image 1 as the source to edit. Attach only the approved reference
   images as Images 2–N. Give each one a single, explicit role, such as
   silhouette, construction, glaze texture, or material response.
8. State that unrelated reference content must not transfer. Match the source
   scene's scale, perspective, lighting direction, colour temperature, contact
   shadow, occlusion, depth of field, and grain.
9. Review the result for cutout edges, seams, repeated texture, copied
   background detail, hallucinated parts, floating objects, impossible
   occlusion, lighting mismatch, and truth-critical drift.

## Template 1 — Restrained global polish

```text
Goal:
Prepare this existing food photograph as a natural, premium menu hero image.

Change:
- Remove the unwanted colour cast and gently improve tonal separation.
- Make the hero food slightly more visually prominent without changing its shape.

Preserve:
- Preserve the exact dish, ingredients, portions, garnish, plating, plate shape,
  camera angle, perspective, focal plane, and background arrangement.
- Preserve existing sauce gloss and highlight texture.

Light and colour:
- Keep the source lighting direction.
- Maintain believable warmth; avoid orange whites or neon ingredients.
- Retain deep but readable shadows and protected highlights.

Realism:
- Keep natural food texture and realistic ceramic, metal, and tabletop materials.

Do not:
- Do not add or remove food, garnish, steam, crumbs, props, text, logos, or
  background objects.
- No plastic texture, artificial HDR, halos, or oversharpening.

Output:
- Photorealistic, high-quality edit with the source framing unchanged.
```

## Template 2 — Composition-preserving reframe

```text
Goal:
Reframe this existing food photograph for [TARGET USE] at [ASPECT RATIO].

Change:
- Crop to place [HERO ELEMENT] at [POSITION] with [SAFE-SPACE PURPOSE].
- Remove only expendable empty background from [EDGE OR REGION].

Preserve:
- Keep the complete [PLATE/BOWL/FOOD HEIGHT] and the exact food arrangement.
- Preserve camera angle, perspective, focal plane, lighting, and all retained
  pixels' visual identity.

Composition:
- Avoid tangencies at the plate rim, garnish, utensils, and frame edges.
- Do not simulate a new viewpoint or reconstruct anything outside the source.

Do not:
- Do not add canvas content, move objects, reshape the dish, or invent missing
  plate edges.

Output:
- [ASPECT RATIO], [ORIENTATION], with useful crop room for [TEXT/MOTION/NONE].
```

## Template 3 — Local light and focal emphasis

```text
Goal:
Improve focal hierarchy while keeping the photograph natural.

Change:
- Gently lift the [SPECIFIC HERO REGION].
- Subtly lower the [SPECIFIC DISTRACTING REGION].

Preserve:
- Keep the original lighting direction, contact shadows, reflections, food
  geometry, and material identity.
- Keep the background and all other regions unchanged in content and layout.

Light and colour:
- Use broad, soft transitions with no visible mask edge.
- Preserve sauce gloss and highlight detail; do not flatten shadow depth.

Do not:
- Do not create spotlight effects, new reflections, fake steam, halos, or
  inconsistent shadows.
```

## Template 4 — Colour and material correction

```text
Goal:
Correct material colour while preserving the photographed dish.

Change:
- Make [MATERIAL/INGREDIENT] read as [TRUTHFUL VISUAL DESCRIPTION].
- Reduce the unwanted [CAST/CONTAMINATION] on [REGION].

Preserve:
- Keep ingredient identity, doneness cues, sauce colour, garnish, portions,
  shape, texture, and lighting relationships.

Light and colour:
- Correct white balance before increasing colour intensity.
- Keep plate neutrals believable and protect natural variation within the food.

Do not:
- Do not recolour unrelated ingredients, exaggerate saturation, bleach
  highlights, or change perceived freshness or doneness.
```

## Template 5 — Match a visual set

```text
Goal:
Edit this image so it belongs to the same menu-photo set as the approved
references while remaining faithful to its own source.

References:
- Image 1 is the source to edit.
- Images 2–[N] define the set's restrained warmth, tonal depth, highlight
  protection, saturation level, and natural texture only.

Change:
- Bring the source toward the references' overall tonal and colour character.

Preserve:
- Preserve Image 1's exact dish, plating, camera angle, composition, lighting
  direction, food geometry, and background objects.
- Do not copy ingredients, props, crop, shadows, or composition from the
  reference images.

Do not:
- Do not force identical brightness across different camera angles.
- Do not introduce details from any reference into the source.
```

## Template 6 — One-change corrective iteration

```text
The previous edit is close. Correct only this issue:
- [ONE OBSERVED FAILURE].

Preserve exactly:
- [DISH AND INGREDIENT INVARIANTS].
- [CAMERA, COMPOSITION, LIGHTING, AND BACKGROUND INVARIANTS].
- All successful changes from the previous edit.

Do not:
- Do not reinterpret the image, add detail, change crop, alter another region,
  or increase the strength of the overall grade.
```

## Template 7 — Reference-object integration

```text
Goal:
Integrate one approved real-world object reference into the existing photograph
as a coherent, photorealistic edit.

Source and object map:
- Image 1 is the source to edit.
- Preserve: [OBJECTS AND REGIONS].
- Modify/replace/add/remove: [ONE APPROVED TARGET OBJECT AND ACTION].

Object references:
- Image 2 is a verified reference for [TARGET OBJECT]. Borrow only its
  [SILHOUETTE/CONSTRUCTION/MATERIAL/TEXTURE CUE].
- Image 3 is a verified reference for [OPTIONAL SECOND CUE]. Borrow only its
  [NAMED CUE].
- Do not copy any reference background, lighting setup, camera angle, props,
  branding, text, or unrelated object.

Change:
- [EXACT OBJECT INTEGRATION REQUEST].

Preserve:
- Preserve Image 1's dish identity, food arrangement, portions, garnish,
  vessel geometry, camera position, lens perspective, focal plane, lighting
  direction, and every unaffected object.

Composition and integration:
- Fit the target to Image 1's physical scale, viewpoint, perspective, overlap,
  and depth order.
- Create only the contact shadow, occlusion, reflection, and edge transition
  required by Image 1's existing light.

Light, colour, and realism:
- Match Image 1's colour temperature, exposure, contrast, depth of field,
  material response, noise, and grain.
- Keep natural asymmetry and surface variation; avoid repeated or synthetic
  texture.

Do not:
- Do not redesign the scene, move preserved objects, invent object parts, copy
  reference scenery, add text or logos, or alter food that is not the target.
- No floating edges, cutout halo, seam, mismatched sharpness, impossible
  shadow, or inconsistent reflection.

Output:
- Photorealistic AI-edited image at [ASPECT RATIO/ORIENTATION/QUALITY].
```

## Multi-turn review loop

For every result:

1. Compare the full frame to the source.
2. Check food identity and geometry before aesthetics.
3. Check the exact requested change.
4. For reference-object edits, check scale, viewpoint, contact, occlusion,
   boundary quality, and whether unrelated reference content transferred.
5. Check lighting direction, shadows, reflections, and material response.
6. Check crop, focal plane, texture, and set consistency.
7. Accept, request one smaller correction, or return to the original when drift
   compounds.

When a second correction starts undoing a previously correct area, stop stacking
edits. Return to the best earlier image and write a narrower prompt.
