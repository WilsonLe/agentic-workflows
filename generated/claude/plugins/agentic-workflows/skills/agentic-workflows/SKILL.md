---
name: agentic-workflows
description: Route plain repository edit requests to the Standard Development Workflow and other tasks to the appropriate Agentic Workflows skill; explain installation and setup.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Agentic Workflows

Choose the skill that matches the requested task. Read its prerequisites before starting; request missing access only when that task needs it. Follow the selected skill's approval and verification rules.
In Codex, select `standard-development-workflow` for a plain-language request to plan or make code, documentation, configuration, or artifact changes in a Git repository, even if the user did not name a skill. A terse follow-up keeps that active route. Use ordinary workflow gates; only a direct `$sdlc-loop` invocation activates its separate autopilot authority.
Keep the user's requested deliverables and later corrections current across turns. For tasks with
authenticated sources or several provider consoles, follow
[task continuity](references/task-continuity.md) before claiming the result is complete.
For repository edits made in a Git worktree, open or update a reviewable PR and read it back
before the final handoff, unless the user explicitly requested local-only changes. Route large
multi-outcome software work through the Standard Development Workflow's issue decomposition
contract; never infer approval for a parent-branch merge to `main` from child PR merges.

## Available skills

- `academic-writing-workflow` (codex, claude-code)
- `cloudflare-account-operations` (codex, claude-code)
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
- `qr-code-generation` (codex, claude-code)
- `humanizer` (codex, claude-code)
- `verified-literature-research` (codex, claude-code)
- `payloadcms-development` (codex, claude-code)
- `youtube-content-inspection` (codex, claude-code)
- `youtube-library-sync` (codex, claude-code)
- `youtube-media-operations` (codex, claude-code)

For installation and plugin troubleshooting, see [plugin-troubleshooting.md](references/plugin-troubleshooting.md), the plugin troubleshooting runbook.

See [onboarding](references/onboarding.md) for installation and the [registry](references/plugin-registry.md) for package status.

with low reasoning, capped at 10 words; see [session-title-policy.md](references/session-title-policy.md) for title rules, opt-out, and host support.
