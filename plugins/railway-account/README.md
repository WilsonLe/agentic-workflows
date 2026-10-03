# Railway Account

Agentic Workflows account-token-only Railway CLI operations plugin for Codex.

## Boundary

This plugin accepts only a Railway account token created in Account Settings
with **No workspace** selected. Railway documents this as its broadest token
class: it can act across every resource and workspace the account is authorized
to access. The helper exposes it only as `RAILWAY_API_TOKEN`.

Project tokens (`RAILWAY_TOKEN`), workspace tokens, OAuth tokens, and persisted
interactive CLI logins are not supported by this plugin.

Never paste a token into chat or commit it. Onboarding accepts a local file
path, installs a protected copy under `~/.config/agentic-workflows/railway/`, and verifies
the account with a read-only command.

## Prerequisites

- Railway CLI installed and available as `railway`
- Python 3
- A downloaded account token created with **No workspace**

## First prompt

```text
Use Railway Account Operations to onboard my downloaded account token read-only. Ask only for its local path, verify the account, and do not change Railway.
```

All Railway mutations require an exact target, authority, readback, and
rollback or recovery plan. Reuse the user's task request for necessary steps,
including provider approval buttons and supported concealed credential transfer.
Production and destructive effects need authority covering that target and impact;
no repeated confirmation is needed when the request already covers them. See
[task authority and concealed secrets](skills/railway-account-operations/references/task-authority-and-secrets.md).
