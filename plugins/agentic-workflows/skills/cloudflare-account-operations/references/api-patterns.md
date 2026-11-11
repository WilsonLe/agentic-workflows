# Cloudflare connected tool patterns

Follow [the shared provider contract](../../agentic-workflows/references/service-browser-operations.md)
and load the Cloudflare plugin's applicable instructions before tool use.
Discover actual tool inputs and result schemas; do not invent endpoints or tool
names from a CLI/API runbook. Verify account and zone IDs through read-only tools.

Use narrow filters and documented pagination. An empty page is not proof of no
resources unless pagination is complete. Treat tool errors, explicit failure
results, and unexpected targets as failures. Preserve sanitized provider error
codes while omitting authorization data and private records.

For writes, use the exposed tool's smallest supported input and exact target;
read back saved state and verify affected behavior. If that capability is absent,
report it rather than creating an API client or requesting a token. Keep logs
bounded and sanitized; never dump secret values or raw headers.
