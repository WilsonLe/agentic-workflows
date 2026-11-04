# Design and image routing

Define product/SKU, decorating method, print area, bleed/safe area, minimum
detail, output dimensions, product colours, viewing distance, message, original
subject, composition, palette, typography, exact Vietnamese copy, invariants,
prohibitions, reference rights, variants, and acceptance checks.

Follow this image-editing pattern: inspect real inputs, preserve
originals, separate Change from Preserve, verify source-page provenance and
reuse rights, invoke the host's image tool, review the complete result, and make
one narrow correction at a time.

In Codex, call the image tool with the prompt only for new art. For local edits
inspect the file first and use `referenced_image_paths`. For conversation-only
images use the smallest `num_last_images_to_include`. Never provide both
mechanisms. On hosts without an image tool, such as Claude Code, deliver the
complete design brief and prompts for the user's image tool, and do not claim
concept art was generated.
Generate three learning routes: bold icon, compact scene, and modular pattern.
Do not trust generated text, transparency, vector status, DPI, colour
separations, or print readiness without deterministic inspection. Keep concept
art, production master, and mockup separate.
