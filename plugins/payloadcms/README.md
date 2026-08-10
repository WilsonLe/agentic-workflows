# Payload CMS

AMSoft's Payload CMS development plugin supports projects using Payload's typed configuration,
including reusable Payload plugins and PostgreSQL-backed applications.

It covers:

- collections and globals that make ownership, fields, and API/admin behavior explicit;
- server-first custom Admin components with a deliberate client-component boundary;
- operation-specific, least-privilege collection, global, and field access control;
- reusable plugins that transform a Payload config predictably; and
- generated Postgres migrations that are reviewed and verified in both directions, plus unit,
  integration, and Playwright E2E coverage.

The workflow is project-scoped. It does not invent a Payload version, database URL, package manager,
authentication model, user role, production target, or browser test environment. It never runs a
destructive migration command against production merely to prove a migration works.

For a PostgreSQL schema change, the required verification is `migrate` (up), `migrate:down`, then
`migrate` again against a disposable database, followed by a migration-status readback. Generated
SQL is reviewed before it is applied; a migration file existing is not proof that it is safe or
reversible.

Start a new Codex task after installing or updating this plugin so the new skill is discoverable.
