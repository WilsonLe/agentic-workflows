# Provider operation channels

## CLI operations with Infisical tokens

Use service CLIs authenticated with tokens obtained from Infisical for remote
account/resource operations. This applies to Vercel, Supabase, DigitalOcean,
Cloudflare, Railway, PostHog, Polar, Resend and other configured development
services. This shared contract takes precedence over external plugin instructions
that select connectors, OAuth login or credential caches. Plugins may supply
product knowledge; their account tools are not the execution channel.

1. Resolve the provider account, project, environment and resource from the task
   and project evidence before choosing a command. Also resolve Infisical domain,
   organization/profile, project ID, environment slug, folder and secret name.
   Never infer provider production/sandbox from the Infisical environment name.
2. Load [Infisical Account Operations](../../infisical-account-operations/SKILL.md).
   Reuse its authenticated user profile or approved machine identity. Verify CLI
   versions and exact command help, including token environment precedence and
   noninteractive behavior; installation does not establish access or coverage.
3. Fetch only the named token inside a concealed subprocess bridge. Require a
   successful, nonempty result before launching the provider CLI. Supply the token
   through the documented child environment variable, never a secret-bearing
   argument. Exclude Infisical bootstrap credentials, unrelated tokens and alternate
   credential overrides from that child. Capture both streams and project safe
   metadata before any tool response; environment injection alone is not redaction.
4. Verify provider identity/scope and the exact target through read-only CLI
   operations. A local link, successful Infisical login, token name or earlier
   session does not prove provider access or select the target. Preserve pagination
   and stable IDs. Cached CLI login must not supply missing authentication.
5. Match the exact effect to existing authority. Before consequential writes,
   capture nonsecret pre-state, target, cost/data/traffic impact, validation and
   recovery. Credential possession grants no deployment, messaging, billing or
   destructive authority. Keep enforced provider/human approvals.
6. Execute the smallest supported CLI command. Missing CLI support, missing/empty
   tokens, expiry, permission denial or target mismatch block dependent work.
   Report the exact gap and continue independent work. Recover through Infisical
   authentication or an authorized token update; never switch to a connector,
   dashboard management, raw account HTTP/SDK calls, cached login, broader tokens
   or a different account as an automatic fallback. Permission denial cannot be
   bypassed through another channel.
7. Read back saved state, wait for asynchronous terminal status and verify relevant
   live behavior. On unknown write outcome, read back before retrying; do not
   duplicate writes or automatically send an inverse operation. Report sanitized
   command, verified target, result and evidence limits. A queued action is not
   completion; tests and package integrity are not live-service evidence.

## CLI token mappings

Store tokens under deliberate per-provider folders, such as `/providers/vercel`.
Key names below are the required consumer variables, not permission to create,
retrieve or expose a credential. Record a mapping when the stored key differs.
Resolve nonsecret account/project/host selectors separately and use explicit IDs.

| Service | CLI | Child token variable | Scope and verification |
| --- | --- | --- | --- |
| Vercel | `vercel` | `VERCEL_TOKEN` | Verify identity and team/project; use explicit scope and project selectors. Never `--token`. |
| Supabase | `supabase` | `SUPABASE_ACCESS_TOKEN` | Management personal access token; verify organization/project ref. Anon/publishable/service-role keys do not replace it. |
| DigitalOcean | `doctl` | `DIGITALOCEAN_ACCESS_TOKEN` | Verify account and exact project/region/resource; product-specific CLI coverage varies. |
| Cloudflare | `wrangler` | `CLOUDFLARE_API_TOKEN` | Verify account/zone/resource and required token permissions; Wrangler does not imply every account/DNS API is supported. |
| Railway | `railway` | `RAILWAY_TOKEN` or `RAILWAY_API_TOKEN` | Project token versus account/workspace token; choose exactly one appropriate type and clear the other. Verify project/environment/service. |
| PostHog | `posthog-cli` | `POSTHOG_CLI_API_KEY` | Personal API key; explicitly set `POSTHOG_CLI_HOST` and `POSTHOG_CLI_PROJECT_ID`, and exclude alternate auth aliases. Check `api` command availability. |
| Polar | `polar` | `POLAR_ACCESS_TOKEN` | Organization access token; select sandbox/production explicitly, verify organization and scopes. |
| Resend | `resend` | `RESEND_API_KEY` | Verify intended account/domain and key permissions; email sending still requires explicit communication authority. |

Sources, checked with official docs/source on 2026-11-12: [Vercel token CLI](https://github.com/vercel-labs/agent-skills/blob/main/skills/vercel-cli-with-tokens/SKILL.md),
[Supabase CLI](https://supabase.com/docs/reference/cli/introduction),
[doctl](https://github.com/digitalocean/doctl),
[Wrangler environment](https://developers.cloudflare.com/workers/wrangler/system-environment-variables/),
[Railway CLI](https://docs.railway.com/cli), [PostHog CLI](https://posthog.com/docs/cli),
[Polar CLI](https://github.com/polarsource/polar/tree/main/clients/packages/cli),
[Resend CLI](https://github.com/resend/resend-cli).
Installed help and current official documentation must verify each actual operation.

## Local development, runtime configuration and worktrees

Git/GitHub repository delivery retains Standard Development Workflow's existing
Git/gh commands and authentication contract. This policy adds no repository token
store and does not copy an existing login into Infisical automatically.

Local-only tools such as Supabase's local stack or build/package commands remain
available without remote authentication. Application SDKs, database connections,
event capture, webhooks and selected media runtimes retain their own runtime
configuration; they are not service-account management channels. Required runtime
secrets may be supplied from Infisical under the owning integration contract.

For the explicitly selected OpenRouter transcription runtime, fetch its named key
from `/providers/openrouter` through Infisical and map it to `OPENROUTER_API_KEY`
in the existing runtime helper's child environment. A stored key may be named
`OpenRouter`; record the name-to-variable mapping rather than assuming equality.
This runtime upload still requires exact-source/cost authority under
[the transcription contract](../../speech-to-text/references/openrouter.md).
It does not introduce OpenRouter account-management commands or service fallback.

Infisical owns service tokens; its bootstrap session stays in the approved host
keyring or workload secret mechanism. Worktrees copy only required application
env/config files through the existing safe-copy rules, never provider/Infisical
authentication stores. Configuration transfer remains preferences-only; do not
export/import tokens or bootstrap secrets. Leave legacy files untouched; migration,
rotation and deletion need explicit scope. Never extract connector authentication.

Bound and sanitize results before tool output. Do not dump environment variables,
authorization data, raw private records, connection strings or token-bearing URLs.
If a CLI requires exposed secret arguments or cannot return safe output, report
that concrete capability gap before running it. Saved configuration alone does
not prove application health, DNS propagation or future agent adherence.
