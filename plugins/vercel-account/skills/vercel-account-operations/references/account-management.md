# Account and team management

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

Resolve identity and permissions before any account change. The browser session and CLI can have separate authorizations. Team inventories
that differ require reconciliation, not an automatic login replacement or
selection of the first team. Read the intended identity independently through
the route that will perform the operation.

## Read-only inventory

Every command below includes the file-backend settings and project `--global-config` option from
[onboarding](onboarding.md#project-credential-location); abbreviated examples omit it for readability.

Start with `vercel whoami` and `vercel teams list --format json`. The CLI marks
its current team; an explicit `--scope <team-slug>` avoids altering that default.
Use `vercel project ls --scope <team-slug>` for project inventory and
`vercel project inspect <project-name> --scope <team-slug>` for detail after
confirming syntax with help. Use the authenticated CLI with explicit team scope and pagination. A partial page is a partial inventory.

For membership, roles, access groups, integrations, domain ownership, billing,
or spend information, use currently supported authenticated CLI reads or documented REST
operations through `vercel api`. Discover with `vercel api ls` and `vercel api --help`; GET is the
default, but set `--method GET` explicitly for an account read. Prefer summaries
of roles, resource counts, limits, and spend controls over personal or financial
detail. Confirm entitlements before assuming a feature is available.

## Account writes

Examples include inviting or removing members, changing roles, transferring
projects, adjusting spend controls, managing domains, and changing integrations.
Consult current official docs for the exact operation and required role. Check the CLI, including documented `vercel api` support. If the authenticated
CLI lacks the exact operation, record that capability gap and use an authorized
dashboard flow on the same verified account/target. Do not invent a `vercel billing` command or endpoint.

Before execution, bind the request to the account, team, target resource, desired
state, permissions, cost or access impact, and recovery. Preview changes to
member roles and transfers; confirm the destination and retain a usable owner
or administrator path. Resolve a new charge, cancellation, or destructive
effect not covered by the request before acting. Do not send invitation emails
or other messages unless the user explicitly requested that communication.

For a CLI API write use the exact documented method and a request body from an
owner-only local file outside Git when it contains sensitive data. Inspect
command output before running anything that can return credentials or values.
Preserve any enforced host/provider confirmation; channel changes cannot bypass it.
Capture previous settings, execute one bounded change, and read back the new
state and effective permissions. State when a transfer, removal, or cancellation
has no automatic rollback; define recovery before executing it.

## Sources

- [CLI teams](https://vercel.com/docs/cli/teams)
- [CLI project](https://vercel.com/docs/cli/project)
- [CLI API](https://vercel.com/docs/cli/api)
- [REST API](https://vercel.com/docs/rest-api)
- [Identity and access](https://vercel.com/docs/rbac)
- [Spend management](https://vercel.com/docs/spend-management)
