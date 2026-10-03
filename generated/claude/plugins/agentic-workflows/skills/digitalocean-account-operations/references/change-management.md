# DigitalOcean change runbook

Use this runbook for every mutating `doctl` command.

## Before

1. Verify account access and resolve the target with read-only commands.
2. Capture current state and rollback-relevant values in JSON.
3. Inspect action-specific help:

   ```bash
   doctl <resource> <action> --help
   ```

4. Classify impact as low, medium, or high. Treat deletion, traffic, credentials, firewall
   exposure, data, rebuild, resize, migration, failover, cluster or database lifecycle, and
   account-wide behavior as high impact.
5. Present the exact secret-free command, target identifiers, expected effect, cost implications,
   validation, and rollback.
6. Match the exact change to the originating request or existing approval. Continue when covered; ask only for missing authority or a material unresolved decision. Apply [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).

## Execute

1. Run the smallest sufficient command.
2. Stop on an unexpected target, prompt, output, or error.
3. Do not automatically retry a mutation unless the operation is documented as idempotent and the
   prior result is known.
4. Do not broaden scope to related resources without approval.

## Verify

1. Read the changed resource again in JSON.
2. Compare expected and observed fields.
3. Test affected behavior when authorized.
4. Report the command shape, target ID, result, verification evidence, cost or availability impact,
   and rollback state.

Rollback automatically only when the user explicitly authorized it or a bounded incident instruction
already included rollback authority.
