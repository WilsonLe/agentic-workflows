---
name: digitalocean-account-operations
description: Inspect and manage DigitalOcean through authenticated doctl using the protected launcher. Use the built-in Codex browser to select the project account and acquire missing access tokens, then verify CLI authentication. Browser operations are fallback only when the authenticated CLI cannot perform the requested action. Keep credentials in gitignored .cli/digitalocean and carry them with local env files into new worktrees.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use doctl and protected launcher; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# DigitalOcean Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

Read [onboarding](references/onboarding.md) for browser-assisted authentication.
Before credentials or writes, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).

Apply [project-local credential controls](../agentic-workflows/references/task-authority-and-secrets.md#project-local-cli-credentials).
Install into `.cli/digitalocean/credentials.json` using the existing installer's
explicit `--destination`, and pass that checkout's absolute `--credentials-file`
on every protected client invocation, including abbreviated runbook examples.
Keep the normalized record at mode `0400` and its directories at `0700`. Carry
it with local env files into new same-project worktrees and reverify there.

## DigitalOcean client

Use `<plugin-root>/scripts/digitalocean_cli.py` and its protected access token.
Check installed doctl version/help. Verify `doctl --context default account get
--output json` through the launcher, then resolve exact account/project/resource,
region, and relevant environment. Preserve `default` context so an unrelated
stored context cannot override the launcher's token. Browser login is not CLI auth.

If credentials are missing, obtain the supported scoped access token through
visible browser controls and validated concealed transfer, install through the
protected helper, then verify account/resource reads again. Preserve owner-only
storage, provider type checks, approval guards, and sanitized output.

## Runbooks

Read [change management](references/change-management.md) before mutations,
[compute/networking](references/compute-networking.md), [DNS](references/dns.md),
[managed services](references/managed-services.md), or
[troubleshooting](references/troubleshooting.md) as required.

Default supported create/update/delete, deploy, resize, migrate, and recovery
operations to authenticated doctl within task authority. If doctl cannot perform
the exact action, document the support gap and use the dashboard on the verified
same account/project/resource. Missing authentication or denied scope is not a
fallback reason. Never expose SSH private keys, kubeconfig, registry credentials,
database connection credentials, tokens, or unreviewed traces.


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
