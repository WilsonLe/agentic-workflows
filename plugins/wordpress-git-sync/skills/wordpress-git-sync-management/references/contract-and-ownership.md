# Contract and ownership

The synchronization unit is one managed WordPress object with one portable
identity and an explicit field allowlist. Environment database IDs and URLs
are provenance/mapping values, never portable identity.

Supported identities include posts/pages/CPTs, `wp_template`,
`wp_template_part`, `wp_navigation`, `wp_global_styles`, `wp_block` synced
patterns, attachments, ACF field groups, and declared ACF values. The object
records environment, ownership, managed and remote fields, canonical data,
references, provenance, state, classification, and tombstone status.

Ownership states are:

| State | Source and write rule |
| --- | --- |
| `git` | Executable/config source changes through reviewed Git delivery only |
| `wordpress` | Observed remote field; Git does not write it |
| `shared-guarded` | Git and WordPress may edit through base lock and atomic CAS |
| `manifest` | Git stores metadata and a binary locator, not an unbounded upload tree |
| `runtime-generated` | Excluded from source and writes |
| `read-only` | Inventory/diff only until a compatible adapter exists |
| `excluded` | Intentionally outside the managed project |

Canonicalization normalizes Unicode and line endings, sorts object keys,
rejects floats and secret-shaped fields, preserves array order and raw
Gutenberg markup, and hashes only the identity plus managed view. Unknown
fields, ownership collisions, numeric-only keys, ambiguous references, and
unsupported versions fail closed.

Locks are environment-specific observations, never secrets. They bind
project/site/environment/identity, serializer, managed fields, atomic guard,
remote revision/hash/time, and local hash. A lock from another site or
environment cannot authorize a write.

Use `"repository_root": "."` for a portable project contract and run the
helper from the repository root. The helper refuses a project document outside
the resolved root; automation also rejects absolute, escaping, or symlinked
input paths.

Private, restricted, draft, pending, and password-protected content bodies do
not enter Git exports. Keep them remote-owned/read-only unless an approved
non-Git content store and adapter is separately designed.
