# UI Design

Design interfaces that start simple and reveal information as the user's task requires it. This plugin captures Wilson's stated taste and a synthesis of inspected CYOBot surfaces and modern frontend design skills.

The default is spacious, restrained, and purposeful. Every visible element should help the user decide, act, orient themselves, or understand an outcome. Progressive disclosure follows the task: choosing a role opens its details; selecting table rows reveals bulk actions; opening a lesson exposes its instructions. Necessary comparison data, critical context, and frequent expert controls remain easy to reach.

## Install and use

Add the marketplace once, then install the focused package:

```sh
# Codex
codex plugin marketplace add wilsonle/agentic-workflows
codex plugin add ui-design@agentic-workflows

# Claude Code
claude plugin marketplace add wilsonle/agentic-workflows
claude plugin install ui-design@agentic-workflows
```

Start a fresh session and invoke the skill, for example:

> Use $ui-design to build a student dashboard. Prioritize continuing the current lesson, then reveal supporting progress and resources when useful.

> Use $ui-design to review our manager dashboard. Explain which information belongs on the initial view and which should appear after interaction.

> Use $ui-design to improve this form while preserving our existing design system.

## What's included

- [Design skill](skills/ui-design/SKILL.md): task framing, information hierarchy, implementation, and review.
- [Disclosure and role patterns](skills/ui-design/references/disclosure-and-roles.md): student, instructor, and manager workflows plus disclosure exceptions.
- [Visual and interaction craft](skills/ui-design/references/visual-and-interaction-craft.md): spacing, typography, tables, motion, and accessible states.
- [CYOBot observations](skills/ui-design/references/cyobot-observations.md): public and authenticated app observations with explicit evidence limits.
- [Design references](skills/ui-design/references/design-references.md): source versions, useful ideas, and limits of each upstream skill.
- [Project taste record](skills/ui-design/references/project-taste-record.md): retain accepted decisions and corrections locally.
- [Evaluation scenarios](skills/ui-design/references/evaluation-scenarios.md): realistic acceptance cases for future skill evaluation.

## Scope and portability

One instruction-only skill supports Codex and Claude Code without extra runtime dependencies. The host supplies any file, browser, or implementation tools needed for the actual task. It works with the project's stack and existing design system; it does not require a component library, font, or styling framework.

This package is independent of the central bundle. It contains original guidance and source links, with no upstream skill code, CYOBot assets, account data, or screenshots. The observed macro decisions inform the approach; CYOBot's visual styling is not a required theme. Package validation does not establish that a model consistently follows the design guidance; the evaluation scenarios make that separate check explicit.
