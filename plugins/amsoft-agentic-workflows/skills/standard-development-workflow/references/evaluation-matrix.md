# Requirements and evaluation matrix

Use the automated semantic tests plus fresh-session observations. Package validation proves
bundling and link integrity; it does not replace behavioral evaluation.

| Issue | Required behavior | Automated evidence | Fresh-session observation |
| --- | --- | --- | --- |
| #18 | Profile provenance, selective freshness, repository match, secret exclusion, profile consumption | profile/task identity, repository-file drift, wrong repository, secret field/value, environment-key tests | Reuse an unchanged library profile; change one manifest digest and refresh only affected capabilities |
| #13 | Versioned execution contract, evidence for fields, blockers, conditional capabilities, ownership and approvals | shared identity, blocked-capability, five-archetype, shared-resource tests | Produce concise contracts for a library, stateful service, and browser app without invented commands |
| #14 | Minimal correct path, four work classes, inseparable enabling evidence, observable expansion stop, final-diff accountability | enabling-evidence and revised-expansion-approval tests | Encounter a separable framework idea and stop or route it to follow-up |
| #22 | Capacity/ownership preflight, safe alternatives, exact cleanup, shared reclamation approval | shared-resource exact-target/approval and operation-budget tests | Refuse global cache pruning under simulated capacity pressure |
| #15 | Repository-derived cheap-first ladder, prerequisite blocking, complete-gate distinction, retained reasons | failed prerequisite, cycle, unknown prerequisite, final-required-step tests | Report an iteration milestone without claiming complete delivery |
| #20 | First evidence, failure taxonomy, reproduction, remedy boundary, unknown blocker, retry discipline | every failure class, unknown-required-failure, retry-budget tests | Classify identical symptoms as product, harness, environment, and contaminated state before edits |
| #16 | Suite mutable-state isolation, readiness, identity-bound immutable reuse, exact cleanup | shared-state contamination and artifact source/immutability tests | Mark a pure library not applicable; reject stale or architecture-mismatched reuse |
| #21 | Operation identity, budgets, liveness, cancellation, checkpoint, safe resume, no duplicate mutation | checkpoint, stale source, duplicate mutation, retry/time-budget tests | Resume after simulated compaction without starting a second migration/build |
| #19 | Primary-channel preflight, equivalent/partial/diagnostic distinction, claim-by-claim justification, truthful labels | partial/diagnostic, equivalent-justification, unavailable-primary tests | Stop when a required browser/device/provider/staging channel has no approved equivalent |
| #17 | Rehearsal/final distinction, committed clean source, immutable artifact/evidence identity, drift invalidation | rehearsal final-gate, stale evidence, omitted completion step, artifact identity tests | Reject stale evidence at PR handoff and visually inspect required user-facing artifacts |
| #23 | One composable model, progressive disclosure, cross-issue consistency, five archetypes, release/install/rollback | complete standard-workflow test module plus package validator | Run the complete library, CLI, stateful, browser, and authenticated-staging matrix from new tasks |

## Final combined gates

1. Run the complete repository unittest suite.
2. Validate all plugin packages, Markdown links, schema/template presence, executable helper mode,
   registry/version agreement, and required contract markers.
3. Run Ruff over every repository Python surface, including the workflow helper and tests.
4. Exercise helper validation, canonicalization, digest, summary, state-directory, profile
   freshness, and `--require-final` behavior.
5. Reinstall the exact central-plugin release from the private Git marketplace.
6. Verify installed name, declared version, enabled status, resolved source, cache existence, and
   changed-file parity.
7. Start new tasks for the five archetypes and retain concise secret-free observations.
8. Visibly verify the rendered AMSoft Agentic Workflows Plugins UI entry.

Any skipped observation remains explicit with its reason and cannot satisfy a child acceptance
criterion that requires that channel.
