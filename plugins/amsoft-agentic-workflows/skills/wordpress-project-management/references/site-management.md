# WordPress site-management workstream

Treat WordPress as an application, content system, presentation system, and operational system.
Classify the requested surface before choosing REST, wp-admin, browser, repository, or WP-CLI.

## Change classification

| Request | Compose | Minimum first question |
| --- | --- | --- |
| Page, post, CPT, copy, slug, status, or metadata | site management + content guard | Is this a draft, publication, or plan-only request? |
| Menu, navigation, footer, breadcrumb, or IA | site management + browser | Which menu/location/template owns the route? |
| Media, logo, crop, featured image, or asset | site management + source/provenance | Is the source approved and is replacement reversible? |
| Theme, template, block pattern, CSS, or responsive layout | site management + repository/CLI + browser | Which owning layer is authoritative? |
| Plugin, setting, form, SMTP, analytics, SEO, or Stream | specialist + site management + integration matrix | Is the state install, configure, connect, consent, collect, or verify? |
| Cache, cron, backup, database, core, or runtime | CLI + target/rollback gate | Which exact runtime and environment are authorized? |
| Release or incident | all required layers | What gate authorizes staging, production, publication, or rollback? |

## Content and pages

Before a write, resolve the stable object ID and record status, slug, parent, template, revision/
modified value, raw block or builder source, metadata, featured media, taxonomies, links, and
source-of-truth facts. Preserve uncertainty; do not invent prices, hours, locations, testimonials,
legal claims, translations, or SEO promises.

Use the content-as-code guard for enrolled objects. Otherwise follow the site-management REST
contract: discover the route/schema, send only intended fields, refetch immediately before write,
read back, and verify the correct authenticated or public surface. Keep drafts/private/noindex/
coming-soon state unchanged unless the publication gate is in scope.

## Information architecture and menus

Inventory menu identity/location, item IDs, labels, hierarchy, target URLs, custom links, active
states, header/footer/mobile/off-canvas variants, redirects, breadcrumbs, and route ownership.
Verify readback plus desktop/mobile rendering, deep links, logged-out behavior, keyboard focus,
accessible names, expanded/collapsed behavior, and touch targets when in scope.

## Media and source assets

Track source/provenance, attachment ID, dimensions, format, crop/focal point, responsive variants,
alt text, caption, credit, and every known reference. Prefer additive, reversible changes. Inspect
the image before creating purpose-based alt text. Never delete or replace an approved asset because
a newer file is merely available.

## Themes, templates, and blocks

Identify the active theme/child theme, Site Editor/templates/patterns/global styles, classic
customizer/widgets, builder templates, snippets, and repository ownership. Use the narrowest
owning layer and preserve the existing architecture. Do not use the production Theme File Editor
or Plugin File Editor, import a starter site, switch themes, reset global styles, or rewrite broad
CSS without explicit scope and rollback.

For visual changes, define affected routes, viewport matrix, focus/keyboard behavior, landmarks,
headings, contrast, alt text, overflow, console/network errors, layout shifts, and performance
conditions. An API response or screenshot alone is not rendered interaction proof.

## Plugins, settings, and integrations

Separate available, installed, active, configured, connected, consent-enabled, collecting/recording,
verified, and rolled-back states. Record dependencies, owning layer, mutable options, custom tables,
scheduled events, provider account, data flow, privacy/retention, duplicate-event risk, backup,
and verification surface. Do not apply a theme/plugin starter, option reset, or bulk import to a
site whose current state is not inventoried.

## Forms, SEO, privacy, and operations

Use safe non-sensitive form tests and provider/log evidence for email. Keep SEO facts/source,
canonical/indexing/robots/sitemap/schema, consent, privacy/legal ownership, and Stream policy in
their specialist contracts. A tag in page source does not prove consent or provider collection; an
audit plugin setting does not prove a supported event was recorded. Cache/CDN, cron, maintenance,
noindex, and error conditions must be recorded because they can hide or distort verification.

## Site handoff

Report object IDs/URLs, intended fields, source and remote state, browser surfaces, provider state,
cache/indexing delay, backup/rollback, unresolved facts, and separate plan/source/site/public/
collection states. Never claim a site is complete from JSON, HTTP 200, wp-admin, health, or CI alone.
