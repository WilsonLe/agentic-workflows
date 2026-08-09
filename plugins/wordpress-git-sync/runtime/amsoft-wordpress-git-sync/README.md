# AMSoft WordPress Git Sync runtime

This WordPress plugin supplies the server-side managed-object registry and
atomic compare-and-swap boundary used by `wp-content-sync`.

The runtime supports WordPress 6.6–6.9 and PHP 8.1–8.4. Install and activate it
through the site's reviewed Git-owned deployment lane. Activation creates only
the empty registry, idempotency journal, and event queue options. It never
enrols content, sends GitHub requests, publishes, or deletes data by itself.

Each managed object must be registered by an administrator with one stable
logical key and an explicit field ownership map. Apply requests enforce the
post type's edit/publish/term/meta capabilities, lock the idempotency journal
and registered post row, compare the expected revision and canonical SHA-256,
write only declared fields inside a database transaction, then perform
canonical readback before commit. Adapter identity fields remain read-only,
and ACF field groups stay in the Git-owned code lane. The database transaction
does not make external hook side effects atomic; the API reports that boundary
explicitly.

WordPress editor saves for public managed objects enter a bounded local queue.
The reviewed GitHub automation consumes those events. Autosaves, revisions,
private content, and bot applies do not create feedback events.

Uninstall retains registry, journal, and queue state. Destructive removal is a
separate operator decision covered by the adoption/de-enrolment runbook.
