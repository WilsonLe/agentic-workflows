# Installation, configuration, and verification

## Select the delivery path

For a repository-managed stack, use `standard-development-workflow`: pin the reviewed Stream
version/source in the existing application contract, add deterministic configuration and tests,
prove it locally or on staging, open a draft PR, and keep production separately approved.

For a directly managed site, use `wordpress-cli-operations` with the discovered adapter. Prefer a
staging rehearsal for production-bound plugin/database changes. Immediately before a production
write, re-read the target and current state, verify the recoverable backup, preview impact and
rollback, and obtain fresh confirmation.

## Installation and configuration

1. Refresh the stable release, compatibility, security, scheduler, integration, and uninstall
   behavior from primary upstream sources.
2. Inspect the current plugin source/version/status, Stream options, tables, and records before
   changing anything.
3. Use the repository's existing manifest/deployment path or the target's installed WP-CLI help.
   Prefer the WordPress.org package and checksum verification where supported.
4. Use serialization-aware WordPress interfaces. Change only policy-owned keys and preserve
   unrelated settings. Stop on an unexpected option shape.
5. Verify version, activation, database/schema state, owned settings, access roles, exclusions,
   integrations, automatic purge, and the selected scheduler.
6. Apply configuration twice where safe and confirm the second run does not broaden or reset state.

Do not use raw SQL for ordinary configuration. Do not reset, truncate, export, delete, or replace
existing records. Do not silently enable broader access, indefinite retention, exclusions,
outbound alerts, exports, Abilities API, MCP Adapter, or AI queries.

## End-to-end proof

Plugin activation is insufficient. On local or staging:

1. Create a unique, non-sensitive fixture identifier.
2. Record the current value or absence of a benign WordPress option or equivalent reversible state.
3. Apply the synthetic change through the normal WordPress/WP-CLI path.
4. Query Stream for the exact connector/context/action and fixture identifier.
5. Assert the matching event exists without printing unrelated records.
6. Restore or delete the fixture in guaranteed cleanup.
7. Verify cleanup and, where expected, the restoration event.
8. Recheck settings, tables/schema, scheduler, checksum/source, Site Health, and relevant PHP,
   database, web-server, container, and scheduler logs.
9. Confirm the matching record and policy in the real wp-admin UI.
10. Verify changed privacy content at the actual draft or public URL.

Production synthetic events require separate scope. If they are not approved, report that the
production verification is structural/read-only rather than claiming end-to-end production proof.

## Failure paths

- Missing tables or events: preserve state and inspect plugin bootstrap, exclusions, connectors,
  database/schema state, Site Health, and logs.
- Missing purge schedule: fail bounded-retention verification and inspect Action Scheduler or the
  supported WP-Cron fallback.
- Source/version/checksum mismatch: stop before installation or upgrade.
- Unexpected settings: report the non-sensitive difference and stop before replacement.
- UI unavailable: treat CLI/API results as partial evidence, not administrator-facing proof.
