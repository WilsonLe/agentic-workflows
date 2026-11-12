# Vercel authority and secrets

Apply the [shared authority and concealed-secret contract](../../agentic-workflows/references/task-authority-and-secrets.md)
and [CLI-token channel](../../agentic-workflows/references/service-browser-operations.md).
Fetch `VERCEL_TOKEN` from Infisical inside the concealed process; require CLI support
for its environment input. Do not use `--token`, cached login, connectors or dashboard
management as a fallback. Verify identity and exact scope for every task/worktree.

Leave legacy auth files untouched and never copy them into a worktree. Keep decrypted
environment values, bootstrap secrets and credential-bearing preview URLs out of
arguments/output. A missing safe input/output route blocks that operation.
