---
name: amsoft-wordpress-devops-management
description: Operate authorized WordPress hosting, runtime, plugin and theme lifecycle, filesystem access, deployment, and rollback through Railway or DigitalOcean with SSH while keeping user-facing content separate.
---

# WordPress DevOps Management

Use this skill only for the WordPress infrastructure and runtime surface. It
owns Railway or DigitalOcean target resolution, authorized SSH, WP-CLI
runtime discovery, hosting and deployment configuration, plugin and theme
lifecycle, filesystem ownership/update failures, PHP/runtime configuration,
database/cache/cron operations, health, recovery, and rollback.

It does not own pages, posts, blocks, images, media, videos, or user-facing
design-system values. Route those concerns to `amsoft-wordpress-content-management`.
For a mixed request, load both skills and keep their contracts, approvals,
change records, and verification separate.

When WordPress Git Sync is selected, DevOps owns versioned installation,
upgrade, compatibility checks, backup, deployment, health, and rollback for
the AMSoft server runtime. `amsoft-wordpress-git-sync-management` owns registry and
CAS semantics; DevOps must not use raw WP-CLI or database updates to bypass
them.

## Authentication and target contract

Read [onboarding.md](references/onboarding.md) and
[target-and-ssh-contract.md](references/target-and-ssh-contract.md) first.
Require:

- exactly one provider target: Railway or DigitalOcean;
- provider access through the dedicated Railway or DigitalOcean account
  workflow, without placing a token in chat; and
- an existing authorized SSH agent, host alias, or equivalent secret-manager
  access path to the WordPress runtime.

Provider access resolves the exact project/service/environment/volume or
Droplet. It does not substitute for SSH. SSH access does not authorize a
provider mutation. Record only secret-free target and credential references in
the reusable and project-specific contracts.

## Read-only discovery

1. Confirm the intended project, site, environment, provider, and requested
   DevOps surface. Never guess a production host, project, service, or path.
2. Verify the provider identity read-only with the installed account workflow.
3. Test the existing SSH path without changing the host. Resolve the host,
   account, runtime adapter, and environment.
4. Discover bare-metal or Docker Compose topology, WordPress root, PHP/PHP-FPM
   user, WP-CLI location, site URL, WordPress version, active theme and plugin
   inventory, mounts, owner/mode state, and deployment/source-of-truth
   relationship.
5. For filesystem/update prompts, run the same-user ownership and write probe
   and `get_filesystem_method()` check described in
   [filesystem-and-plugin-management.md](references/filesystem-and-plugin-management.md).
6. Report `Ready`, `Needs input`, `Needs configuration`, or `Blocked` with the
   exact next safe action.

Do not install, update, activate, deactivate, delete, back up, purge caches,
enable maintenance mode, change ownership, or deploy as an onboarding test.

## Infrastructure-as-code and commit boundary

DevOps changes are infrastructure changes. Every durable infrastructure-as-code
mutation must be represented in versioned source and committed. Before a mutation, identify the
versioned source of truth: Dockerfile/Compose, entrypoint, Terraform or
provider configuration, deployment manifest, plugin/theme package, or the
repository's documented release adapter. Then:

1. inspect the exact revision, branch, dirty state, and relevant checks;
2. model the intended change and rollback in source;
3. validate the source and any generated artifacts;
4. obtain the approval required for the target environment;
5. deploy or execute the smallest supported release operation;
6. read back provider, SSH/runtime, filesystem, plugin/theme, and health state;
7. commit the reviewed infrastructure/deployment change with its evidence.

Do not call a direct `wp plugin update`, `chown`, provider shell, cache purge,
or manual file edit a complete DevOps fix when the source-of-truth change and
commit are absent. A user-authorized emergency repair may be a temporary
recovery action, but it must be recorded as drift, reconciled into source, and
reverified before completion. Never use the WordPress built-in Plugin/Theme
File Editor, `0777`, a guessed provider shell, or an unbounded command.

## Operational surfaces

- **Hosting/provider:** resolve exact Railway or DigitalOcean resources,
  volumes, domains, variables, deployment identity, and rollback revision.
  Keep account-token and production approvals distinct.
- **SSH/WP-CLI:** use the target installation's own runtime; identify whether
  WP-CLI runs on the host, through `docker compose exec -T`, or through
  `docker exec`. Use exact `--path` and multisite `--url` values.
- **Plugins and themes:** inspect compatibility, source, current versions,
  activation, dependencies, filesystem context, backup, and rollback. Model
  desired state in the deployment source before installation/update/activation.
- **Filesystem:** diagnose PHP UID/GID, owners, modes, mounts, writable paths,
  and `get_filesystem_method()` as the serving user. Align only the exact
  writable path through the reviewed deployment mechanism; never collect FTP
  credentials or force `FS_METHOD=direct` over a failed write probe.
- **Runtime/data:** keep database, cache, cron, PHP, maintenance, and recovery
  changes bounded, backed up when material, and separately verified.

Do not edit page/post content or media as a shortcut for a runtime change. If
the desired result is user-facing content, hand it to Content.

## Approval boundaries

Require fresh confirmation immediately before production hosting/provider
mutations, deployment, plugin/theme install/update/activation/deactivation or
deletion, database changes, filesystem ownership/mode changes, cache purges,
maintenance mode, user/role changes, destructive recovery, or any command
broader than the approved envelope. An inspect, diagnose, review, or plan
request authorizes no mutation.

## Verification

Verify each layer independently:

- provider target and deployed revision;
- SSH host/account and runtime adapter;
- WordPress/PHP/core/plugin/theme versions and status;
- filesystem owner/mode, same-user write probe, and `direct` method where
  updates require it;
- database/cache/cron or health state affected by the change;
- logged-out public health and critical journeys; and
- repository source, generated artifacts, commit identity, and rollback path.

WP-CLI exit code, provider health, HTTP 200, root-only filesystem access,
admin UI, or a commit alone does not prove the other layers. Report any
remaining cache, CDN, indexing, deployment, or source drift explicitly.

Read [routing-and-boundaries.md](references/routing-and-boundaries.md) when a
request may need the Content plugin.
