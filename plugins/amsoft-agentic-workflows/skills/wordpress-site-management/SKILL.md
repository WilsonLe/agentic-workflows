---
name: wordpress-site-management
description: Build, redesign, administer, and verify WordPress sites as an authorized administrator through the WordPress REST API and, when needed, the real wp-admin or public site UI. Use for WordPress onboarding, pages and posts, Gutenberg blocks, custom post types, taxonomies, media, menus, navigation, templates, themes, plugins, users, multilingual content, SEO, accessibility, performance, content architecture, responsive design, visual QA, and publishing when the user provides an administrator account credential such as a WordPress Application Password or an existing signed-in browser session.
---

# WordPress Site Management

Operate as an authorized WordPress administrator. Prefer the REST API for structured, auditable
content operations; use the real administrator UI for workflows the site exposes only through
wp-admin; use the public site for visual and behavioral verification. Route server, database,
filesystem, cache, core, or deployment work to `wordpress-cli-operations`.

For setup or first use, read [references/onboarding.md](references/onboarding.md). Never ask the
user to paste a password, Application Password, JWT, OAuth token, cookie, nonce, or API key into
chat. Use credentials already available through the process environment, secret manager, or an
existing signed-in browser session.

## Capability discovery

An “API key” is not a universal WordPress credential. Core WordPress commonly supports Application
Passwords over HTTPS; some sites use OAuth, JWT, hosting APIs, or plugin-specific authentication.
Identify the actual method and discover the site's REST index and endpoint schemas. Never assume
that administrator status makes a theme, plugin, menu, SEO, page-builder, or multilingual action
available through REST.

Before editing:

1. Confirm the canonical HTTPS base URL, environment, intended site, and authorization scope.
2. Discover `/wp-json/`, namespaces, content types, taxonomies, and the specific endpoint's allowed
   methods and schema.
3. Identify the editor and architecture: block or classic theme, Site Editor/templates, Gutenberg,
   classic editor, page builder, custom fields, custom post types, multilingual plugin, SEO plugin,
   caching, and deployment workflow.
4. Inventory the real content, navigation, reusable blocks/patterns, templates, theme settings,
   fonts, colors, spacing, breakpoints, imagery, and language variants before proposing a redesign.
5. Read the target with edit context where authorized and retain its ID, slug, status, modified
   time, content, metadata needed for rollback, and public URL.

Read [references/rest-api-patterns.md](references/rest-api-patterns.md) for authenticated REST work.

## Professional site-building workflow

Read [references/site-building.md](references/site-building.md) for builds and redesigns.

1. Convert the request into acceptance criteria for content, layout, behavior, accessibility,
   search, performance, languages, and responsive breakpoints.
2. Inventory and preserve the site's real design system and content model before changing it.
3. Work on staging for broad redesigns, page-builder migrations, template changes, or changes that
   affect shared components.
4. Back up or export the exact content/configuration being changed.
5. Implement the smallest coherent change using native blocks, patterns, templates, or the
   site's established builder. Do not mix editing systems casually.
6. Preserve URLs, metadata, translations, forms, analytics, consent, structured data, and
   integrations unless the user explicitly changes their scope.
7. Review the draft before publishing. A direct request to create or edit a scoped draft
   authorizes that draft; obtain confirmation before publishing a broad redesign or making a
   destructive, security-sensitive, or site-wide production change.
8. Re-fetch structured state and verify the actual rendered site at relevant desktop and mobile
   widths, logged out and with caches/CDN considered.

Do not invent legal claims, testimonials, opening hours, prices, credentials, organization facts,
translations, or SEO promises. Preserve uncertainty and use draft placeholders when facts are not
confirmed.

## Content and configuration discipline

- Prefer stable IDs and discover them; never guess post, term, media, menu, template, plugin, or
  user identifiers.
- Refetch immediately before writing and stop on an unexpected modified timestamp or content
  change. Do not overwrite another editor's work.
- Preserve block markup and page-builder metadata. Do not treat rendered HTML as a lossless source
  representation.
- Upload media deliberately with descriptive filenames, alt text based on the image's purpose, and
  appropriate dimensions. Do not fabricate alt text without inspecting the image.
- Keep drafts as drafts until publication is in scope.
- Treat plugin/theme installation, activation, deletion, updates, user/role changes, and site-wide
  settings as consequential. Inspect compatibility and rollback, then obtain confirmation.
- Never use the built-in Theme File Editor or Plugin File Editor for production development.
  Manage code through a versioned deployment workflow or `wordpress-cli-operations`.
- Never disable TLS verification or send application credentials over HTTP.

## Verification

API success is not visual proof. For every completed change:

- re-fetch the exact object or configuration and compare intended fields;
- open the canonical public preview or published URL;
- verify navigation, headings, links, media, forms, focus order, keyboard use, contrast, and
  responsive behavior affected by the change;
- test language variants and logged-out behavior where relevant;
- check for PHP, JavaScript, network, and visible layout errors using the available browser tools;
- capture visible desktop and mobile evidence for production visual work;
- report the final status, URL, object IDs, verification performed, and rollback or draft state.

Do not call a site build complete from JSON, an HTTP 200, or wp-admin alone.
