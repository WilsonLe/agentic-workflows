# ADR-0001: Maintain architecture decisions within each project workflow

- Status: accepted
- Date: 2026-10-18
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User request to establish a self-maintaining ADR system per project; routine design choices authorized by Standard Development Workflow; [scope and design](https://github.com/WilsonLe/agentic-workflows/issues/43)
- Supersedes: none
- Superseded by: none

## Context

The development workflow referenced ADRs without specifying discovery, ownership,
status transitions or upkeep. Architectural rationale could remain in transient
chats and task issues, and later changes could drift from earlier decisions.
The repository already owns planning and review in Standard Development Workflow,
with canonical skill sources and generated packages for supported agent hosts.

## Decision

Each project owns its versioned architectural decisions. Reuse an existing ADR
convention; otherwise bootstrap `docs/adr/` on its first durable architectural
choice. Maintain the records and index during discovery/design, implementation
and PR review, linking affected IDs or a justified no-impact result in the task.
This repository adopts that fallback immediately.

The Standard Development Workflow reference owns the lifecycle, while intake,
exploration and review link to it. A dependency-free helper under the same skill
owns the fallback Markdown format and deterministic index. Task records retain
their existing execution contract. Separate persisted responsibilities justify
keeping ADR file operations out of the task-run validator.

On 2026-10-18, this design was selected under the user's implementation request
and the workflow's routine-design authority. Accepted describes the chosen design;
PR review, merge, package release and behavior in other projects remain separate.

## Alternatives

A central cross-project registry would separate decisions from their repository
and complicate ownership and access. A periodic scheduler would require additional
runtime and authority, and could miss the rationale known during implementation.
A separate ADR skill would duplicate the existing development lifecycle. Guidance
alone would leave mechanical index and supersession errors unchecked. Requiring
migration of established formats would create unnecessary adoption work.

## Consequences

Agents must read relevant decisions and include ADR reconciliation in architectural
PRs. Accepted rationale is preserved, with a new decision and reciprocal links for
replacement. Proposed decisions require real authority evidence before acceptance.
The helper checks structure, reference integrity and index freshness; agents and
reviewers check semantic accuracy, history and authority. Existing formats retain
their own tooling. Worktree ID collisions require reconciliation before merge.

This introduces no background process, external service or cross-project mutation.
The reusable workflow becomes available through normal package delivery; adopting
it here does not demonstrate future agent behavior in every consuming project.

## Revisit

Reconsider if independently governed projects in a monorepo need incompatible ADR
boundaries, repeated merge-time ID collisions make numeric allocation costly, or
observed workflow runs show a concrete maintenance failure. Extend the existing
owner with evidence before adding a registry, scheduler or second validation layer.
