---
name: amsoft-wordpress-content-management
description: Manage authorized WordPress pages, posts, user-facing design systems and tokens, images, media, videos, and rendered content through a secret-safe Application Password contract without changing hosting or infrastructure.
---

# WordPress Content Management

Use this skill only for the user-facing WordPress content surface. It owns
pages, posts, user-facing custom content when the request explicitly includes
it, design-system values and design tokens exposed through the supported
WordPress editor or REST API, images, media-library objects, video embeds or
media, and the rendered result of those changes.

It does not own hosting, Railway, DigitalOcean, SSH, WP-CLI, databases,
caches, filesystem ownership, plugin/theme installation or activation,
runtime configuration, deployment manifests, infrastructure-as-code, or Git
commits. Route those concerns to `amsoft-wordpress-devops-management`. If a request
contains both surfaces, keep the content and DevOps actions as separate
workstreams and load both skills.

## Authentication and project contract

Use the [Application Password contract](references/application-password-contract.md)
before authenticated work. The credential is a WordPress Application Password
for one named site, not an arbitrary API key. Obtain it through an existing
approved local secret store or a secret-safe prompt. Never ask the user to
paste it into chat.

On macOS, use the user's Keychain-backed retrieval path (the system
`security` command or an equivalent local `getpass` prompt) and pass the value
only to the HTTPS request process. Never display command output containing the
value. Other platforms must use their OS credential store or an approved
secret manager.

The reusable contract stores the site identity and `credential_ref`, not the
Application Password. A project-specific contract may reference the reusable
record at the documented local path. Reuse is allowed only after rechecking
the canonical HTTPS URL, environment, username, endpoint, and authenticated
read capability. A project contract is not permission to write.

## Read-only discovery

1. Resolve the exact canonical HTTPS URL, environment, project/site key, and
   requested content scope.
2. Resolve the secret-free credential reference and authenticate without
   printing the Application Password, request headers, cookies, or nonce.
3. Read `/wp-json/` and discover namespaces, content types, taxonomies, media
   endpoints, editor features, and the exact methods needed for the task.
4. Inventory only the relevant pages, posts, media, video objects, templates,
   patterns, styles, fonts, colors, spacing, and responsive rules. Treat
   rendered HTML as evidence, not a lossless source for serialized blocks or
   page-builder data.
5. Resolve every target by stable ID and canonical URL. Capture the minimum
   rollback fields, modified timestamp, publication state, and current
   content before proposing a write.

Do not create a test post, upload a test asset, publish, change a token, or
alter a site setting during onboarding.

## Content operations

Use the site's discovered REST endpoint or the real authenticated administrator
UI for the smallest supported operation.

- **Pages and posts:** preserve IDs, slugs, status, authoring, taxonomies,
  block markup, custom fields, translations, metadata, links, and publication
  state. Keep new or substantially rewritten work as a draft unless the user
  explicitly authorizes publication.
- **Design system and tokens:** manage user-facing colors, typography,
  spacing, breakpoints, patterns, templates, and style settings through the
  supported editor/API surface when they are content-owned. If a token exists
  only in theme source, CSS, PHP, a build artifact, or a deployment manifest,
  stop and route the implementation to DevOps; Content may specify the desired
  user-facing result and verify it after release.
- **Images and media:** inspect the actual asset before assigning alt text;
  preserve source and license information; use deliberate filenames, MIME
  types, dimensions, captions, focal information, and associations. Do not
  invent image meaning or silently replace an existing asset.
- **Videos:** manage WordPress-hosted media or supported embeds, captions,
  poster/thumbnail relationships, titles, descriptions, and placement. Do
  not download or republish material without an authorized rights basis.

Refetch immediately before a write. Stop on an unexpected modified timestamp,
revision, object identity, endpoint capability, or publication state. Send
only the approved fields and read the exact object back after the write.

## Side-effect boundary

Content writes are remote content-surface changes. Content does not update
infrastructure-as-code, deployment manifests, theme/plugin source, hosting
configuration, or a Git branch, and they do not create a commit. Do not use a
content task to install or update a plugin, edit a PHP/CSS file, repair
filesystem ownership, change a cache, or modify a provider resource.

If the user asks for a content change plus a code or hosting change, split the
plan:

1. `amsoft-wordpress-content-management` owns the page/post/media/token intent and
   authenticated/public verification.
2. `amsoft-wordpress-devops-management` owns the infrastructure source, runtime
   change, deployment, and commit.
3. Re-run the Content readback and rendered checks after DevOps releases the
   user-facing implementation.

Do not infer that a content request authorizes publication, bulk edits,
deletion, a site-wide token change, or an infrastructure change.

## Verification

For every write, report separately:

- exact site, environment, object IDs, fields, and before/after revision;
- authenticated readback and the resulting publication/draft state;
- logged-out canonical URL behavior;
- affected desktop/mobile rendering, links, media, focus order, keyboard
  behavior, contrast, console/network errors, and language variants;
- cache/CDN or indexing limitations; and
- rollback or draft state.

API success, a saved wp-admin screen, a screenshot, or an HTTP 200 alone is
not proof of the requested user-facing result.

Read [routing-and-boundaries.md](references/routing-and-boundaries.md) when a
request may need both WordPress plugins.
