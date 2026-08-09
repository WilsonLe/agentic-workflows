# Provider and runtime variants

Discover the real adapter; examples are not target commands.

## Docker Compose

Resolve the Compose project, serving WordPress/PHP service, database service,
volumes, UID/GID, WordPress root, health, and versioned Compose/deployment
source. Use the documented `docker compose exec -T` WP-CLI/runtime path and a
worktree-isolated disposable database/volume for rehearsal. Never reuse or
delete a canonical volume.

## Bare-metal or VM

Resolve the SSH alias/account, WordPress root, PHP user, web server, database,
WP-CLI binary, backups, and Git/deployment source. Use exact `--path` and
multisite `--url`; do not run as root merely because it succeeds.

## Managed WordPress

Use only documented provider deployment, backup/restore, SSH/WP-CLI, plugin,
and staging capabilities. If the runtime cannot be installed or database
transactions/REST routes are blocked, inventory/diff planning may continue but
strict writes remain blocked. Do not substitute a provider console, direct DB
tool, or broad migration plugin and claim contract parity.

For every variant, installation/deployment, content apply, staging,
production, publication, rollback, and provider mutation retain separate
approvals and evidence.
