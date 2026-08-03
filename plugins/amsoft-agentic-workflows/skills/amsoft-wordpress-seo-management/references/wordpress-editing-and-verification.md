# WordPress editing and verification

## Prepare the change

Resolve the exact WordPress object by stable ID and canonical URL. Read it with edit context when
available and retain the title, slug, status, modified time, block source, excerpt, taxonomy, media,
author, relevant SEO metadata, and other fields needed for rollback. Preserve block and page-builder
markup; rendered HTML is not a lossless editing source.

Discover how the active SEO plugin stores and exposes title, description, canonical, robots, and
schema controls. If a field is absent from the REST schema, use the authenticated UI or stop; do not
guess a meta key or write directly to the database.

## Apply the smallest authorized edit

- Keep proposed new posts and substantial rewrites as drafts unless publication is explicit.
- Preserve the slug and canonical URL by default.
- Keep the site's established editor, blocks, reusable patterns, taxonomy, voice, and design system.
- Inspect an image before writing purpose-based alt text. Do not stuff keywords into alt text or
  duplicate nearby captions without a user need.
- Add internal links only when they help the reader; use descriptive natural anchors and confirm
  destinations.
- Keep structured data consistent with visible content and current feature requirements.
- Refetch immediately before saving. Stop if the modified timestamp or source differs unexpectedly.

Treat shared templates, redirects, noindex/canonical controls, navigation, taxonomies, SEO-plugin
settings, and bulk actions as higher-risk configuration, not ordinary copy edits.

## Verify in layers

1. Re-read the exact object and compare intended fields with the retained before state.
2. Open the preview or canonical public URL while logged out.
3. Inspect desktop and mobile rendering, headings, links, media, author/date, calls to action, and
   affected accessibility behavior.
4. Inspect the rendered title, meta description when present, canonical, robots directives,
   hreflang when relevant, and structured data. Account for SEO-plugin rendering and caches.
5. Confirm status code, redirect behavior, sitemap inclusion, and indexability only where the change
   affects them.
6. Use current official validators for eligible structured data and performance/experience checks;
   distinguish lab output from field data.
7. Report object ID, URL, draft/published state, checks performed, rollback route, cache or recrawl
   delay, and measurement annotation.

Do not request indexing merely to prove completion. Do not claim that a crawled or indexed page will
rank, or that a ranking movement was caused by the edit without a credible comparison.
