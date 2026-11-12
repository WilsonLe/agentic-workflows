# Cloudflare CLI command patterns

Follow the [shared CLI-token contract](../../agentic-workflows/references/service-browser-operations.md).
Fetch `CLOUDFLARE_API_TOKEN` from Infisical. Use the official `cf` CLI for account
and resource operations: zones, DNS, storage, security and other supported products.
Use `cf cli search` with a quoted task to discover candidates, then `cf schema`
and exact command help to inspect inputs/output before execution. Never invent
flags or translate an arbitrary API endpoint into an assumed command.

For example, `cf zones list --name example.com` resolves a zone and
`cf dns records list --zone <zone-id>` reads its records. Follow documented
pagination (`--page`/`--per-page` for DNS records); an empty page alone proves
nothing. Verify exact account/zone/resource IDs and required token permissions.
A nonsecret `--dry-run` may validate a request shape without sending it, but
cannot establish authentication, permissions or the resulting service state.

Existing Wrangler-configured projects keep their repository-required Wrangler
project commands. `cf` resource operations work alongside them without migration;
do not run `cf migrate` or rewrite configuration for an account-management task.
Supply the same token only in each selected CLI's child environment.

Capture both output streams and project nonsecret metadata before tool output.
Token-bearing bodies, debug output and dry-run payloads need the same concealment
rules as ordinary commands. Use the smallest authorized command, then read back
saved state and relevant live behavior. Missing commands or permissions block the
operation without connector, dashboard, broader-token or raw-account-API fallback.

Official sources: [Cloudflare CLI for agents](https://developers.cloudflare.com/cf/agents/),
[resource operations](https://developers.cloudflare.com/cf/get-started/resources/),
and [token environment](https://developers.cloudflare.com/cf/environment-variables/).
