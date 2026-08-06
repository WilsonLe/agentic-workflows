# WordPress DevOps and Content routing

Choose the plugin that owns the side effect. Installing both does not merge
their credentials or permissions.

| Request surface | Route | Authority and side effect |
| --- | --- | --- |
| Railway/DigitalOcean hosting, SSH, WP-CLI, plugin/theme lifecycle, filesystem, database/cache/runtime, deployment, or recovery | `wordpress-devops-management` | Provider target plus SSH; versioned infrastructure/source change and commit for mutations |
| Pages, posts, blocks, images, media, videos, user-facing design tokens, or rendered content | `wordpress-content-management` | Site-scoped Application Password reference; remote content change; no infrastructure commit |
| Runtime/theme/plugin implementation change plus page/media/design verification | Both | DevOps owns source/release/commit; Content owns content intent/readback/rendered verification |

DevOps may inspect content to prove runtime health, but it must not mutate a
page, post, media object, video, or user-facing design value. Content may
describe a desired token or verify a deployed theme, but it must not edit
source files, run WP-CLI/SSH, repair ownership, or change hosting.

## Handoff record

When composing both, keep these records separate:

- content contract identity, object IDs, fields, remote revision, publication
  state, and rendered evidence;
- DevOps contract identity, provider/SSH target, source revision, deployment
  identity, runtime/plugin/filesystem evidence, commit, and rollback; and
- the explicit dependency linking the DevOps release to the Content
  verification, without copying either secret or credential value.
