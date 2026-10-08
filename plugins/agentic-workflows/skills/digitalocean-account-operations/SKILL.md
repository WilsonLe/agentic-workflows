---
name: digitalocean-account-operations
description: Inspect and manage DigitalOcean through the built-in Codex browser using the active team/account selected for the current project. Use for onboarding, Droplets, networking, DNS, Kubernetes, databases, registries, Spaces, projects, incidents, and recovery; optional read-only doctl logs/status supplement browser operation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: DigitalOcean account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# DigitalOcean Account Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.

Read [onboarding](references/onboarding.md) for first use. Before setup or writes,
apply [task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).

## Core workflow

1. Open the DigitalOcean control panel and verify the signed-in identity.
2. Choose the team/account matching the current project. Resolve project,
   resource, region, and deployment/cluster/database identifiers in the UI.
3. Inspect current state and retain non-secret fields needed for verification
   and recovery. Check actual account permissions, availability, and cost.
4. Follow [change management](references/change-management.md) and execute the
   smallest authorized management change through control-panel UI.
5. Reopen the exact resource, wait for asynchronous actions to finish, compare
   saved state, and verify networking and workload health when applicable.

Inspection and planning authorize reads only. Deletion, rebuild, resize, failover,
migration, exposure, credential changes, and new charges need exact-effect authority.
Do not create a resource, switch CLI context, or rotate credentials to test access.

## Optional doctl diagnostics

Read [troubleshooting](references/troubleshooting.md) for bounded read-only commands.
The protected `<plugin-root>/scripts/digitalocean_cli.py` launcher remains optional;
its authenticated account and resource scope must independently match the browser.
Use existing authorized credentials when available. Missing doctl/token setup
blocks only that diagnostic; it is not required for browser management.
Do not use doctl writes under diagnostic authority. Report missing UI capabilities
and obtain explicit user direction before choosing a non-browser mutation.

## Runbooks and evidence

- [Compute and networking](references/compute-networking.md).
- [Domains and DNS](references/dns.md).
- [Managed services](references/managed-services.md).

Report the browser URL, team/account and exact resource, saved-state readback,
health and cost/availability impact, recovery, and separately identified CLI
results. Never expose tokens, SSH private keys, kubeconfig, registry credentials,
database passwords, raw environments, or unreviewed traces.
