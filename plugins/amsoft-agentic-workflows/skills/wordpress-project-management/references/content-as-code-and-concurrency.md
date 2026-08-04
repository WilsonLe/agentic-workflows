# Content as code and concurrency

Content-as-code mode is opt-in, object-scoped, field-scoped, and environment-scoped. It does not
version-control the whole WordPress database. The repository source, the remote CMS, and provider
state remain separate sources of truth until a guarded apply succeeds.

## Managed representation

For each enrolled object, record post type, stable WordPress ID, canonical URL/key, managed fields,
remote-owned fields, serializer version, environment, source file, and remote baseline lock.
Preserve Gutenberg serialized block markup or REST edit-context raw content; rendered HTML is not a
lossless source. Add a round-trip adapter for builders/custom fields or keep those fields read-only.

Suggested secret-free paths:

~~~text
content/wordpress/<site>/<object-key>.json
content-locks/<site>/<environment>/<object-key>.json
~~~

The lock contains identity, serializer, revision, modified value, canonical checksum, fetch time,
and guard capability. Never put credentials, cookies, nonces, authorization headers, private form
values, or unrelated exports in it. See [content-lock-v1.json](../examples/content-lock-v1.json)
and [content-lock-v1.schema.json](../schemas/content-lock-v1.schema.json).

## Proposed sync/apply interface

`wp-content-sync` is a proposed repository/remote adapter contract, not a command guaranteed to be
installed. The agent must prove an implementation exists before invoking it. Its adapter must use
the discovered REST/WP-CLI runtime and exact multisite URL, never guessed SSH or Compose values.

~~~text
wp-content-sync pull --target <site> --environment <env> \
  --object <post-type>:<id> --output <content-file> --lock-output <lock-file> \
  --verify-remote

wp-content-sync status --target <site> --environment <env> \
  --object <post-type>:<id> --verify-remote

wp-content-sync diff --target <site> --environment <env> \
  --object <post-type>:<id>

wp-content-sync apply --target <site> --environment <env> \
  --object <post-type>:<id> --source <content-file> \
  --expected-remote-sha256 <sha256> --expected-remote-revision <revision> \
  --require-atomic-check --dry-run
~~~

`pull`, `status`, and `diff` are read-only. They must use edit context, canonicalize only the
managed fields, calculate SHA-256 over canonical UTF-8 JSON, report local/remote/both-changed
state, and refuse to overwrite a locally changed file or lock without explicit conflict
resolution. No sync check may create, publish, alter, or purge anything remotely.

The required pre-write sequence is:

The agent must perform a fresh remote sync/check immediately before every write to an enrolled
object, even if a pull occurred earlier in the session.

1. Run `wp-content-sync pull ... --verify-remote` against the exact target immediately before the
   write, even if a pull occurred earlier in the session.
2. Review the bounded managed-field diff and confirm that the returned remote checksum and revision
   are the expected lock values; otherwise stop for reconciliation.
3. Run `wp-content-sync apply` with those expected values and `--require-atomic-check`. A reviewed
   `--dry-run` may precede it, but the real apply must retain the same expectations and perform its
   own conditional check as part of the write.

The apply operation must refuse missing expected checksum/revision, compare the current remote
state, send only the managed allowlist, re-fetch, verify the desired checksum, and record the new
observation.

## Concurrency guard

Distinguish:

- `atomic-compare-and-swap`: the remote adapter rejects a changed baseline as part of the write;
- `best-effort-preflight`: separate read/compare/write with a residual race;
- `unavailable`: no trustworthy guard.

Production and shared staging strict applies require `atomic-compare-and-swap`. A separate GET,
checksum comparison, and ordinary REST/WP-CLI update is not an atomic guarantee. If only that
fallback exists, pull/diff/plan are allowed but the write is `blocked`. Do not add a must-use
plugin, database mutation, endpoint, or remote helper implicitly; any server-side compare-and-swap
adapter needs its own reviewed runtime, security, backup, and rollback contract.

## Conflict and bypass rules

Stop before writing when the remote checksum/revision, object identity, local source/lock,
serializer, authorization, target fingerprint, managed-field mapping, publication state, or guard
capability differs or is unknown. Report the exact conflict, pull the latest state, show a bounded
diff, and require content-owner reconciliation. Never use `--force`, auto-rebase, recreate a
missing object, or choose local/remote silently.

An enrolled object may not be written through raw REST, direct `wp post update`, menu/term/custom
field commands, wp-admin, a builder, a custom endpoint, bulk import, or search-replace. Those paths
are read-only or outside the strict contract unless they expose the same conditional guard.

For a batch, preflight every object before the first write. If atomic batch behavior is unavailable,
use independently reversible units and report partial-apply risk; one object per apply is safest.

## Review and verification

Content PRs show the source diff, managed-field allowlist, object IDs, environment, baseline
revision/checksum, redacted sync/diff evidence, publication state, verification surfaces, and
rollback. Merge is not apply. A release repeats the sync and atomic guard against the target
environment immediately before writing. After apply, verify object identity, desired checksum,
revision, authenticated/private or logged-out/public rendering, cache/indexing/provider limits,
and the new environment-specific lock.
