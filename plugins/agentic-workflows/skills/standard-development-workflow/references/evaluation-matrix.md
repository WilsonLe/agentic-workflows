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
| #121 | Explicit deliverables, later corrections, no-PR narrowing, final artifact audit | contract reconciliation, explicit-over-inferred, excluded/required final-gate tests | Resume an issue-first task; narrow another task to explanation without creating artifacts |
| #122 | Measured check inventory, exact-run deduplication, safe concurrent state, no weaker substitution | cost, repeated run, identity, reuse, overlap, planner tests | Profile a library, Compose app, and concurrent worktrees; compare before/after wall time and coverage |
| #123 | Authenticated route recovery, provider-state ledger, source-copy comparison, target-flow proof | route classification, dependency, saved/readback/final-gate, artifact-check tests | Recover a signed-in source after API redirect and resume a partially configured provider flow |
| #124 / WilsonLe#38 | Pattern-wide discovery, explicit exclusions, and final proof for each included surface | missing/duplicate surface tests; CLI scenarios enumerate practice/mock × reorder/speech/choice × answered/missing-response, reuse shared proof, and reject an omitted cell, missing/unknown proof, or unresolved runtime outcome | Inventory actual routes, question types and states before the change; compare the final handoff with discovery and inspect representative shared renderers |
| #125 | Correlated runtime operation or explicit missing trace; privacy-safe diagnosis and proven/unproven cause | missing-trace, unsupported-cause, policy, and synthetic 429/SQL case tests | Trace a failing operation from user action through tool/provider response without retaining sensitive values |
| #126 | Active runtime revision, mode, URL, health, flow, and public reachability before availability | stale revision, wrong mode, unverified flow, stopped process, and public-reachability tests | Distinguish PR open, merged, stale server, staging only, and verified public production |
| #165 | Composed async feedback with operation ownership, accessible busy state, approved counts, and terminal cleanup | delayed/overlap/cancellation/warm/retry trace replays reject disabled-only, stacking, early clear, partial-ready, and missing terminal observations | Delay an actual changed interaction; inspect shared controls, router, and global consumers together against the current project's convention |
| #166 | Ordinary Goal-mode scope corrections, independent progress, host blocking threshold, resume reset, and actual status readback | scope reduction, changed blocker/progress, three-turn threshold, pause/resume, unavailable controls, and false terminal claim replays | Resume an existing ordinary goal; remove one outcome explicitly, reach the host blocking threshold, verify transition, then resume with a fresh audit |
| #167 | Complete requested provider coverage and separate captured fresh discovery | absent/disabled/conflicting provider, version/path/hash drift, stale/duplicate/wrong-provider discovery, and CLI exit regressions | Reinstall an authorized merged release, read back source/cache parity, then inspect a new task's catalog created after the update |
| WilsonLe#35 / #38 | Consumer outcome and requested verification channel survive handoff | CLI scenarios reject controlled-provider success, failed actual indexing, and a different selected channel labelled primary; accept approved equivalence and explicit future deferral without claiming success | Start a fresh indexing/playtest task with a declared browser/provider; observe the actual consumer, retain failed observations, and verify the selected channel before completion |
| #146 / #151 / WilsonLe#38 | A later UI task consumes current project decisions while preserving essential recovery and accessibility | CLI scenarios accept progressive disclosure with a documented recovery exception; reject pending/failed/missing evidence, another project's rule, stale final capture identity, and an applicable superseded rule | Give a fresh task established project guidance; inspect changed screens for clutter, on-demand detail, labelled recovery and focus; repeat in another project without inheriting the rule |

The reflection handoff scenarios run in the existing repository unittest discovery:

```bash
uv run python -m unittest tests.test_reflection_followups.ReflectionHandoffScenarios
```

These are synthetic complete-record replays through the record helper's
`validate --require-final` command, not live model, provider, or browser runs. They check declared
evidence consistency; they cannot discover undeclared rules/consumers, judge screenshot
content, or establish fresh-task adherence. For the observation column, retain the new
task ID, candidate/target identity, consumed guidance, selected channel, expected and
observed result, evidence reference, and limitations in the existing issue/task evidence.
Keep unavailable observations explicit. Do not turn passing fixtures into a runtime claim.

## Six paired reflection trials

Use the fixed inputs in [reflection-trials.json](../examples/reflection-trials.json) for a
bounded fresh-agent evaluation of the three pre-action decisions. The cases exercise planning
and handoff reasoning against supplied facts. They do not execute the described application,
browser, provider or production checks. A fresh-agent answer is an observation of that answer,
not proof of future task execution or a measured application speedup.

Pin a baseline commit and candidate guidance snapshot. For each case, use a separate fresh agent
for each treatment, the same model/settings, neutral prompt, case facts, read-only tools and
output budget. Supply only the relevant pinned skill/reference paths; keep the rubric, other
answers and expected improvements out of the agent context. Resolve links inside that snapshot.
Do not inherit the implementation conversation or add reminders for the behavior being measured.
Capture agent identity, consumed paths, guidance/case digests, answer and elapsed time. Record
ambient installed-guidance exposure and other limits. New chats, agents and provider calls still
require the host's applicable authority; the protocol grants none.

Set the rubric before reading answers. Give one point per criterion below, using the actual
decision/output rather than wording matches; retain the reason for every missed point. Count
proposed redundant checks and unsupported completion claims separately. User corrections are
unmeasured in these one-turn trials; do not record their absence as evidence of fewer corrections.
Elapsed trial time measures agent deliberation/tool latency, not the supplied check durations.

| Case | Five observable criteria |
| --- | --- |
| verification-reuse | Map both affected claims to their focused passes; reuse their exact matching evidence; propose no unchanged rerun; defer full CI to merge; keep unmeasured capacity explicit |
| verification-capacity | Retain both required integration/browser checks; inspect current host/competing load before launch; distinguish state isolation from capacity; bound/defer unsafe overlap without stopping other work; preserve valid unit evidence and defer full CI |
| outcome-chart | Define a known independent input/oracle before edits; preserve completed values and real gaps; exercise navigation/reload and later publication; cover supported correction/deletion and independent execution gating; label helper/health evidence insufficient |
| outcome-replay | Hide before the first sample and use known later points; check play/pause; check seeking backward/forward and viewport mapping; leave required rendered evidence unavailable; avoid treating API/transport success as rendered proof |
| ui-current-project | Name Project A's current source; reuse its shared controls; remove/defer compiler and fetching metatext; retain visible partial/missing warning and Retry; justify the first-view elements by the administrator's task |
| ui-project-boundary | Use Project B's own source/components; retain side-by-side comparison columns; retain selection, errors and recovery; reject Project A preference leakage; remove filler and keep archive confirmation |

Report all six baseline/candidate scores and errors, including ties and regressions. Keep raw
answers in private task evidence; publish only redacted observations and provenance needed to
assess the result. Guidance-only changes do not prove a validator improved; synthetic negative
cases do not prove an agent acted correctly. A small nonrandomized, unblinded trial with an
implementer grading answers cannot establish causal or general model improvement. If the baseline
already passes, report retained behavior and evaluate harder cases in separately authorized work.

## Final combined gates

During development and draft-PR handoff, run only focused checks for affected contracts and
consumers, plus relevant static/generated validation. The complete test suite and repository-wide
lint below run at the authorized merge stage. Installation and host observations apply only when
that release/installation outcome is in scope.

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
8. Visibly verify the rendered Agentic Workflows Plugins UI entry.

Any skipped observation remains explicit with its reason and cannot satisfy a child acceptance
criterion that requires that channel.
