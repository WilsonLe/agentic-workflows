---
name: engineering-diagnosis
description: Diagnose a hard software bug or performance regression by building a symptom-specific feedback loop, narrowing the cause, and verifying the same path after a fix.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering diagnosis

Read the intended environment and running revision. Follow repository delivery and
evidence rules and the Codex Standard Development Workflow when available. Protect
secrets and personal data in observations.

## Establish a useful signal

1. Capture the exact symptom and first failure safely. Separate observation from
   suspected cause; inspect accessible logs and state before asking the user.
2. Run the smallest repeatable check through the failing path. Derive expected
   results independently of the implementation: known inputs, values, ordering,
   durable effects, or a trusted baseline. Confirm a relevant wrong result fails
   the check; successful execution alone does not prove correct behavior.
3. Control unstable inputs and minimize setup and steps, rerunning after each change.
   For intermittent failures, improve reproduction rate. If the real path is
   unavailable, name the missing evidence before claiming a root cause.

## Locate and fix

Rank a few falsifiable explanations and their distinguishing probes. Test the
cheapest boundary first, changing one variable at a time. Measure a performance
baseline before altering code. Keep temporary instrumentation removable.

Apply [existing abstractions first](../engineering-exploration/SKILL.md#existing-abstractions-first):
repair the responsible owner instead of duplicating its rule in a workaround.
Where a useful seam exists, retain the minimized case as a failing regression,
make the justified fix, and rerun that same test through the original interface.
If no suitable seam exists, report the limitation rather than add an irrelevant test.

Repeat the original user-facing flow on the intended running revision. Remove
probes and report the initial signal, cause confidence, changed behavior, and
unverified environment or provider boundaries.
