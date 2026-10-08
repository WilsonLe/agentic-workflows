# Railway change runbook

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

Use this runbook for every Railway mutation and every local link-state change.

## Before

1. Verify the account read-only.
2. Resolve and read back workspace, project, environment, service, and current
   deployment as applicable.
3. Capture the smallest pre-state required for verification and rollback
   without recording secrets.
4. Inspect installed command help and current official documentation.
5. Classify the target as `non-production`, `production`, or `account`.
6. Classify deletion, teardown, detach, or data-loss potential as destructive.
7. Present the exact secret-free command, targets, impact, expected result,
   validation, and rollback or recovery.
8. Match write, production, and destructive effects to existing request authority
   using [task authority and concealed secrets](task-authority-and-secrets.md). Ask
   only when the exact target or effect is not covered.

## Execute

Use the launcher:

```text
python3 <plugin-root>/scripts/railway_cli.py \
  --target-class <non-production|production|account> \
  --confirm-write I_APPROVE_RAILWAY_WRITE \
  [--confirm-production I_APPROVE_RAILWAY_PRODUCTION] \
  [--confirm-destructive I_APPROVE_RAILWAY_DESTRUCTIVE] \
  -- <railway-command> <flags>
```

Supply helper confirmation phrases and `--yes` when existing task authority covers
the exact action. Do not ask the user to type these phrases again. Stop on an unexpected
target, prompt, response, or nonzero exit. Do not retry an unknown write
outcome.

## Verify

1. Read the exact resource again.
2. Compare intended and observed fields.
3. Inspect deployment state and bounded logs when affected.
4. Test the external behavior or health endpoint when applicable.
5. Report target IDs, sanitized result, readback, behavior, and rollback state.

Rollback is not implicit. Execute it only when the approved plan included
automatic rollback or the user separately authorizes it after failure.
