# Provider operation channels

For Vercel, always use the [Vercel plugin/connected app in Codex](../../vercel-account-operations/SKILL.md).
Codex manages its authentication; exclude Vercel credentials from local `.cli/`
setup and worktree copies. Missing connection or operation support is a blocker.

## PostHog and Polar connected operations

Always use the configured PostHog and Polar plugins/connected apps through Codex
for remote analytics, billing, and account operations. This channel contract takes
precedence over generic CLI, browser, and credential-setup guidance. Codex owns
connector authentication; reuse an existing healthy connection without onboarding
it again. Do not install/authenticate a provider CLI, request API tokens, create
`.cli/posthog/` or `.cli/polar/`, or read/copy legacy authentication stores for
these operations. Leave existing stores untouched.

1. Resolve the target from the request and project evidence before provider skill
   or tool discovery; ask only for a genuinely ambiguous target. Discover the
   available connected tools and load the applicable plugin skill/instructions.
   Verify the connected identity/scope
   and exact PostHog project or Polar organization and sandbox/production environment
   through read-only tool metadata or operations before dependent work. Connection
   presence alone does not prove permissions or select the intended target.
2. Execute authorized operations through those tools and read back the saved state.
   Retain task authority, data minimization, and secret-safe output controls. Billing
   changes, refunds, new charges, and production effects require authority covering
   that effect; a configured connection grants none by itself. Follow the provider's
   tool instructions for bounded queries and safe result handling.
3. If a connection is missing, expired, or mismatched, recover it through Codex's
   plugin/connector flow, then reverify the target. Let the user complete any
   enforced private sign-in step. On insufficient permissions or unsupported
   operations, report the exact limitation and finish independent work. Do not
   fall back to CLI tokens, raw HTTP/SDK account calls, or dashboard management,
   and do not bypass a permission denial through another account or broader token.
4. Report the verified target, operation, readback, and any remaining gap without
   exposing secrets or unnecessary customer/event data. Tool discovery and package
   checks alone do not prove live access or an operation's success.

Application runtime integration is separate: PostHog event capture and Polar SDK
or webhook code may still need documented application configuration and secrets.
Use the provider's integration skill for that work; keep runtime credentials out
of chat/Git and do not extract connector authentication or turn application keys
into an agent account-management fallback. This policy neither migrates nor
deletes existing credentials.

## Providers using authenticated clients

The CLI/browser contract below applies to Supabase, Railway, Cloudflare, and
DigitalOcean. It takes precedence over general browser preferences and provider
runbooks for their authentication and execution channel selection.

## Default to an authenticated CLI

1. Resolve the intended account/team/workspace, project, environment, and resource
   from the task, project documentation, repository links, and domain evidence.
   Never choose the first account or a matching project name alone.
2. Identify the supported provider CLI or bundled command-line client. Install a
   missing tool from official instructions when within scope; absence is not an
   authenticated capability check.
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

## Authenticate with browser assistance

In Codex, open or reuse a visible built-in Codex browser tab for provider login,
OAuth/device authorization, or API-key/token acquisition. Read the host's browser
control documentation first. Without browser controls, give the user the
official URL or CLI login command to complete instead of offering to perform it,
then return to CLI verification.
Honor an explicit user browser selection.

1. Open the official dashboard or CLI-provided official authentication URL. Inspect
   the signed-in identity separately from the account/team/workspace selector.
   Match both identity and resource scope to the current project using observed
   metadata. For a different login identity, follow
   [browser account switching](#switch-browser-login-accounts); a tenant selector
   alone does not establish that switch. Ask only if identity or target is ambiguous.
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

### Switch browser login accounts

Apply this procedure when browser authentication or an authorized browser fallback
needs a different login identity. Reuse a matching session. Team, organization,
workspace, company, or resource-account selection may change scope under the same
user; inspect the signed-in user rather than treating that selector as a login
account switcher. Use observed controls, not an assumption about a provider's UI.

1. Resolve the intended login identity and exact service/site before switching;
   ask only if ambiguous. State which identity the task needs, preserve unsaved
   service work, and account for other tabs sharing this browser context. Necessary
   in-scope switching reuses task authority without another routine approval wait.
2. Use a visible login-identity switcher if it supports the intended account, then
   verify the resulting identity. If none is available or it cannot select that
   identity, sign out through the service's visible controls, verify its signed-out
   or login screen, then sign in to the intended account through official controls.
   Use service-local sign-out, not an all-devices/session-revocation action.
3. If OAuth or SSO returns to the previous identity, sign out of the service again
   and use the identity provider's visible account chooser/switcher where available.
   Otherwise let the user complete the intended login privately. Preserve unrelated
   provider sessions; do not clear browser data, extract sessions, or use
   administrative impersonation to switch users. Private password, MFA, CAPTCHA,
   and concealed credential-transfer rules above still apply. Without supported
   controls or a completed private step, stop dependent work and report that step.
4. Verify the resulting service login identity and exact account/team/workspace,
   project, environment, and resource using stable IDs where available. Stop on a
   mismatch or unknown identity/scope; resume after verification. Other tabs sharing
   the changed service session must reverify identity before further operations.
5. Return to read-only CLI verification through the intended project's credential
   store. A browser switch does not select the CLI identity and does not require
   global CLI logout, token revocation, or overwriting unrelated credentials. Retain
   provider-specific token and rotating-session rules. When existing CLI identity
   and target are correct and no browser work is needed, leave browser sessions as-is.

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
