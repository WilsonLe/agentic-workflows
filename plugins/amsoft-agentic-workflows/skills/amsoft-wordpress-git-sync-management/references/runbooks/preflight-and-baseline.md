# Preflight, restore rehearsal, and baseline

## Entry criteria

- Named project/site/environment/owner and canonical HTTPS URL.
- Clean isolated repository worktree and reviewed adoption issue/plan.
- Read-only REST/runtime inventory channels; no onboarding mutation.
- Secret-safe credential references, backup owner/location/retention, and a
  disposable clone or staging environment approved for restore rehearsal.

## Procedure

1. Record repository SHA, WordPress/PHP/theme/plugin versions, target
   fingerprint, content and Site Editor inventory, media/extensions,
   classifications, caches/integrations, and evidence-channel availability.
2. Create the ownership/disposition matrix. Stop on ambiguous identity,
   unsupported plugin data, private payload, or missing source/rollback.
3. Take the provider/site-approved database/files snapshot outside Git. Restore
   it to the disposable target and verify identity, login, REST, media, and
   critical logged-out behavior. A backup without restore evidence is not ready.
4. Deploy the runtime through Git-owned DevOps source, activate it, register
   only reviewed objects/fields, and read the empty/current registry back.
5. Run `inventory`; review blocked exceptions and dependency graph. Do not use
   `--allow-read-only-exceptions` to hide a required adapter.
6. Run `baseline` only into an empty task-owned directory. Review object and
   lock hashes before committing public Git-safe content.

## Exit evidence and failure stop

Retain the inventory/manifest digests, restore rehearsal result, runtime and
source revision, registry readback, exception register, baseline diff, and
rollback identity. On any mismatch, remove only task-owned disposable output,
leave the source/live site unchanged, and return to ownership/adapters.
