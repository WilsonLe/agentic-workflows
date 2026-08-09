# Waves, coexistence, and automation cutover

## Plan

Generate dependency-ordered waves after the canary passes. Keep each wave
within project limits and one independently recoverable unit per apply. Order
media/patterns/navigation/parts before referencing pages/templates; deploy
Git-owned code and ACF definitions before dependent content.

Declare one coexistence policy:

- editor changes allowed and reconciled through WordPress-origin PRs;
- a short named editor freeze during a bounded wave; or
- read-only observation while unsupported surfaces remain outside the contract.

## Execute and checkpoint

For each object: re-read, compare the lock, review diff, dry-run, apply with a
unique idempotency key, canonical readback, surface verification, and durable
checkpoint. Stop the wave on first unknown/failed state. Completed checkpoints
are not repeated; running/failed checkpoints require readback before resume.

## Automation cutover

After stable manual waves, enable the public-save queue consumer on a bot
branch. Prove debounce, autosave/revision exclusion, loop suppression,
duplicate/out-of-order handling, branch protection, least privilege, secret
masking, dead-letter/reconciliation, and per-site/environment concurrency.

Git-merge apply always fetches a fresh lock after merge and uses environment
approval. Do not reuse PR-time state or equate workflow success with rendered,
deployed, or published acceptance.
