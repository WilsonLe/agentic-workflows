# Cloudflare change runbook

Use this runbook for every non-GET request.

## Before

1. Verify the token and configured account.
2. Resolve the target by listing or reading it. Never guess an identifier.
3. Read the current state and retain the fields needed for rollback.
4. Check the current Cloudflare API documentation for the endpoint and payload.
5. Classify impact:
   - low: isolated non-production resource;
   - medium: production setting with bounded effect and simple rollback;
   - high: traffic, security, credentials, deletion, broad purge, or account-wide behavior.
6. State the exact secret-free CLI command, method, path, body, expected effect, validation, and rollback.
7. Obtain explicit user approval for that exact change.

## Execute

1. Run the approved curl or Wrangler command with the smallest sufficient body or flags.
2. Keep `CLOUDFLARE_API_TOKEN` out of literal arguments and output.
3. Stop if Cloudflare returns `success: false`, an HTTP error, or an unexpected resource.
4. Do not retry a write automatically unless the endpoint is documented as idempotent and the previous outcome is known.

## Verify

1. Read the changed resource.
2. Compare expected and observed values.
3. Test the affected behavior when possible.
4. Report method, target ID, result, verification evidence, and rollback status.

For a failed validation, roll back only when the user approved automatic rollback or a live
incident clearly included rollback authorization.
