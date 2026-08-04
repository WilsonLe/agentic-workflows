# WordPress project onboarding and state

Use this reference before a project-level plan or any write. Keep the record compact, secret-free,
and timestamped. The repository, WordPress site, vendor/provider, and approved source documents
remain authoritative; this record points to evidence and records what is currently known.

## Read-only readiness

Confirm, in order:

1. project/site name, canonical HTTPS URL, environment, owner, and requested scope;
2. repository/ref/worktree and source-of-truth documents/assets;
3. authenticated REST index and relevant schemas/capabilities;
4. SSH target, WordPress root/Compose project, serving service, and WP-CLI runtime when CLI work
   is needed;
5. core/PHP/database/multisite, site URL/home URL, active theme/child theme/editor/builder, and
   relevant plugins/content types;
6. access to authenticated admin, logged-out public, Chrome/CDP, CI, deployment, and provider
   evidence channels;
7. cache/CDN, maintenance/coming-soon, noindex, consent, backup, cron, and known blocked state.

Do not create a test post, upload media, alter options, activate software, publish, purge cache,
or enable maintenance mode as onboarding.

## Secret-free state fields

Record only identifiers and evidence pointers:

- target: project, environment, canonical URL, owner, and approved fingerprint fields;
- source: repository, branch/ref/SHA, worktree, deployment mechanism, and source-of-truth paths;
- runtime: provider/SSH alias, Compose project/service names, ports, root/path identifiers,
  database identity, table prefix, and multisite URL; never credentials;
- WordPress: versions, editor/theme/builder, content types, URL/permalink constraints, and plugin
  states relevant to the task;
- managed content: object type/ID/key, managed fields, serializer version, publication state, and
  environment-specific lock reference;
- integrations: install/activate/configure/connect/consent/collect state, data flow, owner, and
  rollback reference;
- evidence: available channels, status, timestamp, exact target, limitation, and artifact digest;
- change: approval owner, current lifecycle state, baseline, drift, backup, rollback, and TBDs.

Use `verified`, `observed`, `inferred`, `unknown`, `blocked`, and `not-applicable` labels. An
unknown required identity or capability blocks the dependent operation.

## Target fingerprint

Before remote or production mutation, compare expected and observed canonical URL/environment,
provider/SSH target, Compose project/service, host/container ports, database identity/table prefix,
WordPress site URL/home URL, multisite scope, and source/deployment revision. A reachable host,
healthy container, or successful login is not sufficient target identity.

## State record examples

Validate [project-state-v1.json](../examples/project-state-v1.json) against
[project-state-v1.schema.json](../schemas/project-state-v1.schema.json). Do not copy its example
values into a real project without fresh read-only evidence.
