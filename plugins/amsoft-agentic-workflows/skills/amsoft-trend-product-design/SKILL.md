---
name: amsoft-trend-product-design
description: Create production-aware briefs and approval-gated concept-art requests for an exact trend-product concept, routing image work through the host image capability and preserving provenance and review lineage.
---

# Trend Product Design

Read [design and image routing](references/workflow.md). Require persisted
`run_id`, `opportunity_id`, `concept_id`, and an approved brief. This skill owns
the brief, production constraints, prompt, lineage, and review—not an image
model. Route actual generation/editing through the host image capability. Image
output is `concept_only` until deterministic typography/prepress and human
production review pass.
