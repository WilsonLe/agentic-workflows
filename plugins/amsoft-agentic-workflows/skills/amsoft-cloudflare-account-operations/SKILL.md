---
name: amsoft-cloudflare-account-operations
description: Safely inspect and operate a Cloudflare account from the CLI using a user-provided scoped API token, curl for the Cloudflare v4 API, and Wrangler for supported Developer Platform workflows. Use for setup or first-run guidance, token verification, account discovery, zones, DNS, Workers, Pages, KV, D1, R2, WAF, rules, logs, audits, incidents, approval-gated changes, and debugging unfamiliar or failed Cloudflare CLI requests without MCP.
---

# Cloudflare Account Operations

Use command-line tools as the execution layer. Use `curl` for general Cloudflare v4 API operations
and `npx wrangler` or an installed `wrangler` binary only for products and commands Wrangler
supports. Do not add or call an MCP server.

For setup, onboarding, credential configuration, or first-use requests, read
[references/onboarding.md](references/onboarding.md). Expect `CLOUDFLARE_API_TOKEN` to be provided
securely in the process environment. Never request a token in chat and never use a write operation
as an onboarding test.

## Core workflow

1. Confirm the required CLI is available.
2. Verify the token with a read-only Cloudflare token verification endpoint.
3. Discover account context and resource identifiers with read-only commands; never guess account,
   zone, record, script, database, bucket, or ruleset IDs.
4. For a requested change, read the current resource and capture its relevant fields.
5. Consult the current Cloudflare API reference for the exact endpoint, method, and payload.
6. Present the exact secret-free command, intended change, target IDs, impact, validation, and
   rollback.
7. Obtain explicit user approval before any non-GET request.
8. Run the smallest sufficient CLI command.
9. Read the resource again and report before/after evidence.

Never interpret a request to inspect, diagnose, review, explain, or plan as authorization to change Cloudflare.

## Authentication and secrets

- Require `CLOUDFLARE_API_TOKEN` in the environment that runs the CLI.
- Use `CLOUDFLARE_ACCOUNT_ID` when the selected command requires a specific account; otherwise
  discover the account from a read-only API call.
- Never ask the user to paste a token into chat, a source file, a runbook, a literal command
  argument, or a tool parameter.
- Never print, echo, log, or return the token.
- Prefer a least-privilege, expiring account API token scoped to the required account and resources.
- If verification fails, report the HTTP status and sanitized Cloudflare errors.
- Do not use a Global API Key.

## CLI selection

- Use `curl` with `Authorization: Bearer` for the complete Cloudflare v4 API surface.
- Use Wrangler for Workers and supported Developer Platform products when its command maps cleanly
  to the task.
- Run `wrangler --help`, `wrangler <command> --help`, or `npx wrangler <command> --help` when
  syntax or support is unclear.
- Do not silently switch to Global API Keys, dashboard automation, or an MCP tool.

## API command discipline

- Read [references/api-patterns.md](references/api-patterns.md) before building a curl request.
- Keep the literal token out of the command; reference `CLOUDFLARE_API_TOKEN`.
- Prefer JSON responses and preserve Cloudflare error codes, messages, and pagination evidence.
- Use the smallest sufficient request body and a temporary payload file only when necessary. Do not
  store credentials in payloads.

Treat these as high-impact and require especially clear confirmation:

- deleting zones, DNS records, Workers, Pages projects, buckets, databases, tunnels, or rulesets;
- changing nameservers, DNSSEC, SSL/TLS modes, WAF behavior, access policies, routing, or production traffic;
- replacing an entire configuration with `PUT`;
- rotating or deleting credentials;
- purging broad caches.

After a write, verify with a read-only command and state whether rollback is available.

## Help and debugging

When stuck, inspect the installed CLI help first. For Wrangler, enable sanitized debug logging only
when needed:

```bash
WRANGLER_LOG=debug WRANGLER_LOG_SANITIZE=true npx wrangler <read-command>
```

For curl, use status and response-body diagnostics without shell tracing. Never use `set -x`, dump
the environment, or return raw request headers containing authorization material.

## Runbooks

Read the relevant reference before acting:

- [General change runbook](references/change-management.md) for every mutation.
- [DNS runbook](references/dns.md) for DNS records, proxy state, DNSSEC, and zone settings.
- [Workers runbook](references/workers.md) for scripts, routes, bindings, secrets, deployments, and rollbacks.
- [Incident runbook](references/incidents.md) for outages, security events, traffic anomalies, or emergency rollback.
- [API patterns](references/api-patterns.md) for path conventions, pagination, errors, and verification calls.

Cloudflare APIs change. Retrieve current Cloudflare documentation before relying on endpoint shapes, limits, compatibility dates, or product-specific behavior.
