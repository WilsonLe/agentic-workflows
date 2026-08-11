# CLI and runtime

Run the helper from the plugin root:

```text
python3 <plugin-root>/scripts/wp_content_sync.py validate --kind project --input <project.json>
python3 <plugin-root>/scripts/wp_content_sync.py inventory --project <project.json> --output <inventory.json>
python3 <plugin-root>/scripts/wp_content_sync.py pull --project <project.json> --object <type:key> \
  --output <object.json> --lock-output <lock.json> --verify-remote
python3 <plugin-root>/scripts/wp_content_sync.py status --project <project.json> --object <type:key> \
  --source <object.json> --lock <lock.json>
python3 <plugin-root>/scripts/wp_content_sync.py diff --project <project.json> --object <type:key> \
  --source <object.json> --lock <lock.json>
python3 <plugin-root>/scripts/wp_content_sync.py plan --project <project.json> --object <type:key> \
  --source <object.json> --lock <lock.json>
```

Apply is dry-run by default:

```text
python3 <plugin-root>/scripts/wp_content_sync.py apply --project <project.json> --object <type:key> \
  --source <object.json> --lock <lock.json> \
  --expected-remote-sha256 <lock-hash> --expected-remote-revision <lock-revision> \
  --require-atomic-check --idempotency-key <stable-key> --approval-id issue-<number>
```

Only append `--execute` after a fresh pull/status, reviewed diff and dry-run,
exact object/environment approval, current rollback evidence, and verification
channel preflight. The helper reads a credential through the project contract's
Keychain, protected-file, or native masked prompt reference. It never accepts
the Application Password in argv or environment values.

The runtime exposes `/wp-json/amsoft/v1/registry`, managed object readback,
CAS apply, and a bounded save-event queue. It locks the idempotency journal and
registered post row, checks the expected hash/revision and exact registered
ownership contract inside the database transaction, writes only declared
fields after WordPress capability checks, reads back canonically, journals the
idempotency key, and then commits. External hook/provider side effects are
outside the transaction and must be reconciled separately.

An interrupted or transport-failed write has unknown outcome. Re-read by
identity and idempotency key; never retry blindly.
