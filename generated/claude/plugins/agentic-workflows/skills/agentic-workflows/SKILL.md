---
name: agentic-workflows
description: Route tasks to appropriate Agentic Workflows skills and explain installation, updates, and setup. Use when choosing which installed workflow fits a task or when installing, updating, or troubleshooting this plugin. In Codex, route plain repository edit requests to Standard Development Workflow when available; other hosts retain their repository delivery rules.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

<!-- claude-code-notes:start -->
## Claude Code

This skill's references write `<plugin-root>` for `${CLAUDE_PLUGIN_ROOT}` and `<skill-root>` for `${CLAUDE_SKILL_DIR}`. Use those absolute paths in commands you run or give to the user; never show the placeholders.

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

Claude in Chrome is available only when its browser tools are in this session's tool list. If they are absent, do not offer to open pages, create keys or tokens, or say you can use Claude in Chrome. Give the user the exact URL and steps to complete themselves; `claude --chrome` or `/chrome` enables browser help in a later session.

<!-- claude-code-notes:end -->

# Agentic Workflows

Select the task's skill and read its prerequisites and verification rules. Request
access only when needed. Focused engineering methods complement repository delivery
rules; they do not replace authority or PR gates.

In Claude Code, invoke skills as `/agentic-workflows:<skill-id>` or let Claude load
the matching skill; in OpenCode V2, use `@skill-id` or let the host load it. Load
another skill through the host rather than reading its file. These packages expose only
catalog-supported skills: Codex hooks, task orchestration, and Standard Development
Workflow are not installed, so follow the project's `CLAUDE.md` or `AGENTS.md` and
host delivery rules instead. In files a skill reads later, `<skill-root>` is the
loaded skill's base directory and `<plugin-root>` is two levels above it; resolve
both before running a helper or giving a command to the user. See onboarding for
[Claude Code](references/onboarding.md#claude-code) and
[OpenCode V2](references/onboarding.md#opencode-v2).

| Task | Skill |
| --- | --- |
| Define an issue/PR or product decision | `engineering-intake` |
| Diagnose a difficult defect | `engineering-diagnosis` |
| Review a diff | `engineering-review` |
| Survey architecture or prototype a design | `engineering-exploration` |
| Stress-test requirements, a plan, or a design | `grill-me` |
| Improve skills or steering files | `agent-instruction-design` |
| Prepare verified manual provider steps | `human-setup-guide` |
| Design or review a frontend | `ui-design` |
| Create animated artwork or a product showcase video | `motion-design`; pair with `music-composition` for original sound |
| Storyboard and edit footage with speech, blending, transitions and keyframes | `video-editing` |
| Transcribe speech or generate narration | `speech-to-text` or `text-to-speech` |
| Restore dialogue and mix audio | `audio-editing` |
| Index static fonts and lay out titles/captions | `typography` |
| Compose original music, sonic logos, or timed sound effects | `music-composition` |
| Build or prepare a Chrome extension | `chrome-extensions` |
| Select modern web APIs and fallbacks | `modern-web-guidance` |
| Authenticate or work with Supabase CLI | `supabase-cli` |
| Authenticate or work with Vercel CLI | `vercel-account-operations` |

In Codex, route plain-language Git repository code, documentation, configuration, or
artifact planning/edits to `standard-development-workflow`, including terse follow-ups.
Ordinary gates apply; only direct `$sdlc-loop` invocation activates its separate
validated autopilot profile. For tracked worktree edits, open/update and read back
a reviewable PR before handoff unless explicitly local-only. Follow the workflow's
decomposition contract; child merges do not authorize a parent merge to `main`.

Before provider setup, credentials, or external writes, read
[task authority and concealed secrets](references/task-authority-and-secrets.md).
Necessary in-scope steps reuse task authority; explicit user instructions override
skill preferences, while platform restrictions remain enforced.
For Supabase, Railway, Vercel, Cloudflare, DigitalOcean, ERPNext, or Excalidraw, read
[CLI and browser assistance](references/service-browser-operations.md): use an
authenticated client, supported browser-assisted login when needed, then verify
account/project. Browser operations are fallback for client capability gaps.
Supabase, Vercel, Railway, Cloudflare, and DigitalOcean CLI credentials belong in the project's gitignored `.cli/`;
carry them and local env files into same-project worktrees using the shared
credential contract.
For other browser steps, read [browser selection](references/browser-selection.md);
in Codex prefer the in-app browser unless the user or capability requires another;
in Claude Code use Claude in Chrome when it is connected.

Keep deliverables and corrections current across turns. For authenticated sources
or multiple consoles, use [task continuity](references/task-continuity.md) before
completion claims. For an existing explicit host goal, use
[ordinary Goal continuity](references/ordinary-goal-continuity.md) on continuation.

## Available skills

- `academic-writing-workflow` (codex, claude-code, opencode)
- `engineering-intake` (codex, claude-code, opencode)
- `engineering-diagnosis` (codex, claude-code, opencode)
- `engineering-review` (codex, claude-code, opencode)
- `engineering-exploration` (codex, claude-code, opencode)
- `grill-me` (codex, claude-code, opencode)
- `agent-instruction-design` (codex, claude-code, opencode)
- `human-setup-guide` (codex, claude-code, opencode)
- `cloudflare-account-operations` (codex, claude-code, opencode)
- `digitalocean-account-operations` (codex, claude-code, opencode)
- `erpnext-accounting-finance` (codex, claude-code, opencode)
- `erpnext-buying-stock` (codex, claude-code, opencode)
- `erpnext-content-analytics` (codex, claude-code, opencode)
- `erpnext-manufacturing-assets` (codex, claude-code, opencode)
- `erpnext-operations` (codex, claude-code, opencode)
- `erpnext-organization-administration` (codex, claude-code, opencode)
- `erpnext-people-projects-support` (codex, claude-code, opencode)
- `erpnext-sales-crm` (codex, claude-code, opencode)
- `excalidraw-api-operations` (codex, claude-code, opencode)
- `excalidraw-scene-operations` (codex, claude-code, opencode)
- `railway-account-operations` (codex, claude-code, opencode)
- `vercel-account-operations` (codex, claude-code, opencode)
- `supabase-cli` (codex, claude-code, opencode)
- `literature-review-workflow` (codex, claude-code, opencode)
- `guided-writing-coach` (codex, claude-code, opencode)
- `restaurant-marketing-management` (codex, claude-code, opencode)
- `david-jones-till-sales` (codex, claude-code, opencode)
- `systematic-literature-review-workflow` (codex, claude-code, opencode)
- `trend-product-design` (codex, claude-code, opencode)
- `trend-product-discovery` (codex, claude-code, opencode)
- `trend-product-onboarding` (codex, claude-code, opencode)
- `trend-product-operations` (codex, claude-code, opencode)
- `trend-product-opportunity` (codex, claude-code, opencode)
- `qr-code-generation` (codex, claude-code, opencode)
- `humanizer` (codex, claude-code, opencode)
- `verified-literature-research` (codex, claude-code, opencode)
- `payloadcms-development` (codex, claude-code, opencode)
- `youtube-content-inspection` (codex, claude-code, opencode)
- `youtube-library-sync` (codex, claude-code, opencode)
- `youtube-media-operations` (codex, claude-code, opencode)
- `ui-design` (codex, claude-code, opencode)
- `video-editing` (codex, claude-code, opencode)
- `speech-to-text` (codex, claude-code, opencode)
- `text-to-speech` (codex, claude-code, opencode)
- `audio-editing` (codex, claude-code, opencode)
- `typography` (codex, claude-code, opencode)
- `motion-design` (codex, claude-code, opencode)
- `music-composition` (codex, claude-code, opencode)
- `chrome-extensions` (codex, claude-code, opencode)
- `modern-web-guidance` (codex, claude-code, opencode)

For installation and plugin troubleshooting, see [plugin-troubleshooting.md](references/plugin-troubleshooting.md), the plugin troubleshooting runbook.

See [onboarding](references/onboarding.md) for installation and the [registry](references/plugin-registry.md) for package status.
