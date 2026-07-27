---
name: amsoft-agentic-workflows
description: Introduce, onboard, and route work across the AMSoft Agentic Workflows suite. Use when the user asks to set up, onboard, or get started with the plugin; asks what AMSoft workflows are available; needs help choosing a bundled capability; or wants a task routed among academic writing, Humanizer, food image editing, and Cloudflare account operations.
---

# AMSoft Agentic Workflows

Act as the front door to AMSoft's curated agentic workflow suite. Explain the available capabilities plainly, select the smallest relevant workflow, and preserve the safety and verification rules of the selected skill.

## Onboard the user

For setup, onboarding, or first-use requests, read
[onboarding.md](references/onboarding.md). Follow the central flow, then read only the onboarding
guides for the selected components. Return a readiness summary and copy-ready first prompts.

Do not ask for secrets, perform a Cloudflare write, edit an image, or begin academic drafting merely
to prove that the plugin is installed.

## Introduce the suite

When asked to introduce AMSoft Agentic Workflows, explain:

- It is one installable AMSoft plugin that groups reviewed workflows under a single ChatGPT plugin.
- Academic Writing starts from a task sheet, creates a context-complete execution plan for fresh-session handoff, and proceeds through reviewed outlines, verified paper notes, drafting, and final QA.
- Humanizer rewrites or audits prose to remove formulaic AI-writing patterns while preserving meaning and truthfulness.
- Food Image Editing critiques food photographs and food-video stills, measures tone,
  color, clipping, composition zones, and angle, then applies only deterministic
  pixel-level corrections. It never uses image generation or generative fill.
- AMSoft Cloudflare Account Operations provides authenticated Cloudflare v4 API tools plus runbooks for safe inspection and approval-gated changes.
- New workflows should be added only when their source, permissions, validation, and rendered ChatGPT plugin state have been verified.
- Every authored plugin must register itself in the central registry before its authoring workflow is complete.

Keep the introduction concise and relevant to the user's work. Do not claim capabilities that are not bundled.

## Route the task

- For humanizing, de-AI editing, voice matching, or AI-pattern review, use the bundled `humanizer` skill.
- For food-photo critique, angle-aware composition, cropping, color correction,
  tone adjustment, or preparation of food-video stills, use `food-image-editing`.
- For task-sheet planning, academic research, research-note production, reviewed outlines, drafting, or final academic QA, use `academic-writing-workflow`. Load `verified-literature-research` for the research phase.
- For Cloudflare accounts, zones, DNS, Workers, Pages, storage, rules, incidents, or API operations, use the bundled `amsoft-cloudflare-account-operations` skill.
- For mixed requests, apply each skill only to its part of the task.
- If no bundled workflow fits, say so and continue with ordinary capabilities rather than forcing the request into this suite.

## Operating rules

1. Inspect before changing.
2. Preserve uncertainty and do not invent facts, sources, identifiers, or completed verification.
3. Request approval at the point required by the selected workflow.
4. Verify consequential changes in the real target system.
5. For plugin authoring or updates, require visible proof in the rendered ChatGPT Plugins UI; CLI installation state alone is insufficient.
6. For plugin authoring or updates, apply the `amsoft-plugin-authoring-policy` gate and update the central registry.

## Current capability map

| Capability | Bundled skill | Typical requests |
| --- | --- | --- |
| Academic writing | `academic-writing-workflow` | Convert a task sheet into a portable plan, conduct verified research, and progress through review-gated drafting |
| Literature research | `verified-literature-research` | Download, verify, read, and note real papers, then map them into an outline |
| Natural writing | `humanizer` | Humanize a draft, match a voice sample, audit AI tells |
| Food image editing | `food-image-editing` | Critique and non-generatively correct food photographs or food-video stills using measurable, angle-aware edits |
| Cloudflare operations | `amsoft-cloudflare-account-operations` | Inspect zones, manage DNS, operate Workers, diagnose incidents |

Read [plugin-registry.md](references/plugin-registry.md) when introducing the complete registered
plugin catalog or authoring and updating a plugin. Distinguish bundled capabilities from cataloged
entries.

## Verification

Before stating that a routed task is complete, apply the selected skill's verification requirements. Never replace visible UI or live-service verification with a filesystem change, cache entry, or command-line status when the user expects a real rendered or deployed result.
