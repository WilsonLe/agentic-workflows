---
name: resend-account-operations
description: Use whenever inspecting or managing Resend email, domains, delivery, webhooks or account resources, or sending an explicitly requested email through Resend. Use the resend CLI with credentials obtained from Infisical, respect sending-only versus full-access scopes, and distinguish accepted sends from delivery.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Service CLI and Infisical access** — Install resend and Infisical CLI; resolve the selected sending-only or full-access key and exact domain. Deliver RESEND_API_KEY from Infisical in a concealed child environment, respect read/management scope limits and require explicit communication authority for sends.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Resend account operations

Use `resend` under the [shared provider contract](../agentic-workflows/references/service-browser-operations.md)
and load [Infisical Account Operations](../infisical-account-operations/SKILL.md).
Resolve account, domain, resource and effect. Observed `/providers/resend` key
`HABBY_RESEND_SENDING_API_KEY` maps to `RESEND_API_KEY`; sending scope does not prove
account/domain administration. Fetch only the selected key in the captured bridge;
never persist login, pass `--api-key`, select a cached profile or replace it with
full access automatically.

Inspect version/help and environment precedence. Exclude `RESEND_PROFILE` and
alternate auth/config/endpoint overrides; isolate nonsecret config when supported.
Capture/project both streams, including diagnostics: installed 2.28.1 `resend
whoami` is local-only and includes a masked key. It proves no remote identity or
permissions; do not return raw auth output.

For administrative work, verify exact account/domain through supported read-only
commands and stable IDs. Sending-only keys may forbid those reads; report the
scope/identity gap without sending a test email, escalating or switching channels.
For an explicitly requested send through an established domain-specific integration,
verify the approved source mapping and exact sender/domain/recipients/content.
Block if that scope cannot be established. A denied admin read does not authorize
replacing credentials or invalidate a separately established sending scope.

Send only with explicit communication authority, including test inbox/attachments.
Use supported file/stdin for private contents and idempotency where available;
keep message contents out of argv/output. A confirmation flag can express existing
authority. Do not send during inventory, setup inspection or a general deploy.

Read back message ID and accepted/queued/delivered/bounced state when authorized
CLI scope permits. Sending-only keys may not allow delivery reads; disclose this
instead of claiming delivery. After unknown acceptance, inspect the same ID/
idempotency record before retry; if unavailable, report unknown without duplicate
send. Keep recipients/bodies, keys, webhook secrets and private logs out of evidence.
No connector, cached-login or raw API fallback.

Sources checked 2026-11-13: installed 2.28.1 help,
[official CLI](https://github.com/resend/resend-cli),
[key permissions](https://resend.com/changelog/new-api-key-permissions).
