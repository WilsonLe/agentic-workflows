# Railway change runbook

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
8. Obtain explicit write approval. Obtain separate production approval and
   destructive approval when applicable.

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

Add `--yes` only after the exact action is approved. Stop on an unexpected
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
