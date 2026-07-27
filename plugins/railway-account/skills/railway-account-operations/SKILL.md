---
name: railway-account-operations
description: Safely inspect and operate an authorized Railway account through the official Railway CLI using a user-selected account token created with No workspace. Use for Railway onboarding, account and workspace inventory, projects, environments, services, deployments, variables, logs, domains, volumes, scaling, incidents, exact-target approval-gated changes, rollback, and CLI troubleshooting.
---

# Railway Account Operations

Use `railway` as the execution layer. Do not add an MCP server, use browser
automation in place of a supported CLI command, or call the Railway API directly
unless the user explicitly requests API work outside this skill.

For setup, credential selection, or first use, read
[onboarding.md](references/onboarding.md) and
[credential-contract.md](references/credential-contract.md). Accept only an
account token created with **No workspace**. Never ask for its value in chat.

## Core workflow

1. Confirm the installed CLI with `railway --version`.
2. Load the protected account token only through the bundled wrapper.
3. Verify the account read-only with `railway whoami --json`.
4. Resolve the exact workspace, project, environment, and service from
   structured reads; never guess names or IDs.
5. Read [target-resolution.md](references/target-resolution.md) before work that
   depends on a linked directory or explicit target.
6. For a mutation, read
   [change-management.md](references/change-management.md), capture pre-state,
   and present the exact secret-free command, target, impact, verification, and
   rollback.
7. Obtain explicit approval. Obtain separate production approval for a
   production change and destructive approval for deletion, teardown, or
   detach operations.
8. Execute the smallest sufficient command, then read back state and verify the
   affected behavior.

Inspect, diagnose, inventory, explain, and plan requests authorize reads only.
Never treat broad account-token access as broad action authority.

## Helper contract

The plugin root provides:

- `scripts/railway_configure_credentials.py` to install a user-selected account
  token at `~/.config/amsoft/railway/credentials.json`;
- `scripts/railway_cli.py` to run non-interactive Railway commands with only
  `RAILWAY_API_TOKEN` in the child environment.

The launcher requires approval phrases for writes and offers `variable-names`
as the only safe variable inventory. Do not bypass it with
`railway variable list`, which can expose values. Do not use the launcher for
`run`, `shell`, `connect`, `ssh`, or `dev`; those surfaces can expose service
secrets or require an interactive terminal. Use bounded logs only after
acknowledging that application output may contain secrets. The launcher refuses
variable values, template variables, and 2FA codes in command arguments.

## Runbooks

- Read [deployments.md](references/deployments.md) before upload, deploy,
  redeploy, restart, down, scaling, or deployment rollback work.
- Read [variables-and-secrets.md](references/variables-and-secrets.md) before
  inspecting or changing variables.
- Read
  [incidents-and-troubleshooting.md](references/incidents-and-troubleshooting.md)
  for failures, unknown syntax, degraded service, or emergency mitigation.

Use installed command help and current official Railway documentation together.
Help output can itself query Railway or fail in some CLI versions; it is not
proof that authentication or a target operation is healthy.

## Verification

For every completed operation, report the CLI version, resolved targets,
command shape without secrets, approval received, sanitized result, readback,
live verification where applicable, and rollback state. Never include token
material, variable values, raw environments, authorization headers, or
unreviewed logs.
