---
name: engineering-diagnosis
description: Diagnose a hard software bug or performance regression by building a symptom-specific feedback loop, narrowing the cause, and verifying the same path after a fix.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering diagnosis

Use this skill when a bug's cause is uncertain or a regression is difficult to reproduce. Read the intended environment and current revision first. For code changes, follow the repository's delivery and evidence rules and the Codex Standard Development Workflow when available. Protect secrets and personal data in production observations.

## Establish a useful signal

1. Capture the user's exact symptom and the first relevant failure, with secrets and personal data removed. Distinguish an observed fact from a suspected cause.
2. Build the smallest repeatable check that traverses the failing path and detects that symptom. A targeted test, CLI invocation, HTTP request, browser script, trace replay, or differential run may fit. Run it at least once and show what it detected. A check that merely exits successfully is insufficient when the bug is wrong behavior.
3. Tighten the check: reduce setup time, control unstable inputs, and raise the reproduction rate for intermittent failures. If the real environment cannot be reached, state precisely which path and evidence are missing before claiming a root cause.
4. Remove inputs or steps one at a time, rerunning the check until each remaining part matters to the failure.

## Locate and fix

Form a short ranked set of falsifiable explanations. Each should predict what a specific probe would change or reveal. Probe the cheapest discriminating boundary first, changing one variable at a time. For a performance regression, measure a baseline before altering the code. Keep temporary instrumentation identifiable so it can be removed.

Where a meaningful test seam exists, preserve the minimized case as a failing regression test, make the smallest justified fix, and see the same test pass. Prefer a test through the interface or call path where the bug occurred; a test of an isolated helper may miss an integration failure. If no suitable seam exists, report that limitation explicitly rather than adding a reassuring but irrelevant test.

Repeat the original user-facing path on the intended running revision. Remove temporary probes and report the initial signal, cause confidence, changed behavior, and any unverified environment or provider boundary.
