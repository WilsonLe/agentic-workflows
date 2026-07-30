# Spec-ready GitHub issue contract

A spec-ready issue is an implementation-planning input, not a vague idea and not a hidden design
document. It gives a capable engineer enough verified context to produce an exhaustive plan without
guessing about intended behavior.

## Required issue content

1. **Title and outcome** — one concrete, searchable outcome.
2. **Problem and user impact** — who is affected, what is wrong or missing, why it matters, and the
   desired outcome without prematurely dictating an unsupported solution.
3. **Evidence and current behavior** — reproducible observations, relevant URLs or screenshots,
   logs with secrets removed, existing code paths, related issues or pull requests, and the
   repository revision or environment inspected.
4. **Proposed behavior** — observable behavior after completion, including important states,
   workflows, error handling, compatibility, and edge cases.
5. **Scope** — included surfaces, components, users, data, APIs, and environments.
6. **Non-goals** — plausible adjacent work intentionally excluded.
7. **Acceptance criteria** — finite, unambiguous, externally observable, and testable conditions.
   Use scenario form when it improves precision. Include regression expectations.
8. **Constraints and invariants** — repository conventions, compatibility, performance, security,
   privacy, accessibility, localization, data migration, operability, or compliance requirements
   that actually apply.
9. **Dependencies and blockers** — upstream work, credentials, decisions, services, feature flags,
   migrations, and issue relationships. Use GitHub dependencies or sub-issues when supported.
10. **Verification expectations** — required unit, integration, end-to-end, manual, visual,
    accessibility, performance, security, migration, rollback, and environment checks as applicable.
11. **Release and rollback considerations** — local, staging, observability, data safety, feature
    flags, and rollback or recovery expectations. Production remains outside this workflow.
12. **Open questions and decisions** — confirmed facts, safe assumptions, unresolved items, owner,
    and whether each item blocks planning or implementation.
13. **Definition of done** — code, tests, documentation, telemetry, PR evidence, merge,
    synchronization, cleanup, and staging verification applicable to the change.
14. **Minimal correct path** — direct work, inseparable enabling work, follow-ups, prohibited work,
    expected changed-component envelope, and observable scope-expansion triggers.
15. **Execution prerequisites** — consumed capability-profile identity, resource ownership and
    capacity, validation ladder, required verification channels, and blocking unknowns.

## Research procedure

1. Read the complete request and attached evidence.
2. Inspect repository instructions, architecture, tests, nearby implementations, history, open and
   closed issues, relevant pull requests, and CI/deployment configuration.
3. Reproduce or observe current behavior when safe and relevant.
4. Search authoritative external documentation for unstable or unfamiliar technologies. Prefer
   official documentation and primary sources.
5. Separate confirmed facts from inference. Link sources near the claims they support.
6. Search for duplicates before creating a new issue. Refine an existing issue when it is the
   unambiguous source of truth and the user has authorized the workflow.
7. Create the issue with appropriate type, labels, relationships, and milestone only when those
   conventions already exist. Do not invent taxonomy.

## Readiness test

The issue is ready only when:

- every acceptance criterion can be mapped to at least one planned verification method;
- every supported command and capability maps to repository or user evidence;
- scope and non-goals prevent obvious expansion;
- important edge cases and applicable cross-cutting requirements are represented;
- repository evidence identifies the likely change surfaces without prescribing unverified code;
- no unresolved question would materially change architecture, user-visible behavior, data
  handling, security, test strategy, or rollout.
- unavailable required verification channels and unknown ownership or capacity remain explicit
  blockers rather than silently weakened assumptions.

If a blocking question remains, keep the issue explicitly `Needs specification` (or the
repository's equivalent), ask the user for the missing decision, and do not claim it is spec-ready.

## Canonical implementation plan comment

After the issue is spec-ready, post the exhaustive implementation plan as exactly one canonical
issue comment:

- begin with `<!-- amsoft-standard-development-plan -->`;
- include the inspected source revision and every Stage 2 plan requirement;
- pin the comment and read it back before presenting it for approval;
- retain the comment ID and URL in the task record;
- after implementation authorization, change its status in place and append concise dated
  reconciliation entries for material findings and decisions;
- update requirements-to-tests mappings when findings change verification;
- mark it `reapproval_required` before proceeding when scope or architecture materially expands;
- never post a replacement authoritative plan comment merely because the plan evolved.

GitHub environments that cannot pin or update the comment block the canonical GitHub planning
mode. Keep the limitation explicit rather than silently substituting an unpinned or duplicate plan.

## Research basis

This contract operationalizes GitHub's issue forms and required-field model, issue relationships
and dependencies, GitHub's draft pull-request review boundary, and established code-review
expectations that reviewers receive the change's what, why, design, functionality, tests, and
documentation context. Repository-specific policy always wins.
