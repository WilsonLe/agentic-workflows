---
name: agentic-workflows
description: Route plain repository edit requests to the Standard Development Workflow and other tasks to the appropriate Agentic Workflows skill; explain installation and setup.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Agentic Workflows

Select the task's skill and read its prerequisites and verification rules. Request
access only when needed. Focused engineering methods complement repository delivery
rules; they do not replace authority or PR gates.

| Task | Skill |
| --- | --- |
| Define an issue/PR or product decision | `engineering-intake` |
| Diagnose a difficult defect | `engineering-diagnosis` |
| Review a diff | `engineering-review` |
| Survey architecture or prototype a design | `engineering-exploration` |
| Improve skills or steering files | `agent-instruction-design` |
| Prepare verified manual provider steps | `human-setup-guide` |
| Design or review a frontend | `ui-design` |
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
Supabase and Vercel CLI credentials belong in the project's gitignored `.cli/`;
carry them and local env files into same-project worktrees using the shared
credential contract.
For other browser steps, read [browser selection](references/browser-selection.md);
in Codex prefer the in-app browser unless the user or capability requires another.

Keep deliverables and corrections current across turns. For authenticated sources
or multiple consoles, use [task continuity](references/task-continuity.md) before
completion claims. For an existing explicit host goal, use
[ordinary Goal continuity](references/ordinary-goal-continuity.md) on continuation.

## Available skills

- `academic-writing-workflow` (codex, claude-code)
- `agentic-workflows-config-transfer` (codex)
- `engineering-intake` (codex, claude-code)
- `engineering-diagnosis` (codex, claude-code)
- `engineering-review` (codex, claude-code)
- `engineering-exploration` (codex, claude-code)
- `agent-instruction-design` (codex, claude-code)
- `human-setup-guide` (codex, claude-code)
- `session-reflection` (codex)
- `orchestration` (codex)
- `sdlc-loop` (codex)
- `cloudflare-account-operations` (codex, claude-code)
- `calorie-tracker` (codex)
- `digitalocean-account-operations` (codex, claude-code)
- `erpnext-accounting-finance` (codex, claude-code)
- `erpnext-buying-stock` (codex, claude-code)
- `erpnext-content-analytics` (codex, claude-code)
- `erpnext-manufacturing-assets` (codex, claude-code)
- `erpnext-operations` (codex, claude-code)
- `erpnext-organization-administration` (codex, claude-code)
- `erpnext-people-projects-support` (codex, claude-code)
- `erpnext-sales-crm` (codex, claude-code)
- `excalidraw-api-operations` (codex, claude-code)
- `excalidraw-scene-operations` (codex, claude-code)
- `railway-account-operations` (codex, claude-code)
- `vercel-account-operations` (codex, claude-code)
- `supabase-cli` (codex, claude-code)
- `literature-review-workflow` (codex, claude-code)
- `guided-writing-coach` (codex, claude-code)
- `restaurant-marketing-management` (codex, claude-code)
- `david-jones-till-sales` (codex, claude-code)
- `systematic-literature-review-workflow` (codex, claude-code)
- `trend-product-design` (codex, claude-code)
- `trend-product-discovery` (codex, claude-code)
- `trend-product-onboarding` (codex, claude-code)
- `trend-product-operations` (codex, claude-code)
- `trend-product-opportunity` (codex, claude-code)
- `food-image-editing` (codex)
- `qr-code-generation` (codex, claude-code)
- `humanizer` (codex, claude-code)
- `standard-development-workflow` (codex)
- `verified-literature-research` (codex, claude-code)
- `payloadcms-development` (codex, claude-code)
- `youtube-content-inspection` (codex, claude-code)
- `youtube-library-sync` (codex, claude-code)
- `youtube-media-operations` (codex, claude-code)
- `reddit-browsing` (codex)
- `ui-design` (codex, claude-code)
- `chrome-extensions` (codex, claude-code)
- `modern-web-guidance` (codex, claude-code)

For installation and plugin troubleshooting, see [plugin-troubleshooting.md](references/plugin-troubleshooting.md), the plugin troubleshooting runbook.

See [onboarding](references/onboarding.md) for installation and the [registry](references/plugin-registry.md) for package status.

Codex automatic session naming uses the bundled user-prompt hook and an ephemeral fast model
with low reasoning, capped at 10 words; see [session-title-policy.md](references/session-title-policy.md) for title rules, opt-out, and host support.
