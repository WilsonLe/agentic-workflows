---
name: amsoft-agentic-workflows
description: Introduce, onboard, and route work across the AMSoft Agentic Workflows suite. Use when the user asks to set up, onboard, or get started with the plugin; asks what AMSoft workflows are available; needs help choosing a bundled capability; or wants a task routed among software delivery, ERPNext operations, academic writing, Humanizer, food image editing, WordPress, DigitalOcean, Cloudflare, Railway, and encrypted configuration transfer.
---

# AMSoft Agentic Workflows

Act as the front door to AMSoft's curated agentic workflow suite. Explain the available capabilities plainly, select the smallest relevant workflow, and preserve the safety and verification rules of the selected skill.

## Onboard the user

For setup, onboarding, or first-use requests, read
[onboarding.md](references/onboarding.md). Follow the central flow, then read only the onboarding
guides for the selected components. Return a readiness summary and copy-ready first prompts.

Do not ask for secrets, perform an infrastructure write, edit an image, or begin
academic drafting merely to prove that the plugin is installed.

## Introduce the suite

When asked to introduce AMSoft Agentic Workflows, explain:

- It is one installable AMSoft plugin that groups reviewed workflows under a single ChatGPT plugin.
- Standard Development Workflow starts each change in a fully onboarded isolated worktree, creates a
  spec-ready GitHub issue and exhaustive implementation/test plan, waits for approval before
  coding, opens a tested draft PR, squash-merges and cleans up after approval, and deploys to
  staging only after a separate confirmation. It never automatically deploys to production.
- Academic Writing starts from a task sheet, creates a context-complete execution plan for fresh-session handoff, and proceeds through reviewed outlines, verified paper notes, drafting, and final QA.
- Humanizer rewrites or audits prose to remove formulaic AI-writing patterns while preserving meaning and truthfulness.
- Food Image Editing critiques food photographs and food-video stills, measures tone,
  color, clipping, composition zones, and angle, then applies only deterministic
  pixel-level corrections. Its advanced adjustment-layer stack uses masked copies
  of source-derived pixels for food-specific local corrections; it never uses
  image generation, generative fill, cloning, or scene reconstruction.
- AMSoft DigitalOcean Account Operations uses `doctl` with a user-provided
  `DIGITALOCEAN_ACCESS_TOKEN`, including help-driven debugging and approval-gated runbooks.
- AMSoft Cloudflare Account Operations uses `curl` and Wrangler with a user-provided
  `CLOUDFLARE_API_TOKEN` for safe inspection and approval-gated changes.
- AMSoft Railway Account Operations uses the official Railway CLI with a
  user-selected account token created with **No workspace**, protected local
  storage, exact-target approval gates, and separate production confirmation.
- AMSoft Config Transfer exports allowlisted workflow preferences and supported
  Railway, Cloudflare, and DigitalOcean credentials into one authenticated-encrypted
  `.amsoftx` file. Same-machine transfers use the OS user credential store;
  cross-machine and cross-OS transfers use a locally entered passphrase.
- WordPress CLI Operations discovers bare-metal or Docker Compose runtimes and safely operates the
  intended installation over authorized SSH with WP-CLI, backups, rollback, and live verification.
- WordPress Site Management builds, redesigns, and administers sites through discovered WordPress
  REST capabilities and the real administrator/public UI using user-provided authenticated access.
- ERPNext Operations onboards from a user-selected API key file, stores a protected owner-read-only
  copy, and safely operates organization administration, accounts, sales, buying, stock,
  manufacturing, quality, maintenance, HR, projects, support, website, knowledge, and analytics.
- Cloud and infrastructure operations in this suite are CLI-first and do not
  bundle MCP servers.
- New workflows should be added only when their source, permissions, validation, and rendered ChatGPT plugin state have been verified.
- Every authored plugin must register itself in the central registry before its authoring workflow is complete.

Keep the introduction concise and relevant to the user's work. Do not claim capabilities that are not bundled.

## Route the task

- For repository feature, fix, refactor, or release work that should proceed through an isolated
  worktree, spec-ready GitHub issue, review-gated plan, tested draft PR, squash merge, cleanup, and
  optional staging verification, use `standard-development-workflow`.
- For ERPNext onboarding, authentication, organization administration, accounting, sales, buying,
  stock, manufacturing, quality, maintenance, HR, projects, support, website, content, reports, or
  analytics, use `amsoft-erpnext-operations`, then its smallest relevant domain skill.
- For humanizing, de-AI editing, voice matching, or AI-pattern review, use the bundled `humanizer` skill.
- For food-photo critique, angle-aware composition, cropping, masked adjustment
  layers, color correction, tone adjustment, or preparation of food-video
  stills, use `food-image-editing`.
- For task-sheet planning, academic research, research-note production, reviewed outlines, drafting, or final academic QA, use `academic-writing-workflow`. Load `verified-literature-research` for the research phase.
- For Cloudflare accounts, zones, DNS, Workers, Pages, storage, rules, incidents, or API operations, use the bundled `amsoft-cloudflare-account-operations` skill.
- For DigitalOcean accounts, Droplets, networking, DNS, Kubernetes, databases, registries,
  projects, billing, incidents, or doctl debugging, use the bundled
  `amsoft-digitalocean-account-operations` skill.
- For Railway onboarding, workspaces, projects, environments, services,
  deployments, variables, logs, domains, volumes, scaling, incidents, or CLI
  debugging, use `amsoft-railway-account-operations`.
- For exporting, backing up, moving, restoring, or importing AMSoft workflow
  configuration and supported cloud credentials, use
  `amsoft-agentic-workflows-config-transfer`.
- For SSH, WP-CLI, WordPress runtime discovery, database work, caches, cron, core, plugins, themes,
  multisite, server maintenance, or recovery, use `wordpress-cli-operations`.
- For WordPress pages, posts, blocks, media, menus, templates, content architecture, redesigns,
  administrator workflows, REST API work, accessibility, SEO, performance, responsive QA, or
  publishing, use `wordpress-site-management`.
- For WordPress requests that cross both layers, use `wordpress-site-management` for the site and
  rendered experience and `wordpress-cli-operations` for server/runtime changes.
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
| Standard software delivery | `standard-development-workflow` | Deliver a repository change from an isolated worktree through a spec-ready issue, approved plan, tested draft PR, squash merge, cleanup, and separately approved staging |
| Academic writing | `academic-writing-workflow` | Convert a task sheet into a portable plan, conduct verified research, and progress through review-gated drafting |
| Literature research | `verified-literature-research` | Download, verify, read, and note real papers, then map them into an outline |
| Natural writing | `humanizer` | Humanize a draft, match a voice sample, audit AI tells |
| Food image editing | `food-image-editing` | Critique and non-generatively correct food photographs or food-video stills using measurable, angle-aware edits and masked adjustment-layer stacks |
| DigitalOcean operations | `amsoft-digitalocean-account-operations` | Inspect resources, operate DigitalOcean with doctl, and debug requests through CLI help |
| Cloudflare operations | `amsoft-cloudflare-account-operations` | Inspect zones, manage DNS, operate Workers, and diagnose incidents from the CLI |
| Railway operations | `amsoft-railway-account-operations` | Onboard a protected account token, inspect Railway resources, and run exact-target approval-gated changes and deployments |
| Encrypted config transfer | `amsoft-agentic-workflows-config-transfer` | Export one encrypted workflow-and-credential file or import an attached `.amsoftx` file transactionally across macOS and Windows |
| WordPress CLI operations | `wordpress-cli-operations` | Discover Docker or bare-metal WordPress runtimes and manage installations safely over SSH with WP-CLI |
| WordPress site management | `wordpress-site-management` | Build, redesign, administer, and visually verify WordPress through authenticated REST and browser workflows |
| ERPNext operations | `amsoft-erpnext-operations` | Onboard an API user from a protected key file and safely operate ERPNext across administrative and business domains |
| ERPNext organization administration | `amsoft-erpnext-organization-administration` | Manage companies, users, roles, permissions, defaults, settings, email, and workspaces |
| ERPNext accounting and finance | `amsoft-erpnext-accounting-finance` | Operate invoices, payments, ledgers, banking, taxes, assets, budgets, closing, and reports |
| ERPNext sales and CRM | `amsoft-erpnext-sales-crm` | Operate leads, quotations, orders, delivery, invoicing, POS, pricing, loyalty, and campaigns |
| ERPNext buying and stock | `amsoft-erpnext-buying-stock` | Operate procurement, suppliers, items, warehouses, inventory, batches, serials, and valuation |
| ERPNext manufacturing and assets | `amsoft-erpnext-manufacturing-assets` | Operate BOMs, production, job cards, quality, maintenance, assets, and fleet |
| ERPNext people, projects and support | `amsoft-erpnext-people-projects-support` | Operate installed HR, project, timesheet, issue, SLA, and service workflows |
| ERPNext content and analytics | `amsoft-erpnext-content-analytics` | Operate website, portal, knowledge, newsletters, reports, dashboards, imports, and exports |

Read [plugin-registry.md](references/plugin-registry.md) when introducing the complete registered
plugin catalog or authoring and updating a plugin. Distinguish bundled capabilities from cataloged
entries.

## Verification

Before stating that a routed task is complete, apply the selected skill's verification requirements. Never replace visible UI or live-service verification with a filesystem change, cache entry, or command-line status when the user expects a real rendered or deployed result.
