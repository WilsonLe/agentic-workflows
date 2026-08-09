# One-object canary

## Eligibility

Choose exactly one public, low-risk, dependency-light object with a stable
identity, supported adapter, registered blocks, reviewed managed fields,
available editor/public verification, and narrow rollback source. Do not use a
private/draft page, global styles, checkout, form, authentication, or broad
navigation as the first canary.

## Procedure

1. Fetch fresh edit-context source and compute the canonical hash/revision.
2. Store the minimum rollback fields and exact raw source outside Git. Record
   snapshot digest/location/owner without copying its content to the issue.
3. Review the native-block target and its hash. Stop on `core/html`, invalid or
   missing blocks, unsupported meta/builder data, or changed dependencies.
4. Run `status`, `diff`, `plan`, and dry-run `apply` with the current lock.
5. Obtain the exact environment/object apply approval. Re-run the fresh remote
   check, then execute with atomic guard and one idempotency key.
6. Verify canonical REST readback and new lock. Open/save/reload safely in the
   editor, then check the correct authenticated/private or logged-out public
   surface, responsive layout, keyboard/focus, media, links, console/network,
   cache, and publication state.
7. Rehearse the narrow content rollback through the same guard and verify it;
   reapply only with a new approval if the canary is intended to remain.

Unknown apply outcome, hash drift, missing snapshot, unavailable browser,
failed rendering, or rollback mismatch stops the next object. Record the
checkpoint as blocked pending reconciliation; never blind retry.
