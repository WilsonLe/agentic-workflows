---
name: payloadcms-development
description: Develop Payload CMS applications and reusable Payload plugins. Use for typed Payload config, collections, globals, custom admin or field components, access control, Postgres migrations, payload migrate:create, migration rollback, and unit, integration, or Playwright E2E testing.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Payload project** — Open a Payload project and install its declared development dependencies.

<!-- catalog-prerequisites:end -->

# Payload CMS Development

Use this workflow for Payload CMS projects and libraries. Begin by reading the target project's
Payload version, package-manager scripts, `payload.config` path, database adapter, migrations
directory, authentication collection, role model, existing test commands, and the exact environment
target. Current official Payload documentation and the project's installed types outrank this
workflow when they differ.

Do not run `migrate:down`, `migrate:reset`, `migrate:fresh`, or any migration against a shared,
staging, or production database merely as a test. Resolve a disposable database explicitly before
the reversible migration check. Preserve unrelated repository edits and do not change environment
files, credentials, or deployment settings without the requested authority.

## Choose the smallest appropriate surface

- Use a **Collection** for a set of documents: give it a stable `slug`, explicit `fields`, focused
  `admin` behavior, and operation-specific `access`. Keep collection definitions in separate typed
  files and compose them in `buildConfig`.
- Use a **Global** for a singleton such as navigation, site settings, a banner, or application-wide
  content. It has its own fields, access, hooks, and Admin configuration; it is not a collection
  with an arbitrary one-row convention.
- Use a **custom component** only for an actual Admin UI requirement. Default to React Server
  Components; add `'use client'` only when browser state, events, or hooks require it. Register the
  component by the documented config path and regenerate/import-map-check it when the project
  requires that step.
- Use a **Payload plugin** for reusable config transformation across projects. Give it typed options,
  an enable/disable route, deterministic composition, and a small surface area. Do not mutate a
  caller's arrays or silently replace their access rules.

Read [configuration-and-components.md](references/configuration-and-components.md) before defining
collections, globals, or custom components. Read [access-control.md](references/access-control.md)
before implementing authorization.

## Postgres migration workflow

Payload's Postgres adapter can push schema in development, while relational environments rely on
migrations. Do not mix development `push` behavior with manual migration commands for the same
database. Finish and type-check the configuration change before generation, then read
[postgres-migrations.md](references/postgres-migrations.md) in full.

The required `payload migrate:create` interaction pattern is:

1. Confirm the config path, migration directory, and **disposable** `DATABASE_URL`; run the exact
   project script (commonly `pnpm payload migrate:status`) first and record the target.
2. Start `pnpm payload migrate:create descriptive-change` with a short initial tool wait (roughly
   0.5–2 seconds). This is a prompt probe, not a cancellation: keep the same process/session alive.
3. If output presents a prompt, read it and answer only the displayed question through that same
   session. In particular, do not accept a blank migration when an automatic schema migration was
   expected. In unattended CI, use `--skip-empty` to decline the no-schema-change blank-file prompt.
4. Poll the existing process until it exits. If it completed without an auto-generated migration,
   inspect the config, generated schema, migration directory, and command output. Re-run
   `migrate:create` only as a fresh, named attempt after resolving that cause; never start concurrent generators
   or manufacture duplicate timestamp migrations.
5. Inspect the generated `up` and `down` SQL/TypeScript for constraints, data transforms, lock and
   backfill risk, and meaningful reversal. Commit generated artifacts rather than regenerating them
   in CI.
6. On the disposable database, run `migrate` (up), exercise the affected Local/API behavior, run
   `migrate:down`, then run `migrate` again. Read `migrate:status` after each meaningful transition.
   The final state must be current and the second up must work; report any deliberately irreversible
   data transformation as a blocked rollback design, not a passing migration.

`migrate:create` writes a migration but does not apply it. Passing `migrate` once, generating a file,
or seeing an HTTP 200 does not prove its `down` path or a second `up` path works.

## Worktree Compose test management

Every Payload test run must use Docker Compose and a production application build. Read
[testing.md](references/testing.md) in full before choosing or running a test command. Host-native
package-manager tests, `next dev`, `payload dev`, and a development-container run can be useful for
diagnosis, but are not test completion evidence.

Each worktree owns a separate Compose project: its app container, Postgres container, network,
volumes, fixture data, and Compose project name must be derived from that worktree's stable local
identity. Do not share a database, named volume, container, or Compose project with another
worktree. Use the repository's standard application port (and standard Postgres mapping when it is
published), not arbitrary alternate ports; distinct Compose resources create distinct app and
Postgres instances despite those shared port numbers.

Only one local Payload Compose test stack may run on a host at a time. Before `docker compose up`,
`run`, or any command that starts a test service, acquire the host-wide directory lock at
`${TMPDIR:-/tmp}/payloadcms-compose-test.lock`. `mkdir` is the portable atomic acquisition:
the lock owner records the PID, worktree path, Compose project name, and start time in `owner`.
Hold it through image build, database startup, migrations, tests, logs/artifact collection, and
`docker compose down --volumes --remove-orphans`; release it with a shell trap on normal exit,
failure, or interruption. Never delete a lock solely because it looks old: inspect its recorded
owner and confirm that the PID is no longer live before an explicit, documented stale-lock recovery.
If the lock is held, wait or fail clearly rather than starting a second stack.

Build the application image before starting Postgres or any other runtime dependency. The production
build must succeed with no database connection, database credentials, migration command, seed, or
runtime health check available. Keep database access in runtime startup and test setup, and ensure
the Docker build stage has neither `depends_on` semantics nor a route to the database service. A
successful test stack therefore proves both an independently buildable artifact and its runtime
behavior against that worktree's disposable Postgres instance.

## Three-layer test strategy

Plan each change across all applicable layers; do not use E2E to compensate for missing unit or
integration coverage.

1. **Unit:** pure role predicates, access-query builders, field validation, plugin option merging,
   hooks, and component helpers. No Payload process, HTTP server, database, or browser. Cover allow,
   deny, anonymous, and malformed/edge inputs.
2. **Integration:** boot the actual Payload config against an isolated test database and exercise
   Local API and/or HTTP operations. Verify schema, hooks, access results and query constraints,
   plugin composition, migrations, and custom routes. Use distinct fixture users and clean data for
   every test; test access through the real operation, not only by calling the predicate directly.
3. **Playwright E2E:** start the built application and cover a thin set of critical user journeys in
   the real Admin or public UI: authentication, visible authorization, create/edit/save, custom
   component interaction, and a denied action. Use isolated fixtures, role/text/test-id locators,
   web-first assertions, and traces on retry. Do not expose secrets in storage state, screenshots,
   traces, or reports.

Run each selected layer inside its worktree's locked Compose stack, using the production-built
application image. A feature that adds configuration, authorization, UI, and a schema change should
normally have coverage at all three layers plus the migration round trip.

## Completion evidence

Report the Payload and adapter versions, changed config/plugin surfaces, target database class,
generated migration file names and reviewed risks, exact up/down/up results, Compose project and
worktree identity, lock acquisition/release outcome, production-build-without-database result, test
commands and layer coverage, and any production or deployment action deliberately not taken. Never
state that a migration, access rule, or custom component is production-safe without target-specific
verification.
