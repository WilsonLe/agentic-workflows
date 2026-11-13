# ADR-0019: Cover configured provider credentials and mobile store CLIs

- Status: accepted
- Date: 2026-11-13
- Owner: Project maintainer
- Evidence: Explicit maintainer request to update skills for Apple App Store/TestFlight, Google Play and all present Infisical keys by provider; [issue 123](https://github.com/WilsonLe/agentic-workflows/issues/123)
- Supersedes: 0018
- Superseded by: none

## Context

ADR-0018 established Infisical custody and named-token CLI operations. The current
vault also contains coherent ASC PEM/ID sets, Google service-account JSON, app
configuration/reviewer backups, Sign in with Apple keys and separate Polar token
purposes. Thirty present entries span eight providers; four provider folders are
empty. Single-line-token guidance and five provider entrypoints do not describe
these consumers or mobile-store distribution outcomes.

## Decision

Retain ADR-0018's complete custody, channel, bootstrap, concealed delivery,
authority, worktree, runtime, transfer, verification and failure contracts. Extend
the existing Infisical skill with bounded names/presence/schema discovery and
typed credential delivery. Its conditional reference owns stored aliases and
consumer mapping; the shared provider contract remains the sole channel owner.
Discovery must distinguish empty, denied, unvisited and bounded scope and return
no values. A snapshot is not a persistent registry or proof of future access.

Add provider skills for Apple, Google Play, explicitly selected GitHub integration
tokens, Polar and Resend. Existing Supabase/Vercel and OpenRouter runtime owners
remain. Empty folders do not require placeholder skills or credential creation.
Each present key maps to an intended consumer or precise unsupported capability;
configuration backups and runtime keys are not account-operator substitutes.

Select community-maintained `asc` for Apple and project-pinned Fastlane for Google
Play where no single official management CLI provides these workflows. This is
the limited change to ADR-0018's official-CLI preference; it does not enable
arbitrary clients, connectors, raw account HTTP/SDK fallback or cached logins.
Use exact coherent credential sets in minimal captured child environments, with
private task-owned files only for supported consumers that require them. Signing
assets, ASC authentication and Sign in with Apple keys remain separate.

Provider skills own target validation, actual effects and readback. Explicitly
resolve Apple processing/group distribution/beta review/App Review/public release
and Google signing/package/version/track/edit/commit/review/rollout. Account access,
validation and staging are distinct evidence. Stored configuration and historical
authority fields cannot authorize publication, notifications or broader scopes.
Git/GitHub repository delivery retains existing authentication unless the user
explicitly selects the stored integration token for that delivery.

## Alternatives

Bulk exports/run injection would deliver unrelated provider/runtime credentials.
A generic account client or new credential registry duplicates existing owners.
Adding skills for empty folders creates unsupported capability promises. Treating
PEM/JSON/signing inputs as generic API tokens loses format and purpose boundaries.
Using only Apple's upload tooling omits supported account/TestFlight management;
gcloud alone does not publish Play releases. Importing upstream skill packs or
persisting new logins is unnecessary for these focused provider instructions.

## Consequences

The catalog grows from 59 to 64 skills, generated through existing metadata and
package tools. Current aliases are discoverable without values or app/account
identifiers. CLI/version gaps, app-specific signing keys and limited sending/runtime
credentials can block specific effects; the suite reports them without escalation.
Reviewers must check auth precedence and effectful defaults, including remote edit
creation and upload reservations disguised as dry runs.

This change proves instruction/distribution consistency, not live account rights,
release success or future agent adherence. It neither rotates credentials nor
deploys apps, sends email, merges/releases the plugin or changes its active install.
Rollback is source revert and verified regeneration; provider state is unchanged.

## Revisit

Revisit provider mappings when keys, client auth inputs or operation coverage
change. Reevaluate the selected community CLI if upstream maintenance, security,
credential isolation or store compatibility becomes inadequate. Use a replacement
decision for custody/channel changes rather than silently adding fallback clients.
