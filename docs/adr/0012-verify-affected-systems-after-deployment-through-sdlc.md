# ADR-0012: Verify affected systems after deployment through SDLC

- Status: accepted
- Date: 2026-11-04
- Owner: Project maintainer and implementing agent within task authority
- Evidence: Maintainer approval of plan v1 for [issue 99](https://github.com/WilsonLe/agentic-workflows/issues/99) through the Codex plan action.
- Supersedes: none
- Superseded by: none

## Context

SDLC already gates merge on local CI and checks active release identity, health,
and a user flow after deployment. One surface can pass while a downstream
system, worker, or release consumer affected by the same change fails. Ordinary
and autopilot delivery need the same criteria for closing out a rollout.

## Decision

Use the existing Standard Development Workflow merge and deployment stages as
the shared contract. Record passing local checks for the current merge candidate.
Plan the affected systems and evidence per target before merging, then verify
health and functionality for each included system against the actual rollout.
Observe merge-triggered rollouts and use the existing authority rules for manual
deployment, production, and remediation. Keep deployment verification incomplete
while any required result fails or is unavailable.

## Alternatives

A smoke test for the main service leaves downstream and asynchronous effects
unproven. A fixed global checklist would miss repository-specific dependencies
and burden changes with unrelated checks. A new release record schema would
duplicate the existing plan, impact inventory, and release evidence owners.

## Consequences

Ordinary SDLC, SDLC Loop, and Orchestration reuse the same stages. Existing
records remain readable. Release evidence must show why each system was included
or excluded and tie the observed outcome to the real target. A shared probe can
cover several systems if it proves each required outcome. Package and record
validation remain separate from live rollout evidence.

## Revisit

Revisit if tasks repeatedly omit affected systems despite following discovery,
or if existing release evidence cannot express multi-target rollouts clearly.
