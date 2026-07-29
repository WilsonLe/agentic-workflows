# Issue #37 — Instruction-only image-editing prompt workflow

Status: approved scope correction in progress
Approved by: user in the originating Codex task
Approval date: 2026-07-29
Issue: https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin/issues/37
Draft PR: https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin/pull/38

## Objective

Replace PR #38's custom image-processing implementation with an instruction-only skill that helps
Codex produce better prompts for OpenAI image-editing tools and review the resulting edits.

## Scope correction

- Revert all executable, module, schema, example-recipe, validator, and workflow-test additions from
  the original implementation.
- Remove the legacy image-processing helper, its helper-local tests, recipe example, HTML report
  templates, and code-oriented references so the skill package is instruction only.
- Rewrite the standalone food-image-editing skill as visual-analysis, prompt-construction,
  image-tool invocation, comparison, and iterative-review guidance.
- Add Markdown-only prompt templates and editor-derived heuristics.
- Add a reference-object workflow that conceptually decomposes a source image into smaller
  editable objects, searches online for real-world visual references, verifies source provenance
  and reuse rights, and assigns each approved reference a narrow role in the final OpenAI image
  edit.
- Generate the central mirror, update routing/registry/metadata, apply fresh cachebusters, reinstall,
  and verify installed parity.

## Prohibited work

- No image-processing code remains in the skill package.
- No new schemas, CLI commands, automated image transformations, or batch engine.
- No committed restaurant media.
- No scraper, downloader, segmentation, masking, object extraction, or compositing program.
- No direct integration of an online image whose source page and reuse basis have not been
  verified.
- No claim of pixel-perfect preservation or automatic aesthetic approval.
- No merge or deployment.

## Prompt architecture

Every edit prompt will contain:

1. `Goal` — the intended use and visual outcome.
2. `Change` — only the requested modifications, ordered by importance.
3. `Preserve` — source identity, food arrangement, geometry, camera, and unaffected regions.
4. `Composition` — crop/reframe intent and aspect ratio, when applicable.
5. `Light and colour` — direction, tone, white balance, saturation, and material-specific intent.
6. `Realism` — believable texture, gloss, shadows, and photographic integration.
7. `Do not` — explicit drift and fabrication constraints.
8. `Output` — size/aspect/quality and whether transparency or text is required.
9. `Object references` — when applicable, identify the source and every approved reference by
   image number, object role, and the exact form, material, texture, or construction cue to borrow.
10. `Review` — observable checks that determine whether to accept or issue a smaller follow-up.

## Reference-object architecture

1. Build a semantic object map without claiming pixel segmentation: hero food, supporting food,
   vessel, garnish, utensil or hand, surface, background, light/reflection, and text/branding.
2. Mark each object `preserve`, `modify`, `replace`, `remove`, or `add`; require explicit user intent
   before generative additions, removals, or replacements.
3. Search for real-world references using object identity, material, viewpoint, lighting, and
   background terms. Shortlist references for useful geometry or material evidence, not aesthetics
   alone.
4. Open each source page and verify identity, provenance, and a reuse basis. Search-result
   thumbnails are discovery evidence, not permission to reuse.
5. Attach only approved reference images to the OpenAI image tool. Identify Image 1 as the source
   and Images 2–N by their exact reference roles; do not use an ambiguous “match these” request.
6. Prompt the integration to preserve source perspective, scale, lighting direction, colour
   temperature, contact shadows, occlusion, depth of field, grain, and unaffected objects.
7. Review object boundaries, seams, repeated patterns, hallucinated details, lighting mismatch,
   floating objects, and documentary-truth implications.

## Validation ladder

- [x] User approved the instruction-only scope correction.
- [x] Original programmatic implementation reverted.
- [x] GitHub issue updated to the revised specification.
- [x] Standalone skill and prompt reference rewritten.
- [x] Central mirror, router, registry, README, and metadata updated.
- [x] Final package inventory contains no image-editing executable, schema, recipe, or HTML report
  template.
- [x] Package generation, package validation, repository validation, and Ruff pass.
- [x] Fresh cachebusters applied; both personal plugins reinstalled and parity verified.
- [x] Draft PR #38 description updated; branch pushed; stop for review.
- [x] Issue and plan updated for reference-object decomposition, online search, provenance, and
  integration.
- [x] Skill and prompt reference updated with the reference-object workflow and reusable prompt.
- [x] Router, registry, README, metadata, validator, and central mirror updated.
- [x] Full validation, fresh reinstall, installed parity, draft PR update, and branch push complete.

## Requirements-to-evidence

| Requirement | Evidence |
| --- | --- |
| Instruction-only behavior | final skill and prompt-reference review |
| No programmatic implementation | package inventory and executable-free catalog validation |
| OpenAI tool prompting | prompt framework plus seven concrete templates |
| Object decomposition | semantic object map with preserve/modify/replace/remove/add decisions |
| Online reference search | source-page verification, provenance, reuse basis, and thumbnail guard |
| Reference integration | numbered image roles plus scale, perspective, light, shadow, occlusion, and texture constraints |
| Preservation and truthfulness | explicit invariant and negative-constraint sections |
| Iterative quality control | one-change correction loop and visual review checklist |
| Standalone/central parity | deterministic package generator and validator |
| Installed adoption | exact version, enabled state, source/cache paths, byte parity |

## Completion boundary

After validation and installed adoption, update draft PR #38 and stop for user review. Merge and
deployment require separate authorization.

## Validation evidence

- Instruction-only package inventory: exactly `SKILL.md`, `agents/openai.yaml`, and
  `references/openai-image-editing-prompt-workflow.md` in each standalone and central installed
  skill.
- Deterministic mirror generation/check and plugin-package validation passed.
- Complete repository validation passed: 137 tests and Ruff.
- The semantic object map, source-page and reuse-basis checks, numbered reference roles, and
  reference-object integration template are present in both generated skill copies.
- Personal source and installed-cache trees match byte-for-byte, excluding unrelated runtime
  Python bytecode caches elsewhere in the central suite.
- Installed `image-editing@personal` and `amsoft-agentic-workflows@personal` are enabled at
  `0.1.0+codex.20260729202504`.
