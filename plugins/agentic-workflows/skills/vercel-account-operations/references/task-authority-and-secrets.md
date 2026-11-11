# Vercel authority and secrets

Apply the shared [task authority and concealed secrets contract](../../agentic-workflows/references/task-authority-and-secrets.md)
for operation authority, enforced approvals and secret-safe evidence. The
[Vercel connected-app contract](../SKILL.md) owns channel selection and overrides
any generic CLI instructions in shared guidance.

Codex manages the Vercel connection. Do not read, create, migrate or copy local
Vercel authentication files. Leave existing credential stores untouched. Verify
identity and scope through connected-app reads in each task/worktree. Never
request, reveal or log tokens, decrypted environment values or private access
URLs. A missing safe input/output mechanism blocks that secret operation.
