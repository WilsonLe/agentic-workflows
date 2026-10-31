# ADR-0004: Distribute Codex defaults as an opt-in config-transfer asset

- Status: accepted
- Date: 2026-10-31
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User request for portable full-access plugin configuration and routine design authority; [issue 63](https://github.com/WilsonLe/agentic-workflows/issues/63)
- Supersedes: none
- Superseded by: none

## Context

Codex user defaults do not inherit a config.toml merely because it is inside an
installed plugin. The suite already owns onboarding and encrypted configuration
transfer, but the transfer allowlist contains workflow preferences and supported
provider credentials, not Codex configuration. The user requests a portable preset
matching their local full-access settings without changing task authorization.

## Decision

Keep the preset, activation guidance and helper within the existing Codex-only
config-transfer skill. The router and onboarding link that owner. Installation
ships the asset without applying it; preview/apply/restore are explicit local
operations against the intended client's Codex home. Select sandbox_mode alone,
removing a conflicting default_permissions selector while retaining definitions.

Use pinned tomlkit to preserve comments and unrelated TOML tables. Activation
backs up original bytes privately and atomically replaces only config.toml.
Restore verifies the applied digest before replacing newer state. The helper owns
only local TOML activation; encrypted provider transfer and its schema stay unchanged.
Its atomic writer handles arbitrary existing config modes rather than reuse the
credential writer, which requires credential-specific paths and modes. Neither
writer depends on the other. Specific app/tool restrictions remain; named servers
or an explicit all-configured-servers option change server defaults only.

## Alternatives

An install hook applying global settings would misrepresent plugin inheritance and
change permissions without explicit activation. Replacing the whole user config
would discard authentication references and preferences. Regex editing cannot
safely preserve TOML table ownership. Putting Codex config in encrypted transfer
would broaden the credential payload contract unnecessarily. A new setup skill
would duplicate the existing configuration owner and navigation.

## Consequences

The plugin is portable without hardcoded identities or cache versions. Each
machine needs explicit activation. Backups can contain secrets, remain local, and
are excluded from Git and encrypted transfer. tomlkit adds a pinned dependency.
Client parsing and effective permission readback remain separate from actual
tool execution; managed policy, OS consent and task-specific authority still apply.
Windows ACL privacy depends on the user's private Codex home. The helper lock
coordinates helper writers only; close other configuration editors during use.

## Revisit

Revisit if Codex supplies a portable plugin-owned user-configuration activation
API, removes legacy sandbox_mode, or introduces a supported global MCP default
that removes the need for explicit local server selection. Preserve restore and
task-authorization boundaries through any replacement.
