---
name: engineering-exploration
description: Explore an uncertain module design or UI behavior with a focused architecture survey or disposable prototype before committing to implementation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering exploration

Use the smallest survey or disposable experiment that answers the design question.
For tracked changes, follow repository delivery rules and the Codex Standard
Development Workflow when available.

## Existing abstractions first

Apply this method when changing any codebase, including agent skills and tooling:

1. Find the existing responsibility owner, callers, tests, and contracts. Establish
   whether the mechanism still serves the requested behavior before restructuring it.
   Edit, extend, simplify, or remove that abstraction before introducing another.
   Fix the cause in its owning layer; avoid a compensating wrapper or duplicate rule.
2. Introduce a boundary only when the existing owner cannot safely express the
   required behavior. Explain the limitation and why the new responsibility belongs
   separately. Separate optional generalization from the requested vertical path.
3. Keep a new abstraction atomic: one cohesive responsibility with a clear reason
   to change, not an arbitrary one-function or tiny-file limit. Identify consumers,
   dependency direction, required capabilities, and state ownership; avoid hidden
   global coupling and accidental cycles.
4. Define its inputs, outputs, or data schema, including validation, invariants,
   errors, and side effects. Use existing types and schema machinery. For public or
   persisted contracts, specify compatibility and any version/migration needs.
   Verify the behavior through its actual consumer boundary.

## Architecture survey

Read the named subsystem or recent hotspots, domain vocabulary, ADRs, callers, and
tests. Find concrete friction: scattered responsibilities, leaking contracts,
repeated cross-module edits, or a missing useful test seam. Rank a few candidates
with affected files, current cost, responsibility shift, verification benefit, and
confidence. Respect existing ADRs unless new evidence warrants revisiting them.
Survey findings do not authorize every proposed refactor.

## Disposable prototype

State the question and observable success signal before building. For UI uncertainty,
show distinct variants on one runnable surface; for logic, expose state and relevant
edge cases. Label the artifact as a prototype and keep state disposable unless
persistence is the question. Skip production polish and implementation-mirroring
tests. Record observations and the chosen direction
in the existing issue or decision record. Remove or isolate throwaway code from the
delivery branch; retain only validated behavior in production.
