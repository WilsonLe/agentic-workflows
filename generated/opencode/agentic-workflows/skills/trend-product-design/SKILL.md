---
name: trend-product-design
description: Create production-aware briefs and approval-gated concept-art requests for an exact trend-product concept, routing image work through the host image capability and preserving provenance and review lineage.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Optional: Image generation tool** — Connect an image generation tool only when approved concept art is requested.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Trend Product Design

Read [design and image routing](references/workflow.md). Require persisted
`run_id`, `opportunity_id`, `concept_id`, and an approved brief. This skill owns
the brief, production constraints, prompt, lineage, and review—not an image
model. Route actual generation/editing through the host image capability. Image
output is `concept_only` until deterministic typography/prepress and human
production review pass.
