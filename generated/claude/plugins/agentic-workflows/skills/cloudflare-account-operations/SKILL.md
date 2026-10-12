---
name: cloudflare-account-operations
description: Inspect and manage Cloudflare using authenticated protected command-line tools and supported Wrangler workflows. Use browser-assisted login to select the project account and acquire missing scoped credentials, then verify CLI authentication. Browser operations are fallback only when the authenticated client lacks the requested capability. Keep credentials in gitignored .cli/cloudflare and carry them with local env files into new worktrees.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected Cloudflare CLI helper and supported Wrangler; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the host's browser controls (the built-in Codex browser in Codex, Claude in Chrome in Claude Code) for supported login or secure key/token acquisition, or let the user complete that step, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

<!-- claude-code-notes:start -->
## Claude Code

This skill's references write `<plugin-root>` for `${CLAUDE_PLUGIN_ROOT}`. Use those absolute paths in commands you run or give to the user; never show the placeholders.

`<project-root>` is the top-level directory of the checkout you are working in (`git rev-parse --show-toplevel`, or the working directory outside a Git checkout), which can differ from where Claude Code started.

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

Claude in Chrome is available only when its browser tools are in this session's tool list. If they are absent, do not offer to open pages, create keys or tokens, or say you can use Claude in Chrome. Give the user the exact URL and steps to complete themselves; `claude --chrome` or `/chrome` enables browser help in a later session.

<!-- claude-code-notes:end -->

# Cloudflare Account Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the host's browser controls (the
built-in Codex browser in Codex, Claude in Chrome in Claude Code) for supported
login or secure key/token acquisition. Without a browser tool in this session,
give the user the exact login step instead of offering to perform it. Then
return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.

Read [onboarding](references/onboarding.md) for secure browser-assisted token setup.
Before credentials or writes, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).

Apply [project-local credential controls](../agentic-workflows/references/task-authority-and-secrets.md#project-local-cli-credentials).
Install into `.cli/cloudflare/credentials.json` using the existing installer's
explicit `--destination`, and pass that checkout's absolute `--credentials-file`
on every protected client invocation, including abbreviated runbook examples.
Keep the normalized record at mode `0400` and its directories at `0700`. Carry
it with local env files into new same-project worktrees and reverify there.

## Cloudflare clients

Use the protected `cloudflare_api.py` command-line helper for supported API reads
and a supported guarded CLI path for the requested operation. Use Wrangler only
for workflows it supports. Inspect installed help and current official documentation;
do not invent API routes, flags, or protected execution capabilities.

Verify protected credential health read-only, then independently resolve the
account and exact zone/resource/environment. A token verification response alone
is not account/target proof. Obtain a scoped supported token with browser assistance
or from the user if missing; preserve the installer's classification, ownership/mode,
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
