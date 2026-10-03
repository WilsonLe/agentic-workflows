# Cloudflare Account onboarding

Use this guide when a user asks to set up, onboard, or get started with the Cloudflare Account plugin.

## Prerequisites

The plugin requires an authorized scoped API token in a private local file. For an
authorized setup, the agent may create it in the provider and transfer it through a
validated concealed route; follow [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md). It accepts user or
account API tokens and rejects Global API Keys. Wrangler remains optional.

Never ask the user to paste a token into chat, a command argument, or a tool call.

## First-run workflow

1. Establish the token's scope and type from provider metadata or the user's supplied provenance without viewing its value. Create it only when needed within setup authority.
2. Install it with `cloudflare_configure_credentials.py`, selecting the token type explicitly if
   its current supported prefix does not identify it.
3. Add `--verify --archive-source` to verify read-only and move the exact successful source into
   the protected imported-sources directory. Failed verification leaves the source in place.
4. Read the intended account, then list zones if the token permits it.
5. Report only token type, active status, visible account count, required access, and any missing permissions.
6. Do not perform a write as an onboarding test.

## Ready state

The plugin is ready when token verification succeeds, the configured account matches the intended account, and the minimum resources required for the user's planned work can be read. Writes need task authority covering their target and effect, not a new confirmation for each step.

## Suggested first prompt

> Onboard me to Cloudflare Account. From the CLI, verify the configured API token, confirm the
> account, and list the zones I can read. Do not make any changes.
