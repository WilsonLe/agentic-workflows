---
name: polar-account-operations
description: Use whenever inspecting or managing Polar organizations, products, checkout links, subscriptions, orders, benefits or billing incidents. Use the polar CLI with credentials obtained from Infisical, select sandbox or production explicitly, preserve operator versus runtime token purpose, and read back authorized effects.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Service CLI and Infisical access** — Install polar and Infisical CLI; resolve operator versus runtime purpose and sandbox versus production. Deliver the selected POLAR_ACCESS_TOKEN from Infisical with explicit POLAR_ENVIRONMENT and verify organization/resource IDs without cached sessions.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Polar account operations

Use `polar` under the [shared provider contract](../agentic-workflows/references/service-browser-operations.md)
and load [Infisical Account Operations](../infisical-account-operations/SKILL.md).
Resolve organization, environment, resource IDs and effect. Inspect installed
version/help and token/environment precedence; fetch only the selected key in
the captured bridge and map it to `POLAR_ACCESS_TOKEN`:

| Observed key in `/providers/polar` | Purpose |
| --- | --- |
| `HABBY_POLAR_CLI_TOKEN` | Operator candidate; verify organization, environment and scopes. |
| `HABBY_POLAR_PRODUCTION_RUNTIME_TOKEN` | Selected production runtime integration; never automatic operator fallback. |
| `HABBY_POLAR_SANDBOX_ACCESS_TOKEN` | Selected sandbox organization; never seal into production runtime. |

Set `POLAR_ENVIRONMENT=sandbox` or `production` explicitly. Exclude cached-session
selectors, unrelated tokens and `POLAR_API_URL`/endpoint overrides unless the task
selects/verifies that endpoint. Infisical `prod` does not select Polar production.
Do not log in/create tokens as preflight. Installed 3.0.0 supports the environment
token for `polar auth whoami` and resources; verify current behavior.

Use token-authenticated read-only scope checks, such as `polar organizations list
--fields id,slug,name --json`, with pagination. Match organization/resource IDs and
environment. A denial never authorizes retrying with runtime/production/broader
tokens, a connector or cached login. A key name or old checkout is not identity.

Execute the smallest supported resource command with explicit IDs. Project only
required IDs/status/counts; keep customer/order data and checkout capability URLs
private. Paid tests, checkout creation, cancellation, refunds, anonymization and
deletion need their actual authority, including sandbox effects. Read back saved
state and relevant webhook/app behavior; distinguish payment, webhook delivery
and entitlement. Wait for asynchronous completion and inspect unknown outcomes
before retry; no duplicate refund/checkout or automatic inverse. Missing scopes/
commands remain capability gaps.

Sources checked 2026-11-13: installed 3.0.0 help,
[Polar CLI](https://github.com/polarsource/polar/tree/main/clients/packages/cli),
[auth resolution](https://github.com/polarsource/polar/blob/main/clients/packages/cli/src/services/auth.ts).
