---
name: wordpress-project-management
description: Coordinate safe WordPress project and site management across content, navigation, media, themes, plugins, integrations, SEO, CLI/runtime, browser verification, repository changes, and release gates. Use when a WordPress request crosses multiple surfaces, manages content as code, needs remote synchronization or checksum-guarded writes, or requires explicit local/staging/production evidence and rollback boundaries.
---

# WordPress Project Management

Use this skill as the project-level orchestrator for WordPress work. It composes the existing
`wordpress-site-management`, `wordpress-cli-operations`, `amsoft-wordpress-seo-management`, and
`wordpress-stream-audit-logging` skills; it does not replace their specialist procedures or add a
runtime WordPress plugin.

When the repository proves the bundled `wp_content_sync.py` helper and the
AMSoft runtime contract are available, compose
`amsoft-wordpress-git-sync-management` for implementation, migration, and
operation. Project Management remains the coordinator; Git Sync owns the
canonical object, lock, adapter, CAS, automation, and runbook mechanics.

The standalone `wordpress-content` and `wordpress-devops` plugins are the
primary separation boundary for new work. Use `amsoft-wordpress-content-management`
for user-facing pages, posts, design systems/tokens, images, media, and video;
use `amsoft-wordpress-devops-management` for hosting, provider targets, SSH, WP-CLI,
plugins, filesystems, runtime, deployments, and infrastructure-as-code
commits. Compose both only when the request genuinely crosses those surfaces.
This project layer coordinates the handoff and evidence; it does not merge
their credentials or turn a content update into infrastructure-as-code.

## Use the project layer when

- a request crosses content, presentation, runtime, integrations, SEO, audit, browser, repository,
  or release surfaces;
- the site needs onboarding, an inventory, a change plan, a release handoff, or incident recovery;
- content is managed as code or a remote page/post must be synchronized before a write;
- the user needs a truthful distinction between source, site, browser, CI, deployment, and provider
  evidence;
- local, staging, and production identity or approval boundaries must be resolved.

Use a specialist directly for a narrow operation. Compose only the layers required by the outcome.
For server, database, filesystem, cache, cron, core, plugin, theme, or deployment work, load
`amsoft-wordpress-devops-management` (and its `wordpress-cli-operations` compatibility specialist when
needed). For page, post, block, media, menu, template, REST, UI, responsive, design-token, or
publication work, load `amsoft-wordpress-content-management` (and its `wordpress-site-management`
compatibility specialist when needed). Keep SEO and Stream policies authoritative
when those domains are involved.

## Required first read

Before planning a project change, read:

1. [onboarding-and-state.md](references/onboarding-and-state.md);
2. [lifecycle-and-gates.md](references/lifecycle-and-gates.md);
3. [surfaces-and-evidence.md](references/surfaces-and-evidence.md);
4. [site-management.md](references/site-management.md) for site-facing work;
5. [content-as-code-and-concurrency.md](references/content-as-code-and-concurrency.md) for
   managed content or any remote write;
6. the relevant browser, integration, drift/rollback, and issue/plan references.

## Project operating loop

Run this sequence and report the state of each stage:

1. **Discover:** resolve the project, exact site, environment, owner, source of truth, runtime,
   WordPress architecture, managed objects, and available verification channels.
2. **Classify:** name the requested site surface, authorization, lifecycle target, and specialist
   composition. A plan request never authorizes a write.
3. **Plan/spec:** define acceptance criteria, managed fields, source/repository changes, remote
   effects, evidence, backup, rollback, and unresolved facts.
4. **Approve/isolate:** use the approved issue/plan, exact base revision, isolated worktree, and
   environment-specific target. Do not infer production approval from PR approval.
5. **Sync/snapshot:** read the current target immediately before any write. For content-as-code,
   use the checksum/revision guard in the content reference; if atomic protection is unavailable,
   remain plan-only or blocked.
6. **Change narrowly:** use the authorized specialist and only the managed fields/scope. Never
   bypass a content guard with a raw REST, WP-CLI, wp-admin, builder, or bulk write.
7. **Read back:** re-fetch the exact object/configuration and compare the intended fields and
   revision/checksum.
8. **Verify surfaces:** test the requested authenticated/private, logged-out/public, responsive,
   console/network, provider, repository, CI, or deployment surface separately.
9. **Handoff:** report `planned`, `changed`, `read_back`, `verified`, `blocked`, `released`, and
   `published` independently. Record cache, indexing, provider, and recrawl limitations.

## Fail-closed rules

- Do not write when canonical URL, environment, object identity, authorization, source of truth,
  runtime, or target fingerprint is unknown or contradictory.
- Do not overwrite a local content file or remote object when its baseline revision/checksum has
  drifted. Pull, show the diff, and require reconciliation.
- Do not call a separate GET-compare-POST sequence an atomic concurrency guarantee. Production and
  shared staging content-as-code writes require an atomic compare-and-swap adapter.
- Do not treat API/WP-CLI success, HTTP 200, wp-admin, a screenshot, CI, health, or a merged PR as
  proof of another surface.
- Do not publish a draft/private/noindex/coming-soon object without the separate publication gate.
- Never store credentials, cookies, nonces, tokens, private submissions, or raw authorization
  headers in state, locks, examples, logs, issues, or PRs.

## References

- [onboarding and state](references/onboarding-and-state.md) — project inventory and secret-free
  state record;
- [lifecycle and gates](references/lifecycle-and-gates.md) — authority, approvals, and release
  state transitions;
- [site management](references/site-management.md) — content, IA, media, presentation, plugins,
  forms, SEO, privacy, and operational site surfaces;
- [surfaces and evidence](references/surfaces-and-evidence.md) — what each channel proves;
- [browser and private pages](references/browser-and-private-pages.md) — authenticated/public and
  rendered verification;
- [integrations and data flows](references/integrations-and-data-flows.md) — install through
  collection and privacy boundaries;
- [drift, rollback, and incidents](references/drift-rollback-and-incidents.md) — recovery units and
  stop conditions;
- [content as code and concurrency](references/content-as-code-and-concurrency.md) — proposed
  `wp-content-sync` command contract and checksum guard;
- [issue and plan handoffs](references/issue-and-plan-handoffs.md) — spec, PR, release, and evidence
  handoff.

The `wp-content-sync` command described in the content reference is implemented
by the optional WordPress Git Sync package and mirrored helper. Do not run it
unless the current project proves that the helper, project contract, and
compatible server runtime are installed and discovered. A missing or
incompatible adapter remains a blocking condition for a strict content-as-code
write, not permission to substitute an unsafe command.
