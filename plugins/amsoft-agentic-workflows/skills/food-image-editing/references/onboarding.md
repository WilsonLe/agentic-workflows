# Food Image Editing onboarding

Use this guide when a user asks to set up, onboard, or get started with Food Image Editing.

## Prerequisites

- Codex must be able to view the source image.
- Python 3.10 or newer must be available.
- ImageMagick 7 must be installed and expose the `magick` command.
- The user must provide a food photograph or food-video still. Version 0.1 is food-only.

Check the runtime before editing. If ImageMagick is missing, stop and report that prerequisite instead of substituting a generative image tool.

## What to collect

Ask for the intended use, aspect ratio, target dimensions, brand look, and whether the image must match adjacent video shots. Confirm where derived outputs may be written. Keep the original unchanged.

## First-run workflow

1. Inspect the actual image and identify the dish, angle, hero area, crop risks, color and tone issues, and defects that require a reshoot.
2. Verify the runtime and run the analysis command from the skill.
3. Present the visual critique, measured evidence, and proposed bounded corrections.
4. During onboarding, stop before applying edits unless the user explicitly asks to continue.
5. If approved, write a new output plus recipe, provenance, and verification files, then compare the result visibly with the original.

## Ready state

The workflow is ready when the image is viewable, the required runtime is available, the intended output is known, and a separate output location is available.

## Suggested first prompt

> Onboard me to Food Image Editing with this image. Verify the prerequisites, inspect and measure the photo, then propose corrections without editing it yet and without using image generation.
