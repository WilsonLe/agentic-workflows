# Professional WordPress site-building workflow

## Discovery

Inventory before design:

- site purpose, audiences, primary actions, content owners, languages, and success criteria;
- URLs, page hierarchy, post types, taxonomies, menus, search, forms, ecommerce, membership, and
  integrations;
- classic/block theme, Site Editor templates, child theme, Gutenberg patterns, page builder,
  custom fields, and deployment ownership;
- existing colors, typography, spacing, layout widths, components, imagery, breakpoints, and
  accessibility constraints;
- analytics, consent, SEO metadata, redirects, structured data, caching, CDN, and performance
  budget.

Do not copy a reference site or replace the current design before extracting the target site's
real constraints and reusable tokens.

## Architecture

Prefer native WordPress primitives that match the existing architecture:

- semantic content in posts, pages, custom post types, taxonomies, and fields;
- shared presentation in theme styles, templates, template parts, patterns, or established builder
  components;
- content editors should not need to edit fragile raw HTML for routine updates;
- custom functionality belongs in a versioned plugin or theme workflow, not ad hoc production
  editor snippets.

Keep content, presentation, behavior, and environment configuration separated.

## Implementation

1. Establish staging and rollback.
2. Define a small token set for typography, colors, spacing, widths, radii, and interaction states.
3. Build shared header, navigation, footer, buttons, cards, forms, and content patterns before
   duplicating page-specific layouts.
4. Use semantic headings, landmarks, labels, link text, focus styles, and meaningful image
   alternatives.
5. Preserve confirmed content and mark unconfirmed content explicitly.
6. Optimize media and avoid unnecessary plugins, blocking assets, or duplicated builder systems.
7. Review drafts with the user before site-wide publication.

## Acceptance

Verify:

- canonical desktop and mobile layouts, plus intermediate widths;
- keyboard navigation, visible focus, labels, errors, contrast, zoom, and reduced-motion behavior;
- menus, internal/external links, forms, search, authentication, checkout or other critical flows;
- titles, descriptions, canonical URLs, indexability, sitemap, redirects, and structured data in
  the scope of the change;
- real language variants rather than automatic translation presented as approved copy;
- logged-out production behavior after page, object, CDN, and browser caches;
- rollback artifacts and ownership for post-launch monitoring.

Use visible screenshots or video when the user requests visual proof. JSON, source changes, or a
successful deployment command are not substitutes for rendered evidence.
