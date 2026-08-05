---
name: wordpress-cli-operations
description: Safely inspect, maintain, troubleshoot, migrate, and update WordPress installations over SSH with WP-CLI on bare-metal or Docker Compose hosts. Use for WordPress server onboarding, runtime discovery, filesystem ownership and FTP-credential update prompts, backups, database and cache work, core/plugin/theme operations, users and roles, cron, search-replace, multisite, maintenance mode, diagnostics, deployment verification, and rollback planning when the user has authorized SSH access to a host where WP-CLI is available.
---

# WordPress CLI Operations

Use SSH and the target installation's own WP-CLI runtime. Support bare-metal installations and
containerized WordPress services without assuming paths, service names, users, shells, or topology.
For wp-admin FTP prompts or `Could not access filesystem`, read
[references/filesystem-and-updates.md](references/filesystem-and-updates.md) before proposing a
filesystem or configuration change. The durable fix is normally to align the PHP runtime user
with the writable WordPress volume, not to collect FTP credentials or force a constant blindly.

For setup or first use, read [references/onboarding.md](references/onboarding.md). Never ask the
user to paste private keys, passwords, database credentials, salts, or tokens into chat. Use an
existing SSH agent, host alias, or secret manager.

## Core workflow

1. Confirm the authorized host, environment, site, and intended scope. Distinguish production,
   staging, and local systems.
2. Resolve the SSH target from user-provided context or existing SSH configuration. Never guess a
   hostname or account.
3. Discover the runtime read-only:
   - identify the WordPress root or Compose project;
   - determine whether WP-CLI runs on the host, through `docker compose exec -T`, or through
     `docker exec`;
   - identify the PHP version, WordPress version, site URL, multisite state, active theme, and
     active plugins needed for the task.
   - when updates or filesystem access are in scope, identify the PHP/Apache UID/GID, WordPress
     root and update context owners/modes, writable/read-only mounts, and the result of
     `get_filesystem_method()` executed as the serving PHP user.
4. Select one execution adapter and reuse it consistently. Read
   [references/runtime-patterns.md](references/runtime-patterns.md).
5. Inspect current state and capture the fields needed for rollback.
6. For a consequential change, prepare a current database backup and any required file or hosting
   snapshot. Store database exports outside the public web root and record their location without
   exposing contents.
7. Explain the exact target, impact, validation, and rollback. A direct request to make a scoped,
   reversible content or configuration change authorizes that change. Obtain fresh confirmation
   before destructive, irreversible, security-sensitive, or broad production actions.
8. Execute the smallest sufficient WP-CLI command.
9. Read the state back through WP-CLI, then verify the public or administrative behavior that the
   change was meant to affect.
10. Report evidence, backup or rollback information, and any remaining cache or deployment delay.

An inspect, diagnose, review, inventory, explain, or plan request never authorizes a mutation.

## Safety boundaries

Require explicit confirmation immediately before:

- database import, reset, optimization that rewrites tables, or broad `search-replace`;
- core, plugin, or theme installation, update, downgrade, activation, deactivation, or deletion on
  production;
- user creation/deletion, password changes, role or capability changes, and session invalidation;
- multisite topology changes, domain/path changes, permalink changes, or edits to `home`/`siteurl`;
- file deletion, permission or ownership changes, maintenance-mode activation, or cache purges with
  material traffic impact;
- commands using `--all`, unbounded IDs, or targets discovered by a wildcard;
- any action without a credible backup or rollback when failure could make the site unavailable.

Never run `wp db reset`, `wp site empty`, bulk deletes, or a database-wide replacement as a
diagnostic. Use `--dry-run` where supported. Do not add `--allow-root` by default; use it only when
the discovered container runtime requires it and explain why. Do not edit WordPress core files.
Do not treat `FS_METHOD=direct` as a substitute for a same-user write probe. Never use `0777` or
ask for FTP credentials when the target is expected to support direct writes.

## Command discipline

- Start with `wp --info` and command-specific `wp help`; installed WP-CLI help is the
  command-specific source of truth.
- Use `--path=<wordpress-root>` when the working directory is ambiguous.
- On multisite, require the exact `--url=<site-url>` for site-scoped operations.
- Prefer machine-readable output such as `--format=json` for inventory and verification.
- Quote remote paths and values for the remote shell. Never interpolate untrusted content into a
  shell command.
- Use `--skip-plugins` or `--skip-themes` only for controlled diagnosis; they change bootstrap
  behavior and are not proof that the normal site works.
- Never print `wp-config.php`, environment dumps, database URLs, salts, tokens, private keys, or
  full user records.
- Do not install WP-CLI, Docker, PHP, system packages, or SSH keys without user approval.

## Operational runbooks

Read [references/change-runbooks.md](references/change-runbooks.md) before performing updates,
database work, search-replace, user/role changes, or recovery.
For filesystem/update prompts, also read
[references/filesystem-and-updates.md](references/filesystem-and-updates.md) and classify the
problem before changing ownership, modes, `FS_METHOD`, the image, or an entrypoint.

Prefer a staging rehearsal for core, PHP, theme, plugin, database, or domain migrations. Check
compatibility and available disk space before backup or update work. Keep maintenance windows
short and always include the command that disables maintenance mode in the recovery plan.

## Verification

WP-CLI success is necessary but not sufficient. Verify at the layer the user cares about:

- re-read versions, status, options, or records with WP-CLI;
- for filesystem work, re-run the ownership/write probe as the serving PHP UID/GID and require
  `get_filesystem_method()` to return `direct` for every required update context;
- check the intended URL while logged out and, when relevant, as an administrator;
- inspect browser rendering for page, theme, menu, block, CSS, JavaScript, or responsive changes;
- test critical forms, navigation, authentication, and language variants affected by the change;
- account for page cache, object cache, CDN cache, and PHP opcode cache without purging unrelated
  layers;
- capture visible desktop and mobile proof for visual production work.

Never call a deployment complete from an exit code alone.
