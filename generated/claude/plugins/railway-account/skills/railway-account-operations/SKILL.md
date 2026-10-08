---
name: railway-account-operations
description: Safely inspect and manage Railway through the built-in Codex browser, selecting the active account and exact project, environment, and service. Use for onboarding, workspaces, projects, deployments, variables, domains, volumes, scaling, incidents, and rollback; optional read-only CLI logs and status supplement the browser workflow.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: Railway account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# Railway Account Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.

For first use, read [onboarding](references/onboarding.md). Before setup or writes,
read [task authority and concealed secrets](references/task-authority-and-secrets.md).

## Core workflow

1. Open the Railway dashboard. Verify the signed-in account and choose the
   workspace that matches the current project's repository or domain.
2. Resolve and read back the exact project, environment, service, deployment,
   and domain as applicable. Read [target resolution](references/target-resolution.md).
3. Capture relevant pre-state, impact, authority, verification, and recovery using
   [change management](references/change-management.md).
4. Perform the smallest authorized change through visible dashboard controls.
5. Reopen the affected resource, compare saved settings, observe asynchronous
   deployment status, and verify the real domain or relevant user flow.

Inspection and planning authorize reads only. Reuse authority covering the exact
write, production target, and destructive effect; ask only for unresolved scope.
Do not create a resource or change a link merely to test access.

## Optional CLI diagnostics

Read [incidents and troubleshooting](references/incidents-and-troubleshooting.md)
for bounded logs/status. The protected wrapper at
`<plugin-root>/scripts/railway_cli.py` and
[credential contract](references/credential-contract.md) are optional diagnostic
facilities, not onboarding requirements. Verify its identity and exact workspace,
project, environment, and service against the dashboard before using it.
Do not use CLI management or deployment commands under read-only diagnostic authority.

## Runbooks

- [Deployments](references/deployments.md): create, redeploy, restart, scale, and rollback.
- [Variables and secrets](references/variables-and-secrets.md): names-only inspection and UI changes.
- [Incidents and troubleshooting](references/incidents-and-troubleshooting.md): bounded investigation.

## Verification

Report the browser URL, selected account/workspace and exact target, saved-state
readback, live behavior, and rollback state. Identify any supplemental CLI evidence
separately. Never include token material, variable values, raw environments, or
unreviewed logs. If the UI cannot complete management, report the specific gap;
a CLI write requires explicit user direction for that operation.
