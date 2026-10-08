---
name: cloudflare-account-operations
description: Inspect and manage Cloudflare using authenticated protected command-line tools and supported Wrangler workflows. Use the built-in Codex browser to select the project account and acquire missing scoped credentials, then verify CLI authentication. Browser operations are fallback only when the authenticated client lacks the requested capability.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected Cloudflare CLI helper and supported Wrangler; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# Cloudflare Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

Read [onboarding](references/onboarding.md) for secure browser-assisted token setup.
Before credentials or writes, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).

## Cloudflare clients

Use the protected `cloudflare_api.py` command-line helper for supported API reads
and a supported guarded CLI path for the requested operation. Use Wrangler only
for workflows it supports. Inspect installed help and current official documentation;
do not invent API routes, flags, or protected execution capabilities.

Verify protected credential health read-only, then independently resolve the
account and exact zone/resource/environment. A token verification response alone
is not account/target proof. Obtain a scoped supported token through the built-in
browser if missing; preserve the installer's classification, ownership/mode,
verification, and archival controls. Do not use Global API Keys.

Never expand a token into curl headers or process arguments. If a requested
operation has no supported authenticated secret-safe CLI/client path, document
that capability limitation and use the dashboard. Do not extend a wrapper, send
ad hoc requests, or weaken credential checks just to avoid the browser fallback.

## Runbooks

- [Change management](references/change-management.md) for writes.
- [Diagnostic/API patterns](references/api-patterns.md) for supported protected requests.
- [DNS](references/dns.md), [Workers](references/workers.md), and [incidents](references/incidents.md).

Nameserver/DNSSEC, SSL/TLS, WAF/access/routing, deletion, broad purges, and production
effects need exact-target authority. Recheck saved configuration and relevant live
DNS/route/application behavior after changes; API success alone does not prove health.


## Execution and evidence

Before writes, capture relevant pre-state, exact target, effect, task authority,
verification, and recovery. Inspection/planning authorize reads only. Match
production, destructive, communication, and cost effects to existing authority;
do not ask again for routine in-scope steps. Keep enforced provider approvals.

Run the smallest supported operation through the authenticated client, read back
saved state, observe asynchronous completion, and verify relevant live behavior.
An unknown write outcome requires readback before retrying. Report client/version,
verified identity/scope, sanitized operation and result, readback, and recovery.
If browser fallback is needed, report its concrete CLI capability reason, verify
the same account/target in the UI, use visible controls, and reopen saved state.
Never expose keys, tokens, authorization data, environment values, or unreviewed logs.
