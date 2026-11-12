# ADR-0015: Support Codex only and use the connected Vercel app

- Status: superseded
- Date: 2026-11-11
- Owner: Project maintainer
- Evidence: Explicit maintainer request to remove Vercel .cli guidance, always use the Vercel plugin/connected app through Codex, and simplify the repository to Codex only; [issue 110](https://github.com/WilsonLe/agentic-workflows/issues/110)
- Supersedes: 0006, 0011, 0014
- Superseded by: 0018

## Context

The suite maintained a Codex source package plus Claude Code and OpenCode
transformations, manifests, installation instructions and smoke dependencies.
Vercel account guidance required a per-project CLI credential store with special
OAuth-copy handling, despite Codex exposing connected Vercel operations. The
maintainer explicitly chose one host and the connected Vercel channel.

## Decision

Support Codex only across catalog declarations, instructions, delegation and
repository delivery. Retain the existing maintained suite and generator. Build a
complete Codex package and marketplace outside the checkout without transformations;
verify and publish that tree through the existing main-to-dist pipeline. Codex
continues installing from the source marketplace on main. Remove alternate-host
manifests, adapters, install guidance and smoke requirements.

Delegation remains an instruction-only skill using native Codex controls, saved
configuration and isolated worktrees for new independent Git sessions. Keep the
existing title hook and opt-in configuration responsibilities. No new adapter,
launcher or coordination schema is introduced.

Always use the Vercel plugin/connected app through Codex for Vercel remote
operations. Codex owns authentication. Verify connected identity and exact target,
execute authorized tool operations and read back results. Recover missing
connections through Codex; unavailable operations or permissions remain blockers.
No CLI, raw HTTP or dashboard service fallback applies. Exclude Vercel credentials
from local setup and worktree copies; leave existing stores untouched.

## Alternatives

Retaining alternate-host bundles preserves more consumers but carries generator,
validator and instruction complexity the maintainer has explicitly retired.
Keeping Vercel CLI as a fallback preserves local authentication and rotating-session
complexity and contradicts the selected single channel. A new Vercel adapter would
duplicate capabilities already exposed by the connected app.

## Consequences

The next verified distribution replaces the old generated host trees with the
complete Codex tree. Historical commits, ADR rationale, upstream source citations
and licenses remain available; they do not advertise current host support. Remaining
provider workflows retain their existing authenticated clients and credential contracts.
Generic project data migration and schema-compatibility safeguards remain in force.

Static package checks prove tree integrity, not agent adherence or live Vercel
permissions. Fresh Codex tasks and real connected-app operation readbacks supply
those separate observations. This change does not activate installed updates,
delete credentials or authorize deployment to a provider.

## Revisit

Reconsider only on an explicit maintainer request for another host or channel with
a concrete consumer need and verifiable capability/authority contracts. Recover a
bad release by reverting source on main and verifying the forward publication.

[ADR-0017](0017-use-codex-connected-apps-and-retire-project-cli-credentials.md) extends
the connected-app channel to all remote providers and retires the remaining-client
authentication guidance described in this record. The Codex-only host, Vercel
channel, delegation, and distribution choices remain in force.

On 2026-11-12, the maintainer explicitly selected Infisical-backed CLI tokens.
[ADR-0018](0018-use-infisical-backed-tokens-for-provider-cli-operations.md) supersedes
this decision, preserving its historical rationale and the inherited Codex-only,
preferences-only transfer and no-credential-copy boundaries.
