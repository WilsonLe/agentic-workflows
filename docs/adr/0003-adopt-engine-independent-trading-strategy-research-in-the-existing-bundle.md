# ADR-0003: Adopt engine-independent trading strategy research in the existing bundle

- Status: accepted
- Date: 2026-10-28
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User request to deeply research and adopt stock/futures strategy skills into Agentic Workflows; [scope and design](https://github.com/WilsonLe/agentic-workflows/issues/61); routine design authority under Standard Development Workflow and ADR-0001
- Supersedes: none
- Superseded by: none

## Context

The bundle has no trading-research owner. External collections cover useful
hypothesis, data, execution and validation methods, but importing them wholesale
would add overlapping routers, engine dependencies, arbitrary readiness scores
and market-specific assumptions. Research findings need a coherent lifecycle and
clear boundaries between a proposed edge, measured simulation and execution.

## Decision

One portable `trading-strategy-research` skill owns the experiment brief and
evidence handoff in the existing Agentic Workflows bundle. Conditional references
own stocks, futures, data, backtesting and statistical validation methods. Reuse
the project’s engine, records and delivery workflow; Markdown templates are a
fallback, not another schema, engine, validator or persistent state system.

Selectively adapt pinned ML4T and TradeMonty methods with their notices and explicit
modifications. Do not import upstream executable code, automatic PASS/Deploy scores,
fixed statistical gates or broker access. Experiment acceptance is precommitted
for the actual instrument and horizon. Source inspection, historical simulation,
paper observations and live results remain separate evidence classes.

The user’s implementation request and existing workflow policy authorize this
routine design on 2026-10-28. Accepted records the chosen boundary; it does not
assert merge, installed-plugin behavior, trading results or release readiness.

## Alternatives

Separate stock/futures plugins would duplicate experiment and validation ownership
and conflict with the one-bundle publication model. Many small upstream skills
would make shared evidence harder to keep consistent. A new backtester or broker
adapter would require separate runtime, numerical and account contracts beyond
this adoption. Another workflow schema would compete with project-owned research
records without adding enforcement justified by observed needs.

## Consequences

The bundle gains one discoverable lifecycle with portable references and no runtime
dependency. Agents must inspect engine semantics and actual instrument data before
claims. The instruction package cannot mechanically establish statistical validity,
agent adherence or profitability; those require experiment-specific observations.
Upstream licenses remain with adapted material in all generated harness packages.

## Revisit

Split a responsibility only after repeated real requests show that it has distinct
inputs, outputs and independent consumers. Consider a numerical helper or adapter
only when an existing project owner cannot meet a concrete requirement and its
correctness, dependency and execution authority can be verified separately.
