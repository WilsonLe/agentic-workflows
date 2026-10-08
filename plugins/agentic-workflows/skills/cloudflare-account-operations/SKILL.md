---
name: cloudflare-account-operations
description: Inspect and manage Cloudflare through the built-in Codex browser using the active account selected for the current project. Use for onboarding, zones, DNS, Workers, Pages, KV, D1, R2, WAF, rules, incidents, and recovery; optional read-only CLI/helper diagnostics supplement browser operation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: Cloudflare account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# Cloudflare Account Operations

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

1. Open the Cloudflare dashboard and verify the signed-in account.
2. Select the account matching the project's domain/repository. Resolve the exact
   zone, hostname, Worker/Pages project, storage/database, rule, and environment
   as required. Never select a zone by a matching name alone.
3. Inspect current configuration and capture relevant non-secret pre-state.
4. Follow [change management](references/change-management.md); preview the effect,
   traffic/security/data impact, task authority, readback, and rollback.
5. Create, update, delete, configure, deploy, or roll back through dashboard controls.
6. Reopen the resource and compare saved state; verify DNS/route/application
   behavior separately when relevant.

Inspection and planning authorize reads only. Nameservers, DNSSEC, SSL/TLS, WAF,
access policies, routing, broad cache purge, deletion, and production effects need
exact-target authority. Do not change a resource or generate a token to test access.

## Optional diagnostics

[Diagnostic patterns](references/api-patterns.md) covers protected read-only helper
or CLI use, including sanitized errors and bounded inventory. Independently match
its account/resource scope to the dashboard before any supplemental read. Do not
use curl, Wrangler, API helpers, or MCP to perform a management write by default.
Missing UI support requires a concrete limitation and explicit user direction
before a non-browser mutation.

## Runbooks and evidence

- [DNS](references/dns.md): records, proxy state, DNSSEC, and propagation.
- [Workers](references/workers.md): versions, bindings, routes, and rollback.
- [Incidents](references/incidents.md): bounded investigation and mitigation.

Report the browser URL, selected account and resource, saved-state comparison,
relevant live verification, and recovery. Record supplemental diagnostics separately;
never reveal tokens, secret bindings, authorization data, or unreviewed logs.
