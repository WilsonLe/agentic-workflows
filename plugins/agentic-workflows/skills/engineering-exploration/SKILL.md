---
name: engineering-exploration
description: Explore an uncertain module design or UI behavior with a focused architecture survey or disposable prototype before committing to implementation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering exploration

Choose the smallest experiment that answers the decision at hand. This skill creates decision evidence; follow the repository's delivery rules and the Codex Standard Development Workflow when available for tracked project changes.

## Architecture survey

If the user asks where to improve the design, start with the named subsystem or recent change hotspots. Read the domain vocabulary, relevant ADRs, representative callers, and tests. Identify concrete friction: one concept scattered across many shallow wrappers, leaky interfaces, repeated cross-module edits, or behavior that cannot be tested through a useful seam.

Present a few candidates with affected files, the current cost, a proposed responsibility shift, expected test benefit, and confidence. A compact before/after diagram helps when relationships are complex. Rank candidates; do not refactor all of them merely because the survey found them. Respect an existing ADR unless new evidence warrants revisiting it.

## Disposable prototype

If a design question can be answered faster by trying it, state the question and success signal first. For interaction or visual uncertainty, show meaningfully different variants through one easy-to-run surface. For state or logic uncertainty, expose relevant state after each action and include edge cases that could change the design decision.

Keep prototype state local and disposable unless persistence is itself the question. Make the artifact visibly a prototype and cheap to run. Skip production polish and implementation-mirroring tests. Record the question, observed outcome, and chosen direction in the issue or decision record. Remove or isolate throwaway code from the delivery branch; keep only the validated behavior in the production implementation.
