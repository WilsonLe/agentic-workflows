# Apple credential selection and delivery

Resolve `/providers/apple` in the selected vault. Fetch only one coherent ASC key
family; denial does not authorize trying the other. Apply Infisical's
[typed delivery](../../infisical-account-operations/references/secret-operations.md#typed-credentials-and-private-files).
Observed aliases below do not prove current roles, authority or provider access.

| Purpose | Stored names | Consumer |
| --- | --- | --- |
| General App Store Connect | `AMSOFT_APPLE_API_KEY`, `AMSOFT_APPLE_API_KEY_ID`, `AMSOFT_APPLE_API_KEY_ISSUER_ID` | PEM → `ASC_PRIVATE_KEY`; ID → `ASC_KEY_ID`; issuer → `ASC_ISSUER_ID`. |
| TestFlight | `AMSOFT_APPLE_TESTFLIGHT_API_KEY`, `AMSOFT_APPLE_TESTFLIGHT_API_KEY_ID`, `AMSOFT_APPLE_TESTFLIGHT_API_KEY_ISSUER_ID` | Same variables using only this selected family. |
| Profile labels | `AMSOFT_APPLE_API_PROFILE`, `AMSOFT_APPLE_TESTFLIGHT_API_PROFILE` | Comparison metadata; do not select cached auth with `--profile` or `ASC_PROFILE`. |
| Developer team | `AMSOFT_APPLE_TEAM_ID` | Compare task/project/signing team; not the issuer ID. |

For `asc` 6.3.0, use a complete child credential set with `ASC_KEY_TYPE=team` and
`ASC_STRICT_AUTH=1`. Exclude `ASC_PROFILE`, `ASC_BEARER_TOKEN`, alternate private-key
inputs, StoreKit/Ads/web credentials and unrelated auth. Isolate stored auth with
`ASC_BYPASS_KEYCHAIN=1` and an absolute `ASC_CONFIG_PATH` pointing to a task-owned
nonexistent path outside Git. No profile may be selected. Missing/invalid fields
block launch; never log in, export auth, print JWTs or fill from local profiles.
Recheck precedence against installed help/upstream when the version changes.

Capture both streams even for auth diagnostics. Verify the app with
`asc --read-only apps view --id <app-id> --output json` and compare app/bundle ID;
project required fields only. Paginate lists. Local auth status is not network
identity evidence. Keep debug/API logging off and never use `--include-sensitive`.

## Other present entries

| Stored names | Intended consumer and validation |
| --- | --- |
| `AMSOFT_APPLE_HABBY_APP_ID`, `AMSOFT_APPLE_HABBY_BUNDLE_ID` | Compare task, project and remote app; selectors are not credentials. |
| `AMSOFT_APPLE_HABBY_SIGNING_JSON` | Allowlist `profile`, `app_id`, `team_id`, `issuer_id`, `key_id`, `key_sha256` as comparison metadata. This is not a signing private key or provisioning profile; verify actual Xcode signing assets. |
| `AMSOFT_APPLE_HABBY_TESTFLIGHT_CONFIG_JSON` | Allowlist `asc_profile`, `app_id`, `bundle_id`, `team_id`, `group_id`, `tester_ids`, `key_id`, `simulator_id`. Revalidate app/group/key relationships; keep tester IDs private and discard stale simulator assumptions. No invite/notification/review authority comes from this data. |
| `AMSOFT_APPLE_HABBY_APPSTORE_CONFIG_JSON` | Allowlist `app_id`, `team_id`, `bundle_id`, `asc_profile`, `release_type`, `storefront`, `enabled`; saved release mode/enabled flags are not submission/public-release authority. |
| `AMSOFT_APPLE_HABBY_APP_REVIEW_ACCOUNT_JSON` | Deliver only required review-login fields to the authorized review consumer through a protected file/environment; never dump the object or pass a password literally in argv. Stored `authority`, `state`, `verification` are history. If concealed input is unsupported, report the gap. |
| `AMSOFT_APPLE_HABBY_POSTHOG_SDK_ENV`, `AMSOFT_APPLE_HABBY_POSTHOG_VALIDATION_ENV`, `AMSOFT_APPLE_HABBY_POSTHOG_XCCONFIG` | Selected app runtime/build/validation backups: parse internally, allowlist project fields and restore under safe local configuration rules. Do not source text as shell code, put validation credentials in the app or treat backups as PostHog operator access. |
| `HABBY_APPLE_KEY_ID`, `HABBY_APPLE_PRIVATE_KEY` | Sign in with Apple runtime/sealer inputs, confirmed in the app credential register; keep out of ASC/TestFlight auth. Resolve current team, primary App ID/service ID and owning runtime contract. No Sign in with Apple revocation/account-management CLI is established here. |

These tables account for all 20 observed Apple keys. Read the app's current
credential/runbook owner before restoring private application data. Backups prove
neither current signing, reviewer login, runtime health nor consent.

Sources checked 2026-11-13: [upstream asc authentication](https://github.com/rorkai/App-Store-Connect-CLI/blob/main/website/src/content/docs/authentication.mdx)
and installed 6.3.0 help. `asc` is an unofficial Apple API client; inspect current
coverage rather than assume Apple Developer/web-session support.
