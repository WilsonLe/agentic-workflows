# DigitalOcean change runbook

Use the [Infisical-backed CLI channel](../../agentic-workflows/references/service-browser-operations.md).
Obtain the required token from Infisical and verify provider identity and exact
target through read-only CLI commands. Missing tokens, commands or permissions
block dependent work; do not switch to connectors or cached login.

Use this runbook for every mutating CLI operation.

## Before

1. Verify account access and resolve the target with read-only CLI commands.
2. Capture current state and rollback-relevant values as nonsecret structured data.
3. Inspect the exact CLI command help and provider instructions.
4. Classify impact as low, medium, or high. Treat deletion, traffic, credentials, firewall
   exposure, data, rebuild, resize, migration, failover, cluster or database lifecycle, and
   account-wide behavior as high impact.
5. Present the exact nonsecret tool operation, target identifiers, expected effect, cost implications,
   validation, and rollback.
6. Match the exact change to the originating request or existing approval. Continue when covered; ask only for missing authority or a material unresolved decision. Apply [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).

## Execute

1. Run the smallest sufficient CLI operation.
2. Stop on an unexpected target, prompt, output, or error.
3. Do not automatically retry a mutation unless the operation is documented as idempotent and the
   prior result is known.
4. Do not broaden scope to related resources without approval.

## Verify

1. Read the changed resource again as nonsecret structured data.
2. Compare expected and observed fields.
3. Test affected behavior when authorized.
4. Report the tool operation, target ID, result, verification evidence, cost or availability impact,
   and rollback state.

Rollback automatically only when the user explicitly authorized it or a bounded incident instruction
already included rollback authority.
