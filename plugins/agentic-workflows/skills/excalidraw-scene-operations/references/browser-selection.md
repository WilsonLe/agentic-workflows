# Service browser operations

This is the operating contract for Railway, Vercel, Cloudflare, DigitalOcean,
ERPNext, and Excalidraw. It takes precedence over the general browser preference
and optional CLI/API runbooks for these services.

## Browser is the base

In Codex, open or reuse the built-in Codex browser. Read the host's documented
browser controls before operating a tab; use only supported controls and observed
UI. Keep the tab visible for account selection, authentication, and management.
On another supported host, use its authenticated browser controls. An explicit
user browser selection takes precedence; report a missing required browser or
interaction capability instead of silently switching channels.

1. Resolve the current project's provider URL, repository, domain, organization,
   and intended environment from the task and project documentation. Local links
   are hints, not proof of the active browser account. Do not read local secrets.
2. Open the provider dashboard and inspect the signed-in identity and available
   account/team/workspace selector. Reuse an active session. Let the user complete
   private password entry, MFA, CAPTCHA, or human-only authentication when needed.
   Do not extract cookies, tokens, passwords, browser storage, or session state.
3. Select the account/team/workspace that matches this project. Verify the visible
   project, service/resource, environment, domain, and deployment or record when
   applicable. Never choose the first account or a matching name alone when there
   are multiple candidates. Use visible IDs, URLs, repository and domain evidence.
   Ask only if the intended identity or target remains ambiguous.
4. Recheck the visible account and exact target immediately before a mutation,
   especially after navigation, tab changes, account switching, or a long pause.
   Keep unrelated tabs, accounts, resources, and user settings untouched.

Browser onboarding needs a signed-in session and the required UI permissions.
It does not require an API token, CLI installation, MCP connection, or credential
export. Do not generate or rotate a token merely to inspect or manage a service.

For an explicitly local Excalidraw canvas/file task, verify the exact local
persistence target; account/workspace selection applies when using saved Plus
scenes. Do not require sign-in merely to prepare or edit a local scene.

## Manage through the UI

Use visible browser controls for account management, creation, updates, deletion,
configuration, membership, billing, deployment, rollback, and scene/document
editing. Before acting, capture relevant non-secret pre-state, identify the
exact target, effect, cost/access/traffic/data impact, verification, and recovery.
Apply the user's existing task authority; do not ask again for routine in-scope
Save, Add, or provider confirmation buttons. Inspection and planning authorize
reads only. Production, destructive effects, communication, and new charges need
authority covering the exact effect. Respect enforced human approval controls.

After saving, reopen or refresh the same resource and compare the intended state.
For asynchronous work, observe a terminal state and verify the relevant live
behavior. A click, success toast, queued job, screenshot, or local preview alone
does not prove the requested outcome. If the outcome is unknown, read back before
retrying; do not duplicate writes or automatically send an inverse operation.

If a management action cannot be completed through supported UI controls, finish
independent work and report the exact limitation, target, and proposed alternative.
Use a non-browser mutation only when the user explicitly directs that channel
for the affected operation. Read-only CLI permission does not authorize CLI writes.
Do not bypass the UI with page-script fetches, hidden state changes, direct API
requests, MCP mutations, or credential extraction.

## Optional read-only diagnostics

CLI tools and protected API helpers may supplement the established browser
context for bounded logs, status, metrics, or narrowly scoped inventories. They
are optional and do not replace browser account selection or management.

- Verify the tool's authenticated identity independently, then match its account,
  team/workspace, project, service/resource, and environment to the browser target.
  Browser sign-in does not authenticate a CLI, and CLI sign-in does not prove a
  matching browser session. On mismatch or unknown scope, stop that diagnostic.
- Prefer existing authorized authentication. If a diagnostic needs credentials,
  explain that optional requirement and use the provider's protected credential
  contract only when setup is within scope. Never harvest browser credentials or
  make token setup a prerequisite for the browser workflow.
- Use exact targets and read-only commands with time, line/item, and response
  bounds. Inspect installed help/current documentation for syntax. Avoid commands
  that implicitly link projects, alter global context, deploy, or change settings.
- Sanitize logs and errors before reporting; application logs can contain secrets
  and personal data even when a launcher hides the provider token. Never dump
  environment values, decrypted variables, credentials, or raw authorization data.
- Report the supplemental channel and its verified scope separately from browser
  evidence. Missing CLI access blocks only that diagnostic unless it is required
  for the requested outcome. Report unverified claims explicitly.

## Completion evidence

Report the observed browser URL, resolved account/team and exact project/target,
saved-state readback, relevant live verification, and recovery state. Include only
the identity detail needed to distinguish accounts. Record any optional diagnostic,
its independently verified target, sanitized result, and capability limitations.
