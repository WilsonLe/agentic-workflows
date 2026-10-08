# Authenticated CLI operations with browser assistance

This is the channel contract for Railway, Vercel, Cloudflare, DigitalOcean,
ERPNext, and Excalidraw. It takes precedence over general browser preferences
and provider runbooks for authentication and execution channel selection.

## Default to an authenticated CLI

1. Resolve the intended account/team/workspace, project, environment, and resource
   from the task, project documentation, repository links, and domain evidence.
   Never choose the first account or a matching project name alone.
2. Identify the supported provider CLI or bundled command-line client. Install a
   missing tool from official instructions when within scope; absence is not an
   authenticated capability check. ERPNext and Excalidraw use their protected
   Python command-line clients; do not invent separate official provider CLIs.
3. Check existing CLI authentication read-only. Reuse valid credentials only when
   authenticated identity and exact target match the current project. A credential
   file, local link, CLI installation, or earlier login is not authentication proof.
4. If authentication is missing, expired, or for the wrong account, use the browser
   authentication flow below, then return to the CLI and verify again. Do not use
   browser management merely because the CLI is unauthenticated. Preserve unrelated
   logins/credentials; replacement or rotation needs scope for that exact effect.
5. Once authenticated, use supported CLI commands for reads and authorized
   management, creation, updates, deletion, deployment, and recovery. Retain
   protected wrappers, exact-target flags, output controls, and provider guards.
   Recheck identity and target before consequential writes or after context drift.

## Authenticate using the built-in browser

In Codex, open or reuse a visible built-in Codex browser tab for provider login,
OAuth/device authorization, or API-key/token acquisition. Read the host's browser
control documentation first. On other supported hosts, use their authenticated
browser controls. Honor an explicit user browser selection.

1. Open the official dashboard or CLI-provided official authentication URL. Inspect
   the signed-in identity and account/team/workspace selector. Select the account
   appropriate to the current project using observed metadata. Ask only if the
   account or exact target remains ambiguous.
2. Prefer supported CLI login/OAuth where compatible with the provider contract.
   When a protected client requires an API key/token, obtain the supported type in
   the browser with least sufficient account/resource scope. Preserve provider
   token-type constraints; do not substitute a session cookie, unsupported token,
   or broader account to make authentication succeed.
3. Let the user complete private password entry, MFA, CAPTCHA, or human-only
   authentication. Never extract cookies, passwords, browser storage, or sessions.
   Obtain tokens through official controls, not hidden browser/session extraction.
4. Before generating/revealing/copying a key, establish a validated concealed
   transfer into the client's protected store or supported login flow. Apply
   task-authority-and-secrets and the provider credential contract. Never put
   key/token values in chat, tool arguments/output, DOM reads, screenshots, logs,
   shell history, process arguments, Git, or evidence. A masked field or Copy
   button alone is insufficient. If safe transfer is unavailable, let the user
   enter/store the credential privately and report the exact blocked setup step.
5. Return to the CLI and verify authentication read-only. Resolve and match the
   account/team/workspace, project, environment, and resource to browser and task
   evidence. Login success or key creation alone is insufficient. On mismatch or
   unknown identity/scope, stop dependent operations.

Reuse task authority for necessary in-scope authentication and secure setup; do
not ask again for each login, consent, Copy, or Save step. Respect enforced human
approvals and actual permissions. Inspection does not authorize unrelated service
changes or broader permissions.

## Browser fallback after a capability check

Use browser service operations only when the authenticated CLI cannot perform
what was requested. Establish the exact limitation through installed help,
supported client commands, current official documentation, or a safe read-only
capability check. Do not execute a mutation just to test support. Missing/expired
credentials require authentication recovery, not browser fallback. Permission
denials cannot be bypassed through another account, channel, or broader token.

Record the unsupported operation and why the authenticated CLI cannot complete
it, then use supported visible browser controls on the same verified account,
project, and resource. Existing operation authority covers the fallback; do not
ask for extra approval solely for changing channel. Return to the CLI for later
supported actions. Do not silently move the entire task to browser, MCP,
page-script fetches, or hidden application state. If neither supported channel
can complete the action, finish independent work and report the concrete blocker.

Local Excalidraw JSON validation/rendering is preparation and needs no account.
An authenticated client capability gap can justify browser canvas editing or live
visual verification. Distinguish local previews from saved Plus scenes and verify
persistence at the intended target.

## Authority and completion evidence

Before writes, capture relevant non-secret pre-state, exact target, effect,
cost/access/traffic/data impact, verification, and recovery. Inspection/planning
authorize reads only. Production, destructive effects, communications, and new
charges need authority for the exact effect. Retain enforced human approval
controls. Helper confirmation flags express existing authority and never create it.

Execute the smallest operation and read back saved state using authenticated CLI
or justified browser fallback. Observe asynchronous terminal state and verify
relevant live behavior. A login, acknowledgement, toast, queued job, screenshot,
or local preview alone is insufficient. If an outcome is unknown, read back
before retrying; do not duplicate writes or automatically send an inverse action.
Bound and sanitize logs; never dump secrets or raw authorization data.

Report the CLI/client, verified identity/scope, operation shape without secrets,
saved-state comparison, live verification, and recovery. For browser-assisted
authentication report only provider/account and completion status. For browser
service fallback report the capability reason, target URL, and saved-state evidence.
