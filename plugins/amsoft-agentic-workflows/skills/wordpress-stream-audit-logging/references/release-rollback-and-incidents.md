# Release, rollback, and incidents

## Release

For repository-managed sites, release only the reviewed merged revision through the documented
deployment path. Require separate staging and production approvals. For direct production
operations, re-resolve the exact target, capture pre-change state, verify a current database and
required file/hosting backup, state impact and rollback, and obtain fresh confirmation.

After a write, verify the exact active version, settings, tables/schema, purge scheduler, health,
logs, filtered event behavior where approved, administrator UI, and privacy surface. Capture a
post-change backup when the site's release policy requires it.

## Rollback

Rollback should restore the reviewed application/configuration state and, when necessary, the
verified pre-change database and `wp-content`/hosting snapshot. Deactivate Stream only when safe
and justified. Recheck administrator access, public response, application health, scheduler, and
logs after recovery.

Do not use uninstall, database reset, table truncation, record deletion, or a full-option
replacement as routine rollback. Upstream currently documents uninstall-time data-removal
caveats; refresh that status before any destructive data-removal proposal and require separate
explicit authorization.

## Incidents

For missing records, failed purging, table growth, unexpected access, or possible disclosure:

1. Stop nonessential changes and preserve evidence without exporting broad record sets.
2. Confirm target, time window, Stream/source version, policy, scheduler, tables, roles, exclusions,
   integrations, proxy boundary, and relevant logs.
3. Restrict evidence to the minimum affected synthetic or authorized records.
4. Revoke or narrow unintended access through the site's supported capability path only after
   impact and rollback are clear.
5. Do not delete records to conceal or simplify the incident.
6. Record observed facts, unknowns, containment, recovery, and follow-up without exposing personal
   data or credentials.
