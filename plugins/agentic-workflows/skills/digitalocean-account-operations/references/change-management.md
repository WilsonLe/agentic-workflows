# DigitalOcean change runbook

Use the [Codex connected-app channel](../../agentic-workflows/references/service-browser-operations.md).
Verify connected identity and the exact target through read-only tools. Missing
connections, operations, or permissions remain blockers; recover through Codex
without local-token or dashboard fallback.

Use this runbook for every mutating connected-tool operation.

## Before

1. Verify account access and resolve the target with read-only tools.
2. Capture current state and rollback-relevant values as nonsecret structured data.
3. Inspect the exact connected tool schema and provider instructions.
4. Classify impact as low, medium, or high. Treat deletion, traffic, credentials, firewall
   exposure, data, rebuild, resize, migration, failover, cluster or database lifecycle, and
   account-wide behavior as high impact.
5. Present the exact nonsecret tool operation, target identifiers, expected effect, cost implications,
   validation, and rollback.
6. Match the exact change to the originating request or existing approval. Continue when covered; ask only for missing authority or a material unresolved decision. Apply [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).

## Execute

1. Run the smallest sufficient connected-tool operation.
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
