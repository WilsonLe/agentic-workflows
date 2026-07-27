---
name: amsoft-cloudflare-account-operations
description: Safely inspect and operate a Cloudflare account through the AMSoft Cloudflare MCP tools using a scoped account API token, and onboard users to the bundled Cloudflare workflow. Use for setup or first-run guidance, Cloudflare account discovery, token verification, zones, DNS, Workers, Pages, KV, D1, R2, WAF, rules, logs, audits, and other Cloudflare v4 API work, especially when a task requires planning, executing, or verifying a Cloudflare change.
---

# Cloudflare Account Operations

Use the bundled tools as the execution layer and current Cloudflare documentation as the source of truth for endpoint paths and payloads.

For setup, onboarding, credential configuration, or first-use requests, read
[references/onboarding.md](references/onboarding.md). Never request a token in chat, and never use
a write operation as an onboarding test.

## Core workflow

1. Call `amsoft_cloudflare_verify_token`.
2. Call `amsoft_cloudflare_get_account` when account context is needed.
3. Discover resource identifiers with read calls; never guess account, zone, record, script, database, bucket, or ruleset IDs.
4. For a requested change, read the current resource and capture its relevant fields.
5. Consult the current Cloudflare API reference for the exact endpoint, method, and payload.
6. Present the intended change, target IDs, impact, and rollback.
7. Obtain explicit user approval before any non-GET request.
8. Call `amsoft_cloudflare_api_write` with `confirmed: true`.
9. Read the resource again and report the before/after evidence.

Never interpret a request to inspect, diagnose, review, explain, or plan as authorization to change Cloudflare.

## Authentication and secrets

- Expect `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` in the MCP server environment.
- Never ask the user to paste a token into chat, a source file, a runbook, a command argument, or a tool parameter.
- Do not use the generic write tool to transmit a new secret supplied in chat; configure secrets through an approved secret-entry path.
- Never print, echo, log, or return the token.
- Prefer a least-privilege, expiring account API token scoped to the required account and resources.
- If verification fails, report the HTTP status and Cloudflare error messages without exposing credentials.
- Do not use a Global API Key.

## Read operations

Use the most specific tool available:

- `amsoft_cloudflare_verify_token` for credential health.
- `amsoft_cloudflare_get_account` for the configured account.
- `amsoft_cloudflare_list_zones` for zone discovery.
- `amsoft_cloudflare_api_read` for all other GET endpoints.

Pass API paths relative to `/client/v4`, such as `/zones/{zone_id}/dns_records`. Put query parameters in `query`, not in `path`.

Paginate list endpoints until the requested scope is complete. Preserve `result_info` in evidence when present.

## Write operations

Use `amsoft_cloudflare_api_write` only after explicit approval in the current conversation. Include the exact API path, method, and smallest sufficient request body.

Treat these as high-impact and require especially clear confirmation:

- deleting zones, DNS records, Workers, Pages projects, buckets, databases, tunnels, or rulesets;
- changing nameservers, DNSSEC, SSL/TLS modes, WAF behavior, access policies, routing, or production traffic;
- replacing an entire configuration with `PUT`;
- rotating or deleting credentials;
- purging broad caches.

After a write, verify with a GET and state whether rollback is available.

## Runbooks

Read the relevant reference before acting:

- [General change runbook](references/change-management.md) for every mutation.
- [DNS runbook](references/dns.md) for DNS records, proxy state, DNSSEC, and zone settings.
- [Workers runbook](references/workers.md) for scripts, routes, bindings, secrets, deployments, and rollbacks.
- [Incident runbook](references/incidents.md) for outages, security events, traffic anomalies, or emergency rollback.
- [API patterns](references/api-patterns.md) for path conventions, pagination, errors, and verification calls.

Cloudflare APIs change. Retrieve current Cloudflare documentation before relying on endpoint shapes, limits, compatibility dates, or product-specific behavior.
