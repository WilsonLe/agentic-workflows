---
name: amsoft-agentic-workflows
description: Introduce, onboard, and route work across the AMSoft Agentic Workflows suite. Use when the user asks to set up, onboard, or get started with the plugin; asks what AMSoft workflows are available; needs help choosing a bundled capability; or wants a task routed among software delivery, YouTube, restaurant marketing, ERPNext, writing, image editing, WordPress, cloud providers, Excalidraw REST operations, and encrypted configuration transfer.
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
- Standard Development Workflow reuses or refreshes provenance-backed repository capabilities,
  starts each change in an isolated worktree, creates a spec-ready issue and scoped execution
  contract, runs repository-derived fail-fast and state-isolated validation, resumes long
  operations safely, freezes final evidence to immutable source/artifact identities, opens a
  tested draft PR, and deploys to staging only after a separate confirmation. It never
  automatically deploys to production.
- Academic Writing starts from a task sheet, creates a context-complete execution plan for fresh-session handoff, and proceeds through reviewed outlines, verified paper notes, drafting, and final QA.
- Humanizer rewrites or audits prose to remove formulaic AI-writing patterns while preserving meaning and truthfulness.
- Food Image Editing inventories and ranks food-photo candidates, creates a
  concise main HTML curation report plus linked per-dish reports with complete
  candidate reasoning, measures tone, color, clipping, composition zones, and
  angle, then applies only deterministic pixel-level corrections. Its advanced
  adjustment-layer stack uses geometric or
  arbitrary finite canvas rotation, a reviewed Lab/Luv color-similarity mask preview,
  deterministic cleanup and mask composition, and masked copies of
  source-derived pixels for food-specific local corrections. Every new mask
  preview includes binary fill, outline, soft alpha,
  overlay, and provenance; it never uses image generation, generative fill,
  cloning, or scene reconstruction.
- Restaurant Marketing Management turns new dishes, offers, seasonal menus, events, slow periods,
  local discovery, reputation, retention, openings, and relaunches into truthful, margin-aware,
  approval-gated, and measurable campaigns.
- AMSoft YouTube operations inspect exact YouTube URLs without media, retrieve only authorized
  video/audio/sections, and incrementally sync bounded playlists or channels through yt-dlp.
  Account-gated access uses a browser-exported, YouTube-only Netscape cookie file installed in
  owner-protected local storage; cookies are never transferred or shown in chat or evidence.
- AMSoft DigitalOcean Account Operations uses `doctl` with a user-provided
  `DIGITALOCEAN_ACCESS_TOKEN`, including help-driven debugging and approval-gated runbooks.
- AMSoft Cloudflare Account Operations uses `curl` and Wrangler with a user-provided
  `CLOUDFLARE_API_TOKEN` for safe inspection and approval-gated changes.
- AMSoft Railway Account Operations uses the official Railway CLI with a
  user-selected account token created with **No workspace**, protected local
  storage, exact-target approval gates, and separate production confirmation.
- AMSoft Excalidraw API Operations uses a protected user-confirmed personal
  MCP/API key with the Excalidraw Plus REST API, never MCP. It provides broad
  collection, scene, content, workspace, user, invite, and log reads plus
  request-authorized non-destructive writes and destructively gated deletion.
- AMSoft Excalidraw Scene Operations focuses on one exact scene: protected
  backup, empty-scene creation, metadata update, incremental content PATCH,
  validated request-authorized authoritative PUT, destructively gated deletion,
  canonical readback, and unknown-outcome recovery without blind write retry.
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
- New workflows should be added only when their source, permissions, validation,
  and authoritative installed plugin state have been verified. Native Plugins UI
  evidence is optional when the platform blocks self-inspection.
- Every authored plugin must register itself in the central registry before its authoring workflow is complete.

Keep the introduction concise and relevant to the user's work. Do not claim capabilities that are not bundled.

## Route the task

- For repository feature, fix, refactor, or release work that should proceed through reusable
  capability discovery, an isolated worktree, a scoped execution contract, fail-fast validation,
  resumable operations, frozen evidence, a tested draft PR, squash merge, cleanup, and optional
  staging verification, use `standard-development-workflow`.
- For ERPNext onboarding, authentication, organization administration, accounting, sales, buying,
  stock, manufacturing, quality, maintenance, HR, projects, support, website, content, reports, or
  analytics, use `amsoft-erpnext-operations`, then its smallest relevant domain skill.
- For humanizing, de-AI editing, voice matching, or AI-pattern review, use the bundled `humanizer` skill.
- For food-photo shortlisting, shoot curation, candidate ranking, linked main and
  per-dish HTML curation reports, critique, angle-aware composition, cropping,
  safe rotation, bounded four-corner perspective rectification, crop-versus-warp
  decisions,
  masked adjustment layers, color-derived selection, outline or alpha-mask
  preview, mask cleanup or combination, color correction, tone adjustment,
  curves, HSL, vignette, sharpening, Grain-versus-Film-Grain decisions, or
  preparation of food-video stills, use `food-image-editing`.
- For restaurant marketing, including a new dish, offer, seasonal menu, event, slow daypart, local
  discovery, reputation, retention, opening, or relaunch, use
  `amsoft-restaurant-marketing-management`.
- For media-free YouTube metadata, format, subtitle, thumbnail, chapter, playlist, channel, or
  live-state inspection, use `amsoft-youtube-content-inspection`.
- For authorized YouTube video, audio, subtitle, thumbnail, chapter, section, SponsorBlock, or
  experimental live retrieval, use `amsoft-youtube-media-operations`.
- For bounded incremental YouTube playlist or channel archives with download-archive semantics,
  use `amsoft-youtube-library-sync`.
- For task-sheet planning, academic research, research-note production, reviewed outlines, drafting, or final academic QA, use `academic-writing-workflow`. Load `verified-literature-research` for the research phase.
- For Cloudflare accounts, zones, DNS, Workers, Pages, storage, rules, incidents, or API operations, use the bundled `amsoft-cloudflare-account-operations` skill.
- For DigitalOcean accounts, Droplets, networking, DNS, Kubernetes, databases, registries,
  projects, billing, incidents, or doctl debugging, use the bundled
  `amsoft-digitalocean-account-operations` skill.
- For Railway onboarding, workspaces, projects, environments, services,
  deployments, variables, logs, domains, volumes, scaling, incidents, or CLI
  debugging, use `amsoft-railway-account-operations`.
- For Excalidraw Plus onboarding, collections, workspace inventory, API
  permissions, users, invites, logs, or broad REST API work, use
  `amsoft-excalidraw-api-operations`.
- For creating, inspecting, renaming, pinning, moving, backing up, patching,
  replacing, verifying, or soft-deleting one Excalidraw scene, use
  `amsoft-excalidraw-scene-operations`.
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
5. For plugin authoring or updates, verify normalized name, exact installed
   version, enabled status, resolved source, installed cache, and changed-file
   parity. Prefer rendered Plugins UI proof when accessible, but never require
   Computer Use or user intervention solely to obtain it.
6. For plugin authoring or updates, apply the `amsoft-plugin-authoring-policy` gate and update the central registry.

## Current capability map

| Capability | Bundled skill | Typical requests |
| --- | --- | --- |
| Standard software delivery | `standard-development-workflow` | Deliver a repository change through provenance-backed discovery, an isolated worktree, approved scope/resource/channel contracts, fail-fast state-isolated validation, resumable operations, frozen evidence, a tested draft PR, cleanup, and separately approved staging |
| Academic writing | `academic-writing-workflow` | Convert a task sheet into a portable plan, conduct verified research, and progress through review-gated drafting |
| Literature research | `verified-literature-research` | Download, verify, read, and note real papers, then map them into an outline |
| Natural writing | `humanizer` | Humanize a draft, match a voice sample, audit AI tells |
| Food image curation and editing | `food-image-editing` | Rank every candidate, create linked HTML reports, build researched adjustment and composition briefs, compare crop hypotheses, apply truthful bounded perspective rectification when justified, and non-generatively correct food photographs using measurable edits and source-derived layers |
| Restaurant marketing management | `amsoft-restaurant-marketing-management` | Manage new-dish, offer, seasonal, event, local discovery, reputation, retention, and launch campaigns through truth, economics, approvals, measurement, expiry, and learning |
| YouTube content inspection | `amsoft-youtube-content-inspection` | Inspect exact YouTube URLs, formats, captions, thumbnails, chapters, playlists, channels, and live state without downloading media |
| YouTube media operations | `amsoft-youtube-media-operations` | Retrieve authorized video, audio, subtitles, thumbnails, chapters, sections, and experimental live media with bounded yt-dlp options and protected cookies |
| YouTube library sync | `amsoft-youtube-library-sync` | Incrementally archive bounded, authorized playlist or channel items with resumable downloads and verified archive semantics |
| DigitalOcean operations | `amsoft-digitalocean-account-operations` | Inspect resources, operate DigitalOcean with doctl, and debug requests through CLI help |
| Cloudflare operations | `amsoft-cloudflare-account-operations` | Inspect zones, manage DNS, operate Workers, and diagnose incidents from the CLI |
| Railway operations | `amsoft-railway-account-operations` | Onboard a protected account token, inspect Railway resources, and run exact-target approval-gated changes and deployments |
| Excalidraw API operations | `amsoft-excalidraw-api-operations` | Onboard a protected personal key and inspect collections, scenes, workspace resources, permissions, errors, and rate limits through REST only |
| Excalidraw scene operations | `amsoft-excalidraw-scene-operations` | Create, back up, patch, replace, verify, and recover one exact scene without second confirmation for non-destructive writes; deletion retains its destructive gate |
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

Before stating that a routed task is complete, apply the selected skill's
verification requirements. Plugin-package verification may use authoritative
CLI and installed-cache evidence when native self-inspection is prohibited.
Never replace visible UI or live-service verification with filesystem or
command-line status when the user explicitly requested a real rendered or
deployed result.
