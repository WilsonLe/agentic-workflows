# Verification, deployment, and cleanup rules

## Verification quality

- Use the repository's own checks first and add focused tests for the change.
- Tests must be capable of failing when behavior is broken. Do not accept assertions that merely
  execute code without proving outcomes.
- Cover happy paths, relevant boundaries, invalid inputs, permissions, failure recovery,
  concurrency, and regressions in proportion to risk.
- For web work, verify the rendered behavior at the real local origin. Include responsive,
  accessibility, console/network, and visual checks when relevant.
- Match evidence to the request. A passing API test does not prove a visual change, and a
  screenshot does not prove data integrity.
- Record skipped or inapplicable checks with reasons. Never silently convert a required failure
  into a pass.

## Staging parity

- Confirm the deployed commit or immutable artifact matches the squash-merged revision.
- Use staging URLs and external integrations intentionally; do not accidentally test localhost.
- Re-run safe automated smoke, integration, end-to-end, accessibility, performance, and security
  checks that the plan marks staging-capable.
- Repeat the same critical user journeys and visual checks used locally.
- Inspect staging logs, health, telemetry, migrations, queues, and background jobs where applicable.
- Keep test data identifiable and removable. Avoid destructive production-like data operations.
- Verify rollback prerequisites before declaring staging complete.

## Exhaustive but safe worktree cleanup

Cleanup begins only after the PR is merged, the canonical checkout has fast-forwarded successfully,
and any evidence that must survive has been attached or moved to a durable approved location.

1. Resolve the exact feature worktree path, branch, Compose project, containers, networks, volumes,
   temporary files, and evidence targets. Never use broad globs or unresolved variables.
2. Confirm the feature worktree has no uncommitted or untracked user work. If it does, stop and
   report it rather than forcing removal.
3. Stop the feature stack with the repository's documented Compose command and unique project name.
   Remove feature containers, orphans, and feature-only networks.
4. Remove feature-only anonymous and named volumes only when they are confirmed disposable and do
   not contain evidence or data the user asked to preserve. Never prune Docker globally.
5. Remove feature-specific temporary runtime files and generated secrets only when their ownership
   and recoverability are clear. Do not delete shared caches or credentials.
6. Remove the exact Git worktree through Git, then prune stale worktree metadata.
7. Delete the exact merged local feature branch. Delete the remote feature branch when the merge
   operation did not already do so and repository policy permits it.
8. Remove only task-created temporary directories outside the worktree. Never recursively clean a
   repository root, home directory, parent worktree directory, or shared Docker namespace.
9. Verify the worktree no longer appears, the branch is merged and absent as intended, feature
   ports are free, feature containers/networks/approved volumes are gone, the canonical checkout is
   clean apart from pre-existing unrelated files, and its HEAD matches the merged revision.
10. Report what was removed, what was deliberately preserved, and whether any retained artifact
    still needs manual cleanup.

Cleanup is independent of staging: staging deploys from the merged canonical revision or CI, not
from the removed feature worktree.
