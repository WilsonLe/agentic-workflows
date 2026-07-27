# WordPress CLI change runbooks

## Updates

1. Inventory current WordPress, PHP, database, theme, and plugin versions.
2. Check plugin/theme compatibility, release notes, disk space, backups, and rollback.
3. Rehearse on staging when the change can affect rendering, schema, checkout, forms, or login.
4. Back up the database and changed files or take a hosting snapshot.
5. Update one risk group at a time. Do not combine core, PHP, theme, and every plugin into one
   opaque operation.
6. Run required database upgrades only for the component that needs them.
7. Verify versions, logs, front end, administrator access, cron, forms, and critical business flow.
8. Roll back promptly when the acceptance checks fail.

## Database export and import

- Store exports outside the web root with restrictive permissions.
- Confirm available disk space and database size before export.
- Record table prefix and multisite state.
- Treat imports as destructive: confirm the target database, take a fresh pre-import backup, and
  prevent traffic or writes when consistency requires it.
- Verify URLs, serialization-sensitive data, users, and critical records after import.

## Search and replace

- Require exact old and new values and exact site/network scope.
- Run a dry run first.
- Use WP-CLI's serialization-aware command rather than raw SQL for WordPress option/meta content.
- Exclude GUID replacement unless the user provides a specific justified requirement.
- Back up first, execute once, and verify representative options, posts, menus, and media URLs.

## Users and roles

- Resolve the exact user by ID and login.
- Minimize displayed personal data.
- Require confirmation for password, email, role, capability, deletion, reassignment, or session
  changes.
- Never send a password in chat or command history. Prefer a secure reset flow or concealed input.
- Re-read the user's role and test the intended authorization boundary.

## Recovery

- Identify whether failure is WordPress bootstrap, PHP, database, web server, container, cache, or
  network related before changing state.
- Capture narrow, redacted logs.
- For a suspected plugin/theme failure, prefer a staging reproduction. If production recovery
  requires deactivation, change only the identified component and preserve the prior state.
- Include maintenance-mode disablement, cache recovery, backup restore, and service restart steps
  appropriate to the discovered runtime.
