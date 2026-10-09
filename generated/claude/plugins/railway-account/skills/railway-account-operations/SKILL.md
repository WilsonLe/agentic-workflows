---
name: railway-account-operations
description: Inspect and manage Railway using the authenticated Railway CLI and protected account-token wrapper. Use the built-in Codex browser to select the project account and obtain missing CLI credentials; browser operations are fallback only for unsupported authenticated CLI actions. Covers workspaces, projects, environments, services, deployments, variables, logs, domains, scaling, incidents, and rollback. Keep credentials in gitignored .cli/railway and carry them with local env files into new worktrees.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Railway CLI and protected launcher; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# Railway Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

For first use or authentication recovery, read [onboarding](references/onboarding.md)
and [credential contract](references/credential-contract.md). Before credential
handling or writes, read [task authority and concealed secrets](references/task-authority-and-secrets.md).

Apply [project-local credential controls](references/task-authority-and-secrets.md#project-local-cli-credentials).
Install into `.cli/railway/credentials.json` using the existing installer's
explicit `--destination`, and pass that checkout's absolute `--credentials-file`
on every protected client invocation, including abbreviated runbook examples.
Keep the normalized record at mode `0400` and its directories at `0700`. Carry
it with local env files into new same-project worktrees and reverify there.

## Railway client

Use `<plugin-root>/scripts/railway_cli.py` with its protected account token.
Verify `railway --version` and wrapper `whoami --json` read-only, then resolve the
exact workspace/project/environment/service using structured reads. Read
[target resolution](references/target-resolution.md); do not rely on local link
state alone. Preserve the wrapper's account-token-only contract: browser acquisition
uses Account Settings with **No workspace**. Do not substitute project/workspace
or OAuth tokens, or interactive login state unsupported by the wrapper.

The wrapper accepts `RAILWAY_API_TOKEN` only through protected storage; preserve
its approval/production/destructive guards. Use `variable-names` for names-only
inventory; raw variable lists can expose secrets. Avoid `run`, `shell`, `connect`,
`ssh`, and `dev` surfaces that the wrapper cannot safely execute. Bound and sanitize
logs; provider-token redaction does not hide every application secret.

## Runbooks

- [Change management](references/change-management.md) for mutations/link changes.
- [Deployments](references/deployments.md) for upload, deploy, redeploy, restart, scaling, and rollback.
- [Variables and secrets](references/variables-and-secrets.md) for protected changes.
- [Incidents](references/incidents-and-troubleshooting.md) for diagnostics.

Browser login alone does not authenticate this wrapper. After browser-assisted
credential installation verify the CLI identity and project targets before work.
If a requested operation is unsupported by the authenticated guarded client,
record the limitation and use supported dashboard controls within task authority.


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
