# Image Editing

An instruction-only Codex plugin for food-photo curation, prompt construction,
OpenAI image-editing tool use, and visual review.

## What it does

1. Inspects the source image before proposing an edit.
2. Curates complementary establishing, hero, detail, and alternate frames without
   enforcing a fixed quota.
3. Converts visual intent into a structured prompt that separates `Change` from
   `Preserve`.
4. Decomposes a scene into semantic object roles and, when needed, finds
   provenance-verified, rights-appropriate real-object references online.
5. Assigns each reference a narrow role and directs the OpenAI/Codex
   image-editing tool when the user requests an edit.
6. Reviews the complete result for food identity, geometry, composition,
   lighting, colour, material, texture, and set-consistency drift.
7. Iterates with one smaller correction at a time while restating invariants.

The plugin contains no Python, JavaScript, shell, ImageMagick, OpenCV, or ML
image-processing program. Generated outputs are AI-edited images and must not be
treated as documentary evidence of the original dish without disclosure.

See `skills/food-image-editing/SKILL.md` for the workflow and
`skills/food-image-editing/references/openai-image-editing-prompt-workflow.md`
for seven reusable prompt templates, including reference-object integration.
