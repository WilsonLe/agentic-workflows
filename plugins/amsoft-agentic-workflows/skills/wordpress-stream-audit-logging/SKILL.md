---
name: wordpress-stream-audit-logging
description: Inspect, plan, configure, verify, troubleshoot, and recover optional XWP Stream activity and audit logging for authorized WordPress sites. Use for Stream installation or upgrades, audit-log policy, retention, roles, exclusions, scheduler or table health, missing records, privacy disclosure, safe evidence, and repository-managed or direct-site rollout.
---

# WordPress Stream Audit Logging

Treat Stream as an optional application layer. Never install it, activate collection, or change a
site merely because this skill is loaded.

For first use, read [onboarding.md](references/onboarding.md). Before proposing or changing policy,
read [policy-and-data-handling.md](references/policy-and-data-handling.md). Before installation,
configuration, or diagnosis, read
[installation-configuration-verification.md](references/installation-configuration-verification.md).
For production, rollback, or incidents, also read
[release-rollback-and-incidents.md](references/release-rollback-and-incidents.md). Refresh
version-sensitive claims from [research-basis.md](references/research-basis.md).

## Compose the WordPress layers

- Use `wordpress-cli-operations` for SSH/runtime discovery, plugin lifecycle, WP-CLI, database
  tables, cron/schedulers, backups, health, and recovery.
- Use `wordpress-site-management` for Stream's wp-admin records/settings, role-visible behavior,
  privacy content, and public/admin browser verification.
- Use `standard-development-workflow` when a versioned WordPress repository should deliver the
  change. Keep issue, plan, PR, merge, staging, and production approvals distinct.
- Compose `amsoft-wordpress-git-sync-management` when managed-object runtime
  events or applies are in scope. Stream may provide sanitized audit evidence,
  but audit records and actor details never enter Git sync payloads or logs.

Load only the layers required by the request. An inspect, diagnose, review, explain, or plan request
does not authorize mutation.

## Core workflow

1. Resolve the exact site, environment, authorization, canonical URL, runtime adapter, WordPress
   and PHP versions, multisite status, current Stream state, backup path, trusted proxy boundary,
   privacy owner, and available verification channels.
2. Inspect the installed Stream source/version, status, options, tables, access roles, exclusions,
   integrations, retention, record volume, scheduler backend, and warnings without displaying
   records or secrets.
3. Present an explicit site policy covering purpose, retention, access, exclusions, integrations,
   data location/backups, request-IP authority, multisite behavior, privacy, ownership, and
   rollback. Keep unresolved material choices visible and stop before mutation.
4. For a change, prefer staging, preserve exact pre-change state, prepare a recoverable backup,
   preview the target and impact, and obtain the confirmation required by the selected WordPress
   layer.
5. Use the site's supported manifest, deployment, WordPress, and WP-CLI interfaces. Preserve
   records and unrelated settings. Stop on unexpected option shapes, wrong targets, missing
   backups, or version/source mismatches.
6. Verify the exact version/source, settings, tables/schema, purge scheduler, health/logs, and a
   narrowly filtered reversible audit event. Confirm the intended records/settings in the real
   administrator UI and verify changed privacy content at its real surface.
7. Report sanitized evidence, target, policy, verification channels, backup/rollback state, and
   limitations. Never equate activation with working audit coverage.

## Default proposal, not a universal default

When the owner has not selected a policy, offer 90-day live retention, administrator-only access,
no exclusions, automatic purge, no outbound integrations, and no AI/MCP access as a conservative
starting proposal. Require explicit acceptance or replacement; do not silently apply it or claim
that it satisfies every organization or jurisdiction.

## Safety boundaries

- Treat audit records as potentially sensitive operational and personal data. Use synthetic,
  narrowly filtered evidence; exclude unrelated users, IPs, emails, customer data, sessions,
  exports, database rows, and credentials.
- Never trust raw `HTTP_*` forwarded headers for client IP. Require the server or trusted proxy
  boundary to establish a validated `REMOTE_ADDR`.
- Never use raw SQL for ordinary configuration, replace an entire unknown serialized option,
  reset/truncate records, or treat uninstall/data deletion as routine rollback.
- Keep email, webhook, Slack, IFTTT, external shipping, exports, WordPress Abilities API, MCP
  Adapter, and AI access disabled or unchanged unless separately requested, scoped, and verified.
- Do not claim Stream is immutable off-host logging, a SIEM, a backup, intrusion prevention, or a
  complete record of unsupported plugin behavior.
- Require fresh confirmation immediately before production plugin installation, activation,
  update/downgrade, settings mutation, or broad role/capability changes.
