# Provider operation channels

## CLI operations with Infisical tokens

Use service CLIs authenticated with tokens obtained from Infisical for remote
account/resource operations. This applies to Vercel, Supabase, DigitalOcean,
Cloudflare, Railway, PostHog, Polar, Resend, Apple App Store Connect/TestFlight,
Google Play and explicitly selected Infisical-backed GitHub integrations. This
shared contract takes precedence over external plugin instructions
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
3. Fetch only the named token or coherent credential set inside a concealed
   subprocess bridge. Require a
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

For current provider-folder/key discovery and stored-name aliases, use the
[Infisical inventory owner](../../infisical-account-operations/references/provider-inventory.md).
For PEM, JSON, signing inputs or private reviewer/runtime data, apply its
[typed delivery contract](../../infisical-account-operations/references/secret-operations.md#typed-credentials-and-private-files).
Fetch each required field by exact name; do not bulk-inject a provider folder.
An existing key needs an intended consumer/type/purpose, not automatic use in an
account CLI. Configuration/verification history does not supply task authority.

## CLI token mappings

Store tokens under deliberate per-provider folders, such as `/providers/vercel`.
Key names below are the required consumer variables, not permission to create,
retrieve or expose a credential. Record a mapping when the stored key differs.
Resolve nonsecret account/project/host selectors separately and use explicit IDs.

| Service | CLI | Concealed child input | Scope and verification |
| --- | --- | --- | --- |
| Vercel | `vercel` | `VERCEL_TOKEN` | Verify identity and team/project; use explicit scope and project selectors. Never `--token`. |
| Supabase | `supabase` | `SUPABASE_ACCESS_TOKEN` | Management personal access token; verify organization/project ref. Anon/publishable/service-role keys do not replace it. |
| DigitalOcean | `doctl` | `DIGITALOCEAN_ACCESS_TOKEN` | Verify account and exact project/region/resource; product-specific CLI coverage varies. |
| Cloudflare | `cf`; repo-required Wrangler project commands | `CLOUDFLARE_API_TOKEN` | Verify account/zone/resource and required token permissions; Discover actual `cf` resource schemas; retain existing Wrangler projects without automatic migration. |
| Railway | `railway` | `RAILWAY_TOKEN` or `RAILWAY_API_TOKEN` | Project token versus account/workspace token; choose exactly one appropriate type and clear the other. Verify project/environment/service. |
| PostHog | `posthog-cli` | `POSTHOG_CLI_API_KEY` | Personal API key; explicitly set `POSTHOG_CLI_HOST` and `POSTHOG_CLI_PROJECT_ID`, and exclude alternate auth aliases. Check `api` command availability. |
| Polar | `polar` | `POLAR_ACCESS_TOKEN` | Organization access token; select sandbox/production explicitly, verify organization and scopes. |
| Resend | `resend` | `RESEND_API_KEY` | Verify intended account/domain and key permissions; email sending still requires explicit communication authority. |
| Apple App Store/TestFlight | Community `asc` | `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY` | Coherent selected ASC family; isolate cached profiles/config and verify app/bundle/team. See [Apple](../../apple-app-store/SKILL.md). Sign in with Apple keys are separate. |
| Google Play | Project-pinned Fastlane `supply` | `SUPPLY_JSON_KEY_DATA` or `SUPPLY_JSON_KEY` private file path | Service-account JSON; verify package/track and separate upload-signing inputs. See [Google Play](../../google-play/SKILL.md). |
| Explicitly selected GitHub integration | `gh` | `GH_TOKEN` or host-specific `GH_ENTERPRISE_TOKEN` | Verify host, token actor/type and repository; no implied credential switch for ordinary Git delivery. See [GitHub](../../github-account-operations/SKILL.md). |

Sources, checked with official docs/source on 2026-11-12: [Vercel token CLI](https://github.com/vercel-labs/agent-skills/blob/main/skills/vercel-cli-with-tokens/SKILL.md),
[Supabase CLI](https://supabase.com/docs/reference/cli/introduction),
[doctl](https://github.com/digitalocean/doctl),
[Cloudflare CLI environment](https://developers.cloudflare.com/cf/environment-variables/),
[Railway CLI](https://docs.railway.com/cli), [PostHog CLI](https://posthog.com/docs/cli),
[Polar CLI](https://github.com/polarsource/polar/tree/main/clients/packages/cli),
[Resend CLI](https://github.com/resend/resend-cli).
Installed help and current official documentation must verify each actual operation.
Apple/Google/GitHub additions checked 2026-11-13 against installed help and upstream
sources linked from their provider references. `asc` and Fastlane are maintained
third-party clients; do not label them official Apple/Google CLIs. Polar and Resend
details live in their [Polar](../../polar-account-operations/SKILL.md) and
[Resend](../../resend-account-operations/SKILL.md) entrypoints.

## Local development, runtime configuration and worktrees

Git/GitHub repository delivery retains Standard Development Workflow's existing
Git/gh commands and authentication contract. This policy adds no repository token
store and does not copy an existing login into Infisical automatically.
An explicitly selected stored GitHub integration token follows its provider skill;
its presence alone does not change repository delivery credentials or global auth.

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
