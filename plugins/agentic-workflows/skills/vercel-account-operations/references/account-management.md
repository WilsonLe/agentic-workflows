# Account and team management

Use the [CLI-token contract](../../agentic-workflows/references/service-browser-operations.md).
Inspect `vercel --version` and exact subcommand help. Obtain `VERCEL_TOKEN` from
Infisical, verify identity and intended team/project IDs through CLI reads, and
use explicit supported scope selectors. Complete pagination; do not select the
first matching name. Summarize only required roles, limits and resource metadata.

For authorized membership, role, transfer, domain, integration or billing changes,
verify actual CLI command coverage and permissions. Capture prior state, destination,
access/cost effects and recovery. Retain a usable owner path for transfers/removals.
Invitations and other communications need explicit communication authority.

Execute the smallest supported CLI operation and read back state/effective access.
Absent commands and denied permissions remain blockers without connector, REST or
dashboard fallback. State when a change has no automatic rollback.
