# ADR-0014: Ship ordinary Standard Development Workflow across supported hosts

- Status: accepted
- Date: 2026-11-04
- Owner: Project maintainer and implementing agent within task authority
- Evidence: Maintainer approval of plan v1 for [issue 102](https://github.com/WilsonLe/agentic-workflows/issues/102).
- Supersedes: none
- Superseded by: none

## Context

The published Claude Code and OpenCode packages omitted the ordinary SDLC skill.
Its approval, Git, review, and release evidence requirements apply to repository
delivery across hosts. Some native controls and the separate autopilot skills
depend on Codex.

## Decision

Publish ordinary SDLC in the existing portable bundles using the single maintained
skill and generator. Apply shared approval, exact-candidate review, local merge,
and per-system rollout evidence rules on all three hosts. Use chat-based plan
approval, Git worktrees, and supported independent review where applicable.
An unavailable required capability keeps the affected gate incomplete. Keep
verified autopilot and its trust and coordination machinery scoped to Codex.

## Alternatives

Separate host-specific copies would duplicate the delivery rules and risk gate
drift. Packaging the Codex control plane in every bundle would advertise runtime
and authority capabilities those hosts do not provide.

## Consequences

Claude Code and OpenCode receive the same ordinary workflow references and
evidence helpers. Existing records remain compatible. Codex retains its
verified autopilot paths. Fresh-session decision checks use the same controlled
scenarios in each host and remain separate from evidence of a real release.

The shared terminal completion check uses the existing handoff evidence and
validator on every host, including tasks without a full record. Python 3.10+
is required for that check. Retained records remain inspectable as planned or
blocked; completed delivery must refresh missing handoff or review evidence.
This extends the existing portable owner, not a host stop hook or state service.

## Revisit

Revisit when a shared requirement cannot be met through a supported host channel,
or when a portable autonomous control plane has verifiable authority and review
semantics.
