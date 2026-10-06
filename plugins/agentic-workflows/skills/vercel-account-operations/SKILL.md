---
name: vercel-account-operations
description: Set up Vercel agent tooling and inspect or manage authorized Vercel accounts, teams, members, access, projects, domains, integrations, spend settings, and deployments using the official CLI and shared MCP. Use for Vercel onboarding and account administration; use the official Vercel guidance plugin for framework and application implementation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Vercel CLI and account** — Follow the live Vercel agent setup playbook; install the official CLI and authenticate the intended account.
- **Optional: Vercel guidance and MCP** — Reuse or install the official Vercel guidance plugin and authenticate the shared MCP endpoint when the task needs it.

<!-- catalog-prerequisites:end -->

# Vercel Account Operations

Read [onboarding](references/onboarding.md) for setup or authentication and
[account management](references/account-management.md) for account, team, or
project operations. Before provider setup, credentials, or writes, read
[task authority and concealed secrets](references/task-authority-and-secrets.md).
For deploys, environment variables, incidents, or recovery, read
[deployment operations](references/deployment-operations.md).

Use the installed CLI's help and current official documentation to resolve
syntax and capabilities. Prefer the official Vercel plugin's guidance when
available; this skill supplies the suite's account operations workflow.
Do not assume that installing guidance also connects or authenticates tools.

## Working sequence

1. Verify `vercel --version` and `vercel whoami`. Verify MCP independently with
   documentation search and authenticated `list_teams` when MCP is needed.
2. Inventory teams with `vercel teams list --format json` or MCP. Resolve the
   exact account, team ID and slug, project ID, and environment from reads.
   Paginate before claiming a complete inventory. If CLI and MCP expose
   different identities or teams, reconcile the account choice before writes.
3. Prefer an explicit `--scope <team-slug>` over changing the user's global
   team context. Check `.vercel/project.json` (or repository links) only for a
   task that requires a linked project. Stop an implicit auto-link when the
   current directory or team is unresolved.
4. For writes, capture pre-state, the exact target, effect, task authority,
   readback method, and rollback or recovery. Reuse the user's request for
   necessary in-scope CLI and dashboard steps. Inspect and plan requests
   authorize reads only; access to an account does not authorize all actions.
5. Keep human confirmation enabled for every MCP mutation, as required by
   Vercel's setup playbook. Do not disable host approval controls or use a
   different execution route to bypass an enforced confirmation.
6. Execute the smallest authorized operation, read back the saved state,
   verify the requested behavior, and report any remaining recovery limitations.

Global agent setup must not create or link projects. Account cancellation,
team deletion, project transfers, member removal, new charges, and production
deployments need task authority covering the exact target and effect. Ask only
when this is missing; retain separate repository merge and deployment gates.

## Evidence

Report CLI version and username, connection route and scope, independently
verified MCP account/team, resolved targets, sanitized results, and live
readback. Distinguish configured, authenticated, tool-discoverable, and
operation-verified states. A successful CLI login does not prove MCP health.
Never report a write or deployment as complete from an acknowledgement alone.
Keep credential values, environment values, billing details, personal member
data, unreviewed logs, and authorization URLs with secrets out of reports.
