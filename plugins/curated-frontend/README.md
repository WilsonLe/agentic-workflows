# Curated Frontend

Design interfaces that start simple and reveal information as the user's task requires it. This plugin captures Wilson's stated taste and a synthesis of inspected CYOBot surfaces and modern frontend design skills.

The default is spacious, restrained, and purposeful. Every visible element should help the user decide, act, orient themselves, or understand an outcome. Progressive disclosure follows the task: choosing a role opens its details; selecting table rows reveals bulk actions; opening a lesson exposes its instructions. Necessary comparison data, critical context, and frequent expert controls remain easy to reach.

## Install and use

Add the marketplace once, then install the focused package:

```sh
# Codex
codex plugin marketplace add wilsonle/agentic-workflows
codex plugin add curated-frontend@agentic-workflows

# Claude Code
claude plugin marketplace add wilsonle/agentic-workflows
claude plugin install curated-frontend@agentic-workflows
```

Start a fresh session and invoke the skill, for example:

> Use $curated-frontend-design to build a student dashboard. Prioritize continuing the current lesson, then reveal supporting progress and resources when useful.

> Use $curated-frontend-design to review our manager dashboard. Explain which information belongs on the initial view and which should appear after interaction.

> Use $curated-frontend-design to improve this form while preserving our existing design system.

## What's included

- [Design skill](skills/curated-frontend-design/SKILL.md): task framing, information hierarchy, implementation, and review.
- [Disclosure and role patterns](skills/curated-frontend-design/references/disclosure-and-roles.md): student, instructor, and manager workflows plus disclosure exceptions.
- [Visual and interaction craft](skills/curated-frontend-design/references/visual-and-interaction-craft.md): spacing, typography, tables, motion, and accessible states.
- [CYOBot observations](skills/curated-frontend-design/references/cyobot-observations.md): public and authenticated app observations with explicit evidence limits.
- [Research and curation](skills/curated-frontend-design/references/research-and-curation.md): source versions, useful ideas, and limits of each upstream skill.
- [Project taste record](skills/curated-frontend-design/references/project-taste-record.md): retain accepted decisions and corrections locally.
- [Evaluation scenarios](skills/curated-frontend-design/references/evaluation-scenarios.md): realistic acceptance cases for future skill evaluation.

## Scope and portability

One instruction-only skill supports Codex and Claude Code without extra runtime dependencies. The host supplies any file, browser, or implementation tools needed for the actual task. It works with the project's stack and existing design system; it does not require a component library, font, or styling framework.

This package is independent of the central bundle. It contains original guidance and source links, with no upstream skill code, CYOBot assets, account data, or screenshots. The observed macro decisions inform the approach; CYOBot's visual styling is not a required theme. Package validation does not establish that a model consistently follows the design guidance; the evaluation scenarios make that separate check explicit.
