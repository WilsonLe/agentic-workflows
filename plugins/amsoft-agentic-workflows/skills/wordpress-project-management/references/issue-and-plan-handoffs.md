# WordPress issue, PR, and plan handoffs

For a project task, keep the spec, implementation, site state, and release evidence separate.

## Spec-ready issue

Include outcome, current evidence, site/project inventory, exact scope, non-goals, managed objects
and fields, source-of-truth, target environments, lifecycle/approval gates, surface-specific
acceptance criteria, content checksum/rollback requirements, integration/privacy limits,
dependencies, risks, and open decisions. Link relevant specialist contracts and do not put secrets
or private content in the issue.

## Implementation plan

The plan names the base SHA, isolated worktree, changed file families, route/composition behavior,
schemas/examples, command contract, test fixtures, validation ladder, browser/provider limitations,
generated artifacts, PR structure, release/rollback boundary, and definition of done. Update the
canonical plan in place when material findings change it; do not silently broaden scope.
Use `standard-development-workflow` for the repository delivery gates that surround this plan,
including the isolated worktree, fail-fast validation, draft PR, and separately approved staging or
production work.

## PR handoff

The PR must state:

- what changed and what remains specialist-owned;
- that `wp-content-sync` is a contract unless an implementation is explicitly present;
- tests and exact results, including negative/conflict cases;
- no real WordPress site, provider, production runtime, or analytics/audit data was changed;
- source/PR/local/staging/production/public/provider states separately;
- known skipped/blocked channels and rollback limitations;
- merge, plugin reinstall, staging, and production as separate gates.

Passing repository checks prove the package candidate only. They never prove a WordPress site was
changed, deployed, published, indexed, or collecting data.
