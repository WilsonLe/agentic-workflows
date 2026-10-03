# Cloudflare CLI and API patterns

## Authentication

Use the bundled protected wrapper for token verification:

```bash
python3 <plugin-root>/scripts/cloudflare_api.py verify
```

The wrapper selects verification by the stored token type and builds authorization
headers internally. Never expand `CLOUDFLARE_API_TOKEN` into `curl --header`:
shell expansion places the value in process arguments. For additional operations,
extend the supported wrapper or use a reviewed non-argv credential channel whose
output is sanitized. Keep token values out of tracing and request-header output.

## Paths

Build URLs under `https://api.cloudflare.com/client/v4`.

Examples:

- `/accounts/{account_id}`
- `/zones`
- `/zones/{zone_id}/dns_records`
- `/accounts/{account_id}/workers/scripts`

Use `curl --get --data-urlencode` for query parameters when values require encoding.

## Responses

Cloudflare v4 responses commonly include:

- `success`
- `errors`
- `messages`
- `result`
- `result_info` for pagination

Treat HTTP errors and `success: false` as failures. Preserve Cloudflare error codes and messages in the report.

## Pagination

Use the endpoint's documented pagination parameters. For page-based endpoints, advance `page` until
`total_pages` or until a page returns fewer than `per_page`. Keep queries narrow and preserve
`result_info`.

## Verification

Useful read-only calls include token verification, `/accounts/{account_id}`, and `/zones` filtered
to the intended account. Confirm the correct verification endpoint in current Cloudflare
documentation for the supplied token type.

## Writes

For an approved write, use `--request`, the exact endpoint, and the smallest JSON body. Prefer
`--data-binary @<temporary-payload-file>` for non-trivial payloads so quoting is inspectable. Ensure
the payload contains no credentials and remove the temporary file after verification.

## Debugging

- Add `--fail-with-body --show-error` to surface HTTP failures.
- Use `--write-out` for status codes without printing request headers.
- Never use `curl --verbose` when its output might expose headers unless the output is captured and
  sanitized before review.
- For Wrangler, use `--help` first. If needed, use `WRANGLER_LOG=debug` with
  `WRANGLER_LOG_SANITIZE=true`.

Always check current Cloudflare API documentation for product-specific endpoint and payload details.
