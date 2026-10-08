# Excalidraw errors and rate limits

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

The documented statuses are `200`, `400`, `401`, `403`, `404`, `429`, and
`500`. Error bodies normally include `statusCode`, `error`, and `message`.
Sanitize messages and never output request headers.

The documented limit is 600 requests per minute per IP. Monitor:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

Safe GET requests may use bounded backoff for `429` or transport failure.
Writes must not be retried automatically because no idempotency contract is
documented. Bound response bodies and timeouts; large scene content and embedded
files can be substantial.

Official references:

- https://plus.excalidraw.com/docs/api/error-handling
- https://plus.excalidraw.com/docs/api/rate-limiting
- https://plus.excalidraw.com/docs/api/pagination
