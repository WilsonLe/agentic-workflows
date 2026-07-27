# AMSoft Cloudflare Account Operations onboarding

Use this guide when a user asks to set up, onboard, or get started with the bundled Cloudflare workflow.

## Prerequisites

The workflow requires a 32-character Cloudflare account ID and a least-privilege account API token scoped to the account and products the user intends to manage. Do not use a Global API Key.

Never ask the user to paste a token into chat, a file, a command argument, or a tool call.

On macOS, use the central plugin's bundled `scripts/configure-cloudflare-macos-keychain.sh` script. It stores the account ID and token in macOS Keychain. On other systems, set `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` in the environment that launches Codex. Restart Codex and open a new task after changing credentials.

## First-run workflow

1. Confirm that the user has created an appropriately scoped token without asking to see it.
2. Guide the user through the approved credential-entry path for their system.
3. After restart, call the namespaced token-verification tool.
4. Read the configured account, then list zones if the token permits it.
5. Report a read-only readiness summary: credential health, configured account, visible zones, and any missing permissions.
6. Do not perform a write as an onboarding test.

## Ready state

The workflow is ready when token verification succeeds, the configured account matches the intended account, and the minimum resources required for the user's planned work can be read. Write operations still require explicit approval for each change.

## Suggested first prompt

> Onboard me to AMSoft Cloudflare Account Operations. Verify the configured token, confirm the account, and list the zones I can read. Do not make any changes, and never ask me to paste the token into chat.
