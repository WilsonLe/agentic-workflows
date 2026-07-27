# Cloudflare Account onboarding

Use this guide when a user asks to set up, onboard, or get started with the Cloudflare Account plugin.

## Prerequisites

The plugin requires `curl`, a user-provided least-privilege account API token available as
`CLOUDFLARE_API_TOKEN`, and `CLOUDFLARE_ACCOUNT_ID` when the selected command requires an explicit
account. Wrangler is optional and should be used only for supported Developer Platform workflows.
Do not use a Global API Key.

Never ask the user to paste a token into chat, a file, a command argument, or a tool call.

The user should configure the variables through their normal secret manager or secure launcher in
the environment that starts Codex. Restart Codex and open a new task after changing credentials.

## First-run workflow

1. Confirm that the user has created an appropriately scoped token without asking to see it.
2. Confirm `curl` is available and only whether the required variable exists; never print it.
3. Verify the token with a read-only curl request described in `api-patterns.md`.
4. Read the intended account, then list zones if the token permits it.
5. Report a read-only readiness summary: credential health, configured account, visible zones, and any missing permissions.
6. Do not perform a write as an onboarding test.

## Ready state

The plugin is ready when token verification succeeds, the configured account matches the intended account, and the minimum resources required for the user's planned work can be read. Write operations still require explicit approval for each change.

## Suggested first prompt

> Onboard me to Cloudflare Account. From the CLI, verify the configured API token, confirm the
> account, and list the zones I can read. Do not make any changes.
