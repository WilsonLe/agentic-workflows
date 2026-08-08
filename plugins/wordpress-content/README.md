# WordPress Content

AMSoft's content-only WordPress operations plugin.

## Boundary

This plugin manages user-facing WordPress content: pages, posts, user-facing
design systems and design tokens exposed by the site's supported editor or
REST surface, images, the media library, video embeds or media, and the
rendered experience affected by those objects.

It does not manage hosting, SSH, WP-CLI, databases, caches, filesystems,
WordPress plugin or theme installation/activation, provider resources, or
infrastructure-as-code. Route those requests to **WordPress DevOps**. A task
that changes a plugin/theme implementation and then needs a content review
uses both plugins: DevOps owns the source and release; Content owns the
user-facing content and rendered verification.

## Block-first content contract

New and refactored content never uses the WordPress Custom HTML block
(`core/html`) or another raw-HTML workaround. The workflow first reuses a core
or site-registered block, then uses a synced or unsynced pattern composed from
registered blocks when the structure repeats. If the editor lacks a real
component, Content stops the write and gives WordPress DevOps a registered
block requirement instead of inserting temporary HTML.

Existing Custom HTML is treated as bounded migration input. Its exact raw
edit-context source and rollback fields are preserved while one stable object
at a time is mapped to registered blocks, patterns, or a separately released
block. The target must parse, contain no `core/html`, survive an editor
save/reload round trip, and pass rendered, responsive, and accessibility checks.
Rendered HTML is verification evidence, never serialized block source.

## Authentication contract

The content workflow uses a site-scoped WordPress Application Password over
HTTPS. It records only a reference to the approved local secret store in a
content-auth contract. On macOS, the reference may resolve through the user's
Keychain using the system `security` retrieval path or a local `getpass`
prompt; the secret value is never printed, placed in Git, or written into the
contract. A project-specific contract reuses the reference after rechecking
the canonical URL, environment, username, and read capability.

Do not paste an Application Password, cookie, nonce, token, or authorization
header into chat.

## First prompt

```text
Use WordPress Content to onboard my named site with its existing local Application Password reference, verify read-only access, and inspect pages, posts, media, and design tokens without changing infrastructure.
```

All writes require an exact object, a fresh raw edit-context read, a bounded
field diff, the required publication approval, block/editor validation, and
readback plus rendered verification.
