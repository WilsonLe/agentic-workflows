---
name: wordpress-git-sync-management
description: Inspect, adopt, and operate guarded two-way synchronization between Git and explicitly managed WordPress pages, posts, Site Editor entities, patterns, media manifests, ACF data, and Git-owned code using stable identities, canonical hashes, atomic compare-and-swap, reviewed automation, and rollback-first runbooks.
---

# WordPress Git Sync Management

Use this skill only when the repository proves the `wp-content-sync` helper
and AMSoft WordPress Git Sync runtime are available. It implements the
content-as-code interface coordinated by `wordpress-project-management`; it
does not replace WordPress Content, DevOps, Site Management, CLI, SEO, audit,
browser, or Standard Development Workflow authority.

## Required composition

- Use `wordpress-project-management` as coordinator for any cross-surface or
  existing-project adoption task.
- Use `wordpress-content-management` for page/post/media intent and rendered
  verification. Use `wordpress-devops-management` for runtime/theme/plugin
  source, installation, deployment, filesystem, backup, and rollback.
- Use Standard Development Workflow for repository changes and reviewed pull
  requests. Merge never authorizes a WordPress apply.
- Keep the WordPress Application Password reference separate from provider,
  SSH, GitHub, and Git credentials. Never request a secret through chat or
  place one in a command argument, environment value, Git file, issue, log, or
  artifact.

## Required first read

Read, in order:

1. [contract and ownership](references/contract-and-ownership.md);
2. [CLI and runtime](references/cli-and-runtime.md);
3. [entity adapters](references/entity-adapters.md);
4. [code, media, and extensions](references/code-media-and-extensions.md);
5. [reviewed automation](references/github-automation.md);
6. [existing-project adoption](references/existing-project-adoption.md);
7. the applicable [operator runbooks](references/runbooks.md); and
8. [assurance and rollback](references/assurance-and-rollback.md).

## Operating loop

1. **Resolve:** exact project, repository/ref, canonical HTTPS site,
   environment, owner, runtime, installed helper/runtime versions, credential
   references, and verification channels.
2. **Inventory:** use read-only discovery. Classify every surface exactly once
   as Git-owned code, managed database content, manifest media, environment
   configuration, runtime-generated, unsupported/read-only, or excluded.
3. **Contract:** review stable identities, field ownership, adapters,
   classification, dependencies, size limits, lock location, source/rollback,
   and publication state. Ambiguity blocks enrolment.
4. **Baseline:** read canonical edit-context state, create Git-safe public
   objects and environment locks, preserve remote-owned fields, and refuse
   divergent existing files.
5. **Canary:** rehearse one low-risk object. Snapshot outside Git, re-read,
   dry-run, apply with expected hash/revision and atomic guard, read back, then
   verify editor/rendered behavior and rollback.
6. **Waves:** migrate bounded dependency-ordered units with durable
   checkpoints. Reconcile before resume; never blind-retry unknown writes.
7. **Automate:** WordPress public saves create reviewed bot PRs; approved Git
   merges trigger fresh read/plan/CAS/readback. Autosaves, revisions, private
   content, and bot loops are excluded.
8. **Handoff:** report source, remote, lock, browser, runtime, CI, deployment,
   publication, rollback, and deferred unsupported state independently.

## Command boundary

`validate`, `inventory`, `pull`, `status`, `diff`, `plan`, and
`code-export-plan` are read-only remotely. `baseline`, `wave-plan`, and
`checkpoint` write local task-owned artifacts only. `apply` is a dry run unless
the user authorized the exact environment/object and `--execute` is supplied
with the current lock expectations, `--require-atomic-check`, idempotency key,
and approval identifier.

No command supplies a force overwrite, direct database write, raw WP-CLI
content update, bulk search-replace, protected-branch push, autonomous merge,
deployment, publication, provider mutation, or destructive de-enrolment.

## Stop conditions

Stop before mutation on target mismatch, absent runtime, non-atomic guard,
stale lock, changed Git or WordPress baseline, identity collision, unowned
field, unsupported plugin/builder version, missing dependency, private or
restricted payload, unknown media rights, unavailable verification channel,
missing snapshot/rollback, or unclear authorization.
