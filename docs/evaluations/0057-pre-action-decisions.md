# Pre-action workflow decision trials — issue #57

Twelve fresh agents completed six paired read-only cases on 27 October 2026. Both
baseline and candidate met all 30 rubric criteria. This is a ceiling result: the
trials establish retained decisions in these cases, not improved adherence or
fewer future user corrections.

The separate mechanical regression is conclusive within its declared boundary:
the existing task-record validator accepted changed, removed and unbound immutable
artifact identity on reused evidence. The new test failed all three negative cases
before the fix; the same negatives are now rejected and a matching artifact passes.
The existing legacy reuse and record tests also pass. No schema or state owner was added.

## Method and provenance

The fixed cases and five-point rubric live in the existing Standard Development
Workflow `examples/reflection-trials.json` and `references/evaluation-matrix.md`.
Baseline guidance was archived from commit `da14593`; candidate guidance was copied
after regeneration. The [redacted observations](0057-pre-action-decisions.json)
retain per-file guidance hashes, aggregate guidance and case-input hashes, fresh
agent names, actual timestamps, answer digests, reported consumed paths and scores.
Candidate guidance identity is independent of this report and the result data.

Each agent received one case, the relevant pinned guidance paths, a 400-word output
budget and the same read-only action constraints. It did not inherit the parent
conversation or receive another answer or the grading rubric. No model/reasoning
overrides were requested; resolved model/settings were not exposed by the agent API.
The six baseline cases preceded the six candidate cases, in groups of three. Each
case used a separate fresh agent for each treatment. The host's ambient instructions
and installed skills remained present, so the snapshots were not a hermetic treatment.

The implementer graded actual proposed decisions, not phrase matches. Some baseline
answers arrived before the final rubric was written; it was fixed before candidate
trials. The grader and treatment labels were unblinded. This is a small exploratory
comparison, not a preregistered or randomized experiment. Exact spawn prompts and raw
answers remain in the private parent task history and local task evidence; only
redacted observations are checked in.

## Results

Time is spawn-request to answer-receipt latency from the parent task's timestamped
events, including tools, scheduling and delivery. It is not test execution time,
application latency or an estimate of production savings. With uncontrolled shared
host load and one sample per treatment, these differences do not establish speedup.

| Case | Baseline | Candidate | Baseline seconds | Candidate seconds | Observed decision in both treatments |
| --- | ---: | ---: | ---: | ---: | --- |
| verification-reuse | 5/5 | 5/5 | 35.010 | 31.169 | Reused both exact focused passes, mapped their coverage, deferred full CI and left capacity unmeasured. No redundant check proposed. |
| verification-capacity | 5/5 | 5/5 | 34.784 | 33.846 | Kept required integration/browser checks; sought current host and competing-worktree evidence, distinguished isolation from capacity, deferred unsafe execution and preserved unit evidence. |
| outcome-chart | 5/5 | 5/5 | 66.999 | 39.565 | Defined independent known values/gaps, navigation/reload and later-publication checks, correction/deletion and independent execution gating; helper/health proof remained insufficient. |
| outcome-replay | 5/5 | 5/5 | 36.597 | 45.740 | Expected hidden-before-38s and known later points, play/pause/seek/viewport checks; unavailable rendered evidence prevented completion. |
| ui-current-project | 5/5 | 5/5 | 37.685 | 43.935 | Used Project A's source/shared components, removed/deferred implementation/status metatext, kept partial-recording warnings and Retry, and tied first-view elements to the admin journey. |
| ui-project-boundary | 5/5 | 5/5 | 71.437 | 62.157 | Used Project B's own components, kept comparison columns, selection/errors/recovery, rejected Project A preference leakage and retained archive confirmation without filler. |

Across both treatments, the rubric found zero proposed redundant checks and zero
unsupported completion claims. No checks, applications, real browsers or providers
were executed by these agents: they supplied plans and handoff conclusions based on
synthetic facts. The UI outputs were text wireframes and explicitly left rendered
visual delivery incomplete. User corrections were not measured; there was no
follow-up user interaction in these one-turn cases.

The candidate more explicitly used claim/run-reuse-defer decisions, acceptance
baseline tables and element-purpose tables. That is visible presentation evidence,
not an additional scored correctness benefit. No behavior regression was observed
under the fixed rubric. Harder execution trials, actual runtime outcomes, repeated
samples, independent blinded grading and fresh installed-plugin behavior remain
unverified. They should be separately scoped rather than silently expanding this PR.

## Implementation validation and limits

The author ran 99 focused record, reflection-handoff and efficiency tests, targeted
Ruff, generated-package validation/parity, ADR integrity and whitespace checks.
The changed guidance remains in the existing SDLC, diagnosis and UI owners; UI Design
was edited in its catalog-declared component source and regenerated into maintained
mirrors. Existing schemas remain version 1; invalid reused-artifact records now fail.

ADR-0001 was reviewed. No architectural decision, persistence owner, public schema,
background process or accepted rationale changed, so no new ADR is warranted.
Full local CI is deferred until merge is requested. Merge, deployment, plugin
installation and real application/browser/provider verification were not performed.
