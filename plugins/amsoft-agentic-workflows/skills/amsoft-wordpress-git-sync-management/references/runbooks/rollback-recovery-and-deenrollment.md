# Rollback, recovery, and de-enrolment

## Incident response

1. Stop further queue consumption and applies; preserve the first error,
   correlation/idempotency identity, current lock, and target fingerprint.
2. Re-read WordPress and Git. Classify contract, content, Site Editor, code,
   media, extension, automation, runtime, rendering, or provider failure.
3. Reconcile unknown writes by readback; never retry solely from a timeout.
4. Obtain the applicable content, code, runtime, database, or provider rollback
   approval and recover the narrowest unit.
5. Verify canonical, editor/rendered, runtime/deployment, and provider surfaces
   independently. Record residual drift and a resume or repair-forward plan.

## De-enrolment

De-enrolment is not deletion. Disable automation, drain/reconcile the queue,
record final Git/WordPress hashes, choose the continuing source of truth,
remove the object's registry entry through a reviewed runtime change, and
retain locks/evidence according to policy. Do not delete posts, media,
snapshots, Git history, plugin data, runtime options, or the source environment
without a separate destructive authorization and tested recovery path.

Uninstalling the runtime retains registry/journal/queue data by default. A
later destructive cleanup must name exact option/table/file targets and prove
that no retained rollback or audit evidence depends on them.
