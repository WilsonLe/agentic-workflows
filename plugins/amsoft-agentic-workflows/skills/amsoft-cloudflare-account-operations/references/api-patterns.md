# Cloudflare API patterns

## Paths

Pass paths relative to `https://api.cloudflare.com/client/v4`, beginning with `/`.

Examples:

- `/accounts/{account_id}`
- `/zones`
- `/zones/{zone_id}/dns_records`
- `/accounts/{account_id}/workers/scripts`

Do not place `?query=params` in `path`; use the `query` object.

## Responses

Cloudflare v4 responses commonly include:

- `success`
- `errors`
- `messages`
- `result`
- `result_info` for pagination

Treat HTTP errors and `success: false` as failures. Preserve Cloudflare error codes and messages in the report.

## Pagination

Use the endpoint's documented pagination parameters. For page-based endpoints, advance `page` until `total_pages` or until a page returns fewer than `per_page`. Keep queries narrow to avoid oversized tool results.

## Verification

Useful first calls:

- token: `/accounts/{account_id}/tokens/verify`
- account: `/accounts/{account_id}`
- zones: `/zones` with `account.id={account_id}`

Account API tokens are account-owned. Use the account-scoped token verification endpoint rather than the user-token endpoint.

Always check current Cloudflare API documentation for product-specific endpoint and payload details.
