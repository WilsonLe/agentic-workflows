# Provider inventory and credential mappings

Use for configured-provider discovery, stored aliases and "all existing keys".
This reference owns nonsecret discovery/mapping; the
[shared provider contract](../../agentic-workflows/references/service-browser-operations.md)
owns channels, and provider skills own effects. Names below were observed on
2026-11-13; rediscover the selected vault rather than treating this snapshot as
complete/current. Keep account/app IDs and private configuration outside evidence.

## Discovery

1. Verify domain/profile/organization and list project/environment metadata with
   the installed CLI. Resolve task scope before reading secrets; never choose the
   first project or default `dev`. Account-wide coverage needs every authorized
   project/environment; label a narrower result.
2. List folders at resolved paths with `secrets-manager folders get -o json`.
   Traverse the authorized provider subtree with an explicit bound and account for
   every child, including per-app folders.
3. CLI 0.45.6 has no names-only secret listing. Inside the captured subprocess, use
   `secrets-manager secrets get -o json --recursive=false --include-imports=false
   --secret-overriding=false --expand=false` with explicit scope/path. Project only
   `secretKey`, presence and necessary type/schema status before tool output.
   After success/schema validation, JSON `null` or an empty array means no local
   shared keys. Failure/denial means unknown. Never return unfiltered JSON,
   comments, values or raw exception text.
4. Keep exact path/name pairs and classify consumers. Report visited/empty/denied/
   unvisited paths, bounds and environment. Discovery grants no provider operation,
   rotation or deployment. Delivery returns to exact named reads, without recursion.

The snapshot had 30 present keys in eight populated providers and four empty
folders. All 12 are accounted for below; rediscovery may change that inventory.

| Folder under `/providers` | Observed keys | Consumer and limits |
| --- | --- | --- |
| `apple` | 20 entries in [Apple credentials](../../apple-app-store/references/credentials.md) | Separate ASC, Sign in with Apple, release/signing metadata, reviewer and runtime data; `apple-app-store`. |
| `google-play` | `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`, `GOOGLE_PLAY_ACCOUNT_CONFIG_JSON` | Fastlane credentials and account/signing selectors; `google-play`. Per-package signing inputs were absent. |
| `github` | `VULCAN_GITHUB_TOKEN` | `GH_TOKEN` for the intended host/repository under `github-account-operations`; the name proves no scope. |
| `openrouter` | `OpenRouter` | `OPENROUTER_API_KEY` for [transcription](../../speech-to-text/references/openrouter.md) with source/upload/cost authority. No account-management CLI established. |
| `polar` | `HABBY_POLAR_CLI_TOKEN`, `HABBY_POLAR_PRODUCTION_RUNTIME_TOKEN`, `HABBY_POLAR_SANDBOX_ACCESS_TOKEN` | `POLAR_ACCESS_TOKEN` with explicit purpose/environment under `polar-account-operations`; no runtime/sandbox operator fallback. |
| `resend` | `HABBY_RESEND_SENDING_API_KEY` | `RESEND_API_KEY` under `resend-account-operations`; sending access is not account administration. |
| `supabase` | `AMSOFT_SUPABASE_API_KEY` | `SUPABASE_ACCESS_TOKEN` under `supabase-cli`; observed management PAT. Revalidate type/project; never substitute an app key. |
| `vercel` | `AMSOFT_VERCEL_API_KEY` | `VERCEL_TOKEN` under `vercel-account-operations`; verify team/project independently. |
| `cloudflare` | Empty | Existing `cloudflare-account-operations`; resolve a named key before remote work. |
| `digitalocean` | Empty | Existing `digitalocean-account-operations`; resolve a named key before remote work. |
| `posthog` | Empty | Shared `posthog-cli` mapping requires a personal API key; Apple-folder backups do not establish operator access. |
| `railway` | Empty | Existing `railway-account-operations`; choose account/project token type when available. |

Do not rename, relocate, create or export keys to match CLI variable names. New
providers/unmapped keys need a verified consumer/type/target mapping before use.
An unsupported capability or missing input is an explicit gap, not success.
