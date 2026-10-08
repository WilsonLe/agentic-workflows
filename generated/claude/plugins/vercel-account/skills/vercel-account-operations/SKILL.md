---
name: vercel-account-operations
description: Inspect and manage Vercel through an authenticated official CLI. Use the built-in Codex browser for login/OAuth or missing token acquisition and verify the account/team/project before CLI execution. Browser operations are fallback only for unsupported authenticated CLI actions; covers accounts, access, domains, integrations, spend settings, and deployments.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated service CLI** — Use Official Vercel CLI; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# Vercel Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the built-in Codex browser for
supported login or secure key/token acquisition, then return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

Read [onboarding](references/onboarding.md) for login/authentication recovery,
[account management](references/account-management.md) for accounts/teams/projects,
and [deployment operations](references/deployment-operations.md) for deploys,
variables, incidents, and rollback. Before setup or writes, apply
[task authority and concealed secrets](references/task-authority-and-secrets.md).

## Vercel client

Check `vercel --version` and `vercel whoami`; reuse valid matching authentication.
Use read-only team/project inventory and explicit scope to resolve the exact
team ID/slug, project, and environment. Inspect installed help/current official
documentation for syntax, including documented `vercel api` operations when the
CLI supports the needed account action. Do not change global team context,
auto-link a directory, or assume a local `.vercel/` link proves identity.

When login is missing, use the CLI's supported authentication flow in the built-in
browser with the intended account; verify `whoami` and team/project scope afterward.
Use tokens only if required by the chosen supported flow, through concealed
protected transfer. CLI authentication does not prove MCP authentication; MCP is
not a replacement for this default CLI workflow. Application guidance plugins
remain separate from account authentication and do not need installation as setup.

Global authentication setup does not create/link projects, deploy, or change
membership/billing. If the authenticated CLI, including supported API commands,
cannot perform an action, record the exact capability gap and use the dashboard
on the same account and target. Preserve enforced approval and access controls.


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
