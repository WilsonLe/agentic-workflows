# Cloudflare CLI command patterns

Follow the [shared CLI-token contract](../../agentic-workflows/references/service-browser-operations.md).
Fetch `CLOUDFLARE_API_TOKEN` from Infisical and inspect installed Wrangler help for
the exact product/action. Verify account, zone and resource IDs through supported
read commands. Wrangler covers selected products; do not translate an arbitrary
REST endpoint into an invented CLI command or silently use an HTTP client.

Use narrow filters and documented pagination. An empty page proves nothing until
pagination is complete. Capture output and project nonsecret metadata before it
reaches the agent. Preserve sanitized error categories, omitting authorization
data and private records. Verify identity even when a token was explicitly supplied.

Use the smallest authorized CLI command, then read back state and affected behavior.
Missing DNS/account/product coverage is a concrete capability blocker; do not use
a connector, dashboard, broader token or raw account API as fallback.
