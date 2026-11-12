# Cloudflare change runbook

Use the [Infisical-backed CLI channel](../../agentic-workflows/references/service-browser-operations.md).
Obtain the required token from Infisical and verify provider identity and exact
target through read-only CLI commands. Missing tokens, commands or permissions
block dependent work; do not switch to connectors or cached login.

Use this runbook for every mutating CLI operation.

## Before

1. Verify the authenticated account and intended zone/resource.
2. Resolve the target by listing or reading it. Never guess an identifier.
3. Read the current state and retain the fields needed for rollback.
4. Inspect the CLI command help and applicable provider instructions.
5. Classify impact:
   - low: isolated non-production resource;
   - medium: production setting with bounded effect and simple rollback;
   - high: traffic, security, credentials, deletion, broad purge, or account-wide behavior.
6. State the exact tool operation and nonsecret input, expected effect, validation, and rollback.
7. Match the exact change to the originating request or existing approval. Continue when covered; ask only for missing authority or a material unresolved decision. Apply [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).

## Execute

1. Invoke the supported CLI command with the smallest sufficient input.
2. Keep provider authentication and application secrets out of arguments/output.
3. Stop if Cloudflare returns `success: false`, an HTTP error, or an unexpected resource.
4. Do not retry a write automatically unless the endpoint is documented as idempotent and the previous outcome is known.

## Verify

1. Read the changed resource.
2. Compare expected and observed values.
3. Test the affected behavior when possible.
4. Report method, target ID, result, verification evidence, and rollback status.

For a failed validation, roll back only when the user approved automatic rollback or a live
incident clearly included rollback authorization.
