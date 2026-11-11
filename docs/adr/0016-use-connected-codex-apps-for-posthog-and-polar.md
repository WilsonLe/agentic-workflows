# ADR-0016: Use connected Codex apps for PostHog and Polar

- Status: superseded
- Date: 2026-11-11
- Owner: Project maintainer
- Evidence: Explicit maintainer request to reuse already configured PostHog and Polar Codex plugin connectors and no longer use local CLI tokens; [issue 113](https://github.com/WilsonLe/agentic-workflows/issues/113)
- Supersedes: none
- Superseded by: 0017

## Context

ADR-0015 chose Codex as the supported host and the connected Vercel app as its
remote operation channel. The shared provider contract still describes CLI
providers but has no explicit PostHog or Polar route. The maintainer has configured
both connectors and requires agents to respect that setup rather than provision
local tokens.

## Decision

Extend the existing shared provider channel contract for PostHog and Polar remote
operations. Reuse their configured Codex plugins/connected apps, discover applicable
tools/instructions, and verify the exact project or organization and environment
before dependent work. Codex owns connector authentication. Recover connections
through Codex and report unsupported operations or permissions without a CLI,
raw HTTP/SDK account-management, or dashboard fallback.

Exclude their agent account-authentication stores from local `.cli/` setup and
worktree copies. Preserve existing stores without reading, migrating, or deleting
them. Application runtime integration configuration and secrets remain distinct;
connector authentication is never extracted for application use. Existing action
authority and readback requirements remain in force.

Keep one instruction owner in service-browser-operations.md with entry-point,
onboarding, credential, browser-selection, and worktree links. Add no provider
adapter, new skill, credential format, or validator. ADR-0015's Vercel and host
decisions and the other named providers' CLI contracts remain in force.

## Alternatives

Merely preferring connectors would allow agents to reprovision tokens after a
connection or capability failure, contrary to the maintainer's channel choice.
A dedicated PostHog or Polar wrapper would duplicate the connected plugins and
introduce another authentication owner. Removing all CLI provider guidance would
change unrelated providers beyond the request.

## Consequences

Agents reuse already configured connections and avoid copying legacy account tokens
into new worktrees. An unavailable connection, permission, or operation blocks only
its dependent work. Runtime SDK and webhook configuration still needs the relevant
integration instructions and secret handling.

Package checks and scenario inspection establish instruction consistency and
portability, not live provider permissions or future agent adherence. This source
change does not update installed plugins, mutate provider state, or delete tokens.
Rollback uses a source revert and regenerated package without credential migration.

## Revisit

Reconsider only on an explicit maintainer request for a different channel with a
concrete unsupported operation and a verified authentication/authority contract.

On 2026-11-11, [ADR-0017](0017-use-codex-connected-apps-and-retire-project-cli-credentials.md)
replaced this policy under the maintainer's global connected-app and no-project-token-store request.
The rationale above records the earlier choice; current operation and runtime
authentication follow ADR-0017.
