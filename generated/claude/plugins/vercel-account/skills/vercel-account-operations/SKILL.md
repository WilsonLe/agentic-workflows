---
name: vercel-account-operations
description: Inspect and manage Vercel accounts, teams, projects, access, domains, integrations, spend settings, and deployments through the built-in Codex browser using the account selected for the current project. Optional read-only CLI logs and status supplement the browser; use application guidance separately for framework implementation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: Vercel account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# Vercel Account Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.

Read [onboarding](references/onboarding.md) for authentication and
[account management](references/account-management.md) for teams, access, projects,
and billing. Before setup or writes, apply
[task authority and concealed secrets](references/task-authority-and-secrets.md).
For deployments, variables, incidents, or rollback, read
[deployment operations](references/deployment-operations.md).

## Working sequence

1. Open the Vercel dashboard and verify the signed-in identity.
2. Select the team/account matching the project's repository and domain. Resolve
   the exact project, environment, deployment, and URL from the visible UI.
3. Read the current settings and capture the intended change, permissions,
   cost/access/traffic impact, verification, and recovery.
4. Execute management, create/update/delete, deployment, and configuration actions
   through supported dashboard controls using existing task authority.
5. Reopen the settings or deployment; compare saved state and verify the relevant
   live behavior. A queued deployment or success toast alone is insufficient.

Onboarding does not create projects, link directories, deploy, modify membership,
or change billing. Cancellation, transfers, deletion, new charges, and production
need authority covering the exact effect. A browser capability gap is a blocker
for that step, not permission to switch to CLI, REST, or MCP writes.

## Optional CLI diagnostics

Existing authorized CLI access can supply bounded logs/status after `vercel whoami`
and read-only team/project inventory independently match the dashboard context.
Use explicit scope and exact targets, inspecting installed help for read-only
syntax. Do not auto-link a directory or change global team context. Avoid decrypted
variable output and auth files. Missing CLI access does not block browser work.
The official Vercel guidance plugin may inform application implementation;
installation, CLI login, and MCP setup are not prerequisites for this workflow.

## Evidence

Report the browser URL, selected account/team and project/environment, saved-state
readback, relevant deployment revision/URL and health, recovery state, and any
supplemental diagnostic channel. Keep credentials, environment values, personal
member data, billing details, and unreviewed logs out of reports.
