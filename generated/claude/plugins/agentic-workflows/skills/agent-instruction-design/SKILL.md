---
name: agent-instruction-design
description: Create or revise agent skills, AGENTS.md guidance, or a session retrospective so instructions are discoverable, concise, and verifiable.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Agent instruction design

Use this skill when authoring instructions that an agent will consume, or when reviewing a session for improvements to that environment. Follow the repository's skill schema, package generator, and validation commands. Do not edit memory or unrelated global instructions without an explicit request.

## Write instructions

1. Identify the actual task branch that should trigger the document. Put that trigger in the skill description or the smallest existing navigation pointer. Avoid broad wording that draws unrelated tasks into the skill.
2. Keep the actions every run needs in the entry point. Place substantial conditional detail in a linked reference that is read only for that condition. Do not create a router for a one-path task.
3. End important steps with an observable completion condition. State the desired behavior directly. Use a hard prohibition only when a concrete safety or authority boundary requires it.
4. Keep each rule in one authoritative location. Link to repository commands, schema, and existing policies instead of copying facts that the environment can reveal and that may drift.
5. Check the finished instruction against at least one realistic request: would the description select it, could the agent find every needed reference, and would it know when it is done? Run the repository's package and instruction validation.

## Review a session

Read the actual session evidence before proposing a rule. Look for repeated navigation delays, missed checks, stale instructions, expensive tool patterns, and information the agent could not access. Prefer a deterministic lint, test, or CI check for a mechanical failure. Reserve prose standards for choices that need judgment. Compare proposals with existing issues and delivered fixes; report severity and evidence without silently creating trackers or changing project instructions. In Codex, use `session-reflection` when the request spans multiple sessions or asks for issue deduplication.
