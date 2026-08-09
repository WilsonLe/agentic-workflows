# Entity adapters

## Posts, pages, and CPTs

The adapter preserves raw Gutenberg block markup, title/excerpt raw values,
slug, status, dates, parent/author logical references, taxonomy terms,
registered meta, featured-media reference, and template only when each field
is declared. Unknown registered blocks are preserved losslessly. `core/html`,
invalid blocks, unsupported builder payloads, protected meta, comments,
revisions, and autosaves are not normalized into a target.

CPT support requires an allowlisted REST-visible post type. Status changes
toward greater visibility need a separate publication approval.

## Site Editor

`wp_template`, `wp_template_part`, `wp_navigation`, `wp_global_styles`, and
`wp_block` are database entities with theme/slug or logical identities.
Dependency order is pattern/navigation → parts → templates → global styles.
Theme file defaults remain Git-owned; database customizations keep origin and
active-theme identity so operators can choose adopt or reset rather than
silently shadowing a release.

The runtime treats adapter identity fields as read-only dependencies:
`post_type` for CPTs, `theme` for Site Editor records, `sync_behavior` for
synced patterns, and `target_ref`/`field_group_refs` for ACF values. ACF field
groups themselves use the reviewed Git-owned code lane. Template-part `area`
is writable; registered post meta is writable only through an exact allowlist
of WordPress-registered meta keys.

Synced patterns remain `wp_block` objects. Unsynced pattern insertions are
ordinary block content in their owning post. Do not flatten a reusable pattern
to rendered HTML.

## Unsupported data

Builders, options, custom tables, serialized values, and unregistered meta are
read-only until a versioned adapter proves round-trip behavior, capability,
size, rollback, and compatibility. An adapter warning cannot authorize a
best-effort write.
