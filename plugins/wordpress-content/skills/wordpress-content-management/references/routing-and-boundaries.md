# WordPress Content and DevOps routing

Choose the smallest plugin that owns the requested side effect. Installing
both does not merge their permissions or make either credential valid for the
other.

| Request surface | Route | Authority and side effect |
| --- | --- | --- |
| Pages, posts, blocks, media, images, video embeds, user-facing design tokens, or rendered content | `wordpress-content-management` | WordPress Application Password reference; remote content/API/UI change; no infrastructure commit |
| Railway or DigitalOcean target resolution, SSH, WP-CLI, plugin/theme lifecycle, filesystem ownership, database/cache/runtime, hosting, deployment, or recovery | `wordpress-devops-management` | Provider account plus authorized SSH; infrastructure/source-of-truth change and commit when mutating |
| A plugin/theme/runtime change that must be checked against a page, post, media asset, or design system | Both | DevOps owns source, release, and commit; Content owns the content intent and authenticated/public verification |
| SEO research or audit | Content plus the separate SEO capability when installed | Content owns page/post/media changes; SEO owns search-specific research and measurement; DevOps is added only for runtime implementation |

## Mixed-task sequence

1. Classify each requested operation before asking for access.
2. Load Content only for user-facing content work and DevOps only for runtime
   or infrastructure work. Load both for a genuine cross-surface dependency.
3. Establish separate content and DevOps contracts. Do not use a provider or
   SSH credential for REST content access, or an Application Password for
   hosting access.
4. Keep separate change records, approvals, and verification. A DevOps commit
   does not prove content changed; a content readback does not prove the
   deployment or filesystem is healthy.
5. Report the two outcomes independently and stop at the first unavailable
   required surface.

## Explicit non-composition

Content must hand off when the requested fix requires a PHP/CSS/JS/theme/plugin
file, WP-CLI, SSH, a database, a cache, a filesystem owner/mode, a provider
resource, or an infrastructure/deployment manifest. DevOps must hand off when
the requested mutation is a page, post, block, image, media, video, or
user-facing design value. Do not hide a boundary crossing inside a generic
WordPress write.
