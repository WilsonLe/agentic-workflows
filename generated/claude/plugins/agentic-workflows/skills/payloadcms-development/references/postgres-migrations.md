# Payload Postgres migrations: generate, review, prove reversal

Payload's Postgres adapter uses Drizzle and may automatically push schema changes in development.
For environments using migrations, keep a committed migration history and do not mix automatic
development push with manual migration commands against the same database.

## Preflight

1. Read the target's Payload, adapter, Node, package-manager, and migration-directory versions.
2. Confirm the exact `PAYLOAD_CONFIG_PATH`/project script and active configuration environment.
3. Confirm that the database is a disposable database dedicated to this verification; print only a
   safe target label, never a connection-string secret.
4. Run `pnpm payload migrate:status` (or the repository's equivalent) and save its non-secret
   status. Resolve unexpected pending migrations before generating a new one.
5. Type-check/lint the changed config and make its environment-specific collection/plugin list
   stable. Generating with a development config that excludes production entities creates drift.

## Interactive generation without losing prompts

Use a meaningful, lowercase migration name, for example:

```bash
pnpm payload migrate:create add-post-owner
```

When controlling this command through an agent terminal, use a short initial wait (about 0.5–2
seconds) to detect output and prompts. A timeout/yield is not a reason to terminate or relaunch the
command: retain its session, inspect emitted text, respond to a displayed prompt once, then keep
polling that session. The common Postgres no-schema-change prompt asks whether to create a blank
migration. If an automatic migration was expected, choose the non-blank/decline path and diagnose
why the config did not produce schema SQL.

For non-interactive jobs, `--skip-empty` makes the no-schema-change case fail/skip without creating
a blank migration. `--force-accept-warning` intentionally accepts prompts and can create a blank
migration; do not use it as a substitute for understanding the generated diff.

If generation exits without an automatic migration, inspect the process result, migration directory,
config path, effective environment, and generated schema. Repeat `migrate:create` only after fixing
the identified cause and verifying no competing process created a file. Do not retry while another
generator is live and do not hand-author an empty file merely to advance CI.

## Review `up` and `down`

Payload migration files export `up` and `down`. Review generated `up` and `down` before applying:

- tables, columns, enums, indexes, constraints, defaults, nullability, and relations match the
  intended collection/global change;
- SQL does not unexpectedly drop, rewrite, lock, or truncate existing data;
- data transformations are bounded, idempotent where reruns are possible, and use the migration
  transaction/request context when calling the Local API;
- `down` actually restores the former compatible schema and data semantics, rather than only
  deleting objects with data loss; and
- large backfills have an explicit deployment/lock plan instead of being casually hidden in startup.

For Postgres direct SQL, use the adapter's documented `db`/`sql` interfaces inside the supplied
transaction. The migration transaction rolls back if the migration errors, but transactional
rollback is not a replacement for a correct `down` implementation.

## Required round trip

Against a disposable database seeded with the minimum representative data:

```bash
pnpm payload migrate
pnpm payload migrate:status
# exercise the changed Local API / HTTP behavior
pnpm payload migrate:down
pnpm payload migrate:status
pnpm payload migrate
pnpm payload migrate:status
```

After the first up, exercise writes and reads that depend on the changed schema. After down, verify
the previous schema/API contract that remains supported by the migration. After the second up,
repeat the changed behavior. Treat `migrate:down` as a database mutation with the same target gate
as `migrate`; never point this sequence at production.

## CI and deployment

CI should apply pending migrations before a production build only when the deployment environment
can safely reach the intended database and one runner owns migration execution. A common script is
`payload migrate && <build>`. Runtime `prodMigrations` can be appropriate for long-running services,
but it still needs serialized startup/deployment ownership and the same reviewed artifacts.

## Official sources

- [Payload migrations](https://payloadcms.com/docs/database/migrations)
- [Payload Postgres adapter](https://payloadcms.com/docs/database/postgres)
