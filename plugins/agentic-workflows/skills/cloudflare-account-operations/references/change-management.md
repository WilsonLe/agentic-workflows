# Cloudflare change runbook

Use the [Codex connected-app channel](../../agentic-workflows/references/service-browser-operations.md).
Verify connected identity and the exact target through read-only tools. Missing
connections, operations, or permissions remain blockers; recover through Codex
without local-token or dashboard fallback.

Use this runbook for every mutating connected-tool operation.

## Before

1. Verify the connected account and intended zone/resource.
2. Resolve the target by listing or reading it. Never guess an identifier.
3. Read the current state and retain the fields needed for rollback.
4. Inspect the connected tool schema and applicable provider instructions.
5. Classify impact:
   - low: isolated non-production resource;
   - medium: production setting with bounded effect and simple rollback;
   - high: traffic, security, credentials, deletion, broad purge, or account-wide behavior.
6. State the exact tool operation and nonsecret input, expected effect, validation, and rollback.
7. Match the exact change to the originating request or existing approval. Continue when covered; ask only for missing authority or a material unresolved decision. Apply [task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).

## Execute

1. Invoke the supported connected tool with the smallest sufficient input.
2. Keep connector authentication and application secrets out of arguments/output.
3. Stop if Cloudflare returns `success: false`, an HTTP error, or an unexpected resource.
4. Do not retry a write automatically unless the endpoint is documented as idempotent and the previous outcome is known.

## Verify

1. Read the changed resource.
2. Compare expected and observed values.
3. Test the affected behavior when possible.
4. Report method, target ID, result, verification evidence, and rollback status.

For a failed validation, roll back only when the user approved automatic rollback or a live
incident clearly included rollback authorization.
