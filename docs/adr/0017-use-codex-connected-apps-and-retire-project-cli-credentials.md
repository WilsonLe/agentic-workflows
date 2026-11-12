# ADR-0017: Use Codex connected apps and retire project CLI credentials

- Status: superseded
- Date: 2026-11-11
- Owner: Project maintainer
- Evidence: Explicit maintainer request to use configured Supabase, Cloudflare, and DigitalOcean Codex connectors and remove all expectations of project-local CLI token stores; [issue 115](https://github.com/WilsonLe/agentic-workflows/issues/115)
- Supersedes: 0013, 0016
- Superseded by: 0018

## Context

ADR-0015 selected Codex and its connected Vercel app. ADR-0016 extended that channel
to PostHog and Polar while retaining four providers' custom CLI authentication.
Shared bootstrap still copied account tokens, configuration transfer backed up
provider credentials, and ADR-0013 required an OpenRouter key in each checkout.
The maintainer now chooses connected apps for remote providers and retires the
project-local credential-store concept across the suite.

## Decision

Use the existing shared provider channel contract for all remote account/resource
operations. Codex owns connector authentication. Reuse configured connections,
discover actual plugin tools/instructions, and verify connected identity and exact
target read-only before dependent work. Recover connections through Codex; missing
connections, operations, or permissions remain explicit blockers without local-token,
raw account API/SDK, or dashboard fallback. A named provider skill does not promise
that its connector exists or supports every product. Retain authority, data
minimization, asynchronous completion, readback, and live-behavior checks.

Update existing provider skills, catalog prerequisites, prompts, runbooks, and
shared guidance. Preserve the supabase-cli invocation name for compatibility and
local-only development while routing hosted operations through the app. Other
repository-required local tools and application runtime secrets remain separate.
Worktrees carry only required application env/config files through the existing
safe-copy controls; never copy or inspect agent authentication stores.

Retire provider-token installers/wrappers and the OpenRouter key-copy command from
the suite and catalog. Keep the existing shared private-file primitives needed by
preferences and transcript artifacts, with no project-token exception. Do not
read, migrate, rotate, or delete existing user credentials.

Configuration transfer now exports/imports allowlisted preferences only. Retain
the encrypted envelope and OS-local/portable encryption modes; version the payload
as 2, reject credential-bearing version-1 files before writes, and accept exact
version-1 preference-only files by normalization. Never silently drop/restore tokens
or inspect/decrypt legacy archives manually. Preserve the user's archive and
recover account access through Codex independently. Old importers intentionally
reject version-2 payloads; both hosts need the updated suite.

Keep ADR-0013's explicitly authorized, bounded, source-hash-bound OpenRouter audio
runtime, private receipts, one-submission behavior, and offline recovery. Replace
checkout-key discovery with explicit OPENROUTER_API_KEY runtime environment input.
No Git checkout or key-copy step is required; media subprocesses exclude that key.
A runtime key is never connector authentication or an agent management fallback.

## Alternatives

Merely changing three provider entry points leaves contradictory token paths in
bootstrap, metadata, runbooks, transfer, and transcription. Retaining dormant custom
authentication wrappers invites fallback and maintains another authentication owner.
Deleting local development and runtime integrations would remove useful behavior
beyond the requested account-authentication policy. Silently importing only the
preferences from credential-bearing legacy archives hides a material compatibility
change, so the importer fails explicitly before writes instead.

## Consequences

The suite no longer needs project account-token stores or copies. Railway operations
also require an actual connected capability; this decision does not configure one.
Provider-specific resource verification and application/runtime secret handling
remain necessary. Existing files and archives remain intact; provider-token export
and restoration are intentionally retired, without an automatic migration.

Source checks, synthetic preferences/runtime tests, and portable package checks
establish the maintained contracts, not fresh-agent adherence, installed-plugin
activation, connector permissions, or real provider operations. Rollback is a source
revert and verified regeneration; no account state changes are part of this update.

## Revisit

Reconsider a channel only on an explicit maintainer request with a concrete
unsupported operation and a verifiable authentication/authority contract. Change
runtime authentication or transfer compatibility through their existing owners
and a versioned decision, rather than adding another credential subsystem.

On 2026-11-12, the maintainer explicitly selected Infisical-backed CLI tokens.
[ADR-0018](0018-use-infisical-backed-tokens-for-provider-cli-operations.md) supersedes
this decision, preserving its historical rationale and the inherited Codex-only,
preferences-only transfer and no-credential-copy boundaries.
