# WordPress content surfaces and design system

Inventory the actual site before changing it. The same visual outcome may be
owned by a page/post block, a reusable pattern, Site Editor styles, a theme
token, a page builder field, a media attachment, or deployed theme code. Do
not flatten these sources into rendered HTML and assume it is reversible.

For page, post, template, or pattern authoring, follow
[block-first-authoring.md](block-first-authoring.md). Never use Custom HTML as
the implementation strategy for new or refactored content. Prefer an existing
registered block, then a pattern composed from registered blocks, then a
separately implemented registered block when a genuine component gap remains.

## Content inventory

For the requested scope, capture:

- page or post type, stable ID, slug, canonical URL, status, author, language,
  taxonomies, modified time, and revision state;
- raw/edit-context content and only the custom fields required by the task;
- the parsed block tree, registered block types and variations, pattern and
  reusable references, invalid or unsupported blocks, and every legacy
  `core/html` occurrence;
- links, navigation relationships, forms, SEO fields, structured data, and
  integrations that are visibly or functionally affected;
- media IDs, source files, MIME type, dimensions, captions, alt text, focal
  information, license/provenance, and every affected association; and
- video source/rights basis, embed or attachment ID, captions, poster, title,
  description, and responsive behavior.

## Design system and tokens

Treat user-facing design as content-owned when the site's supported REST/UI
surface exposes it as styles, templates, patterns, global settings, or
editable token values. Record the exact token name, before value, intended
value, scope, breakpoint, language, and affected objects. Check contrast,
font loading, spacing, layout, focus states, and mobile behavior.

If the value is only in a source-controlled CSS/PHP/JSON build input, compiled
asset, theme package, plugin package, or deployment manifest, do not edit it
from this skill. Return a DevOps handoff containing the desired token change,
affected user-facing surfaces, and required rendered checks.

## Preservation rules

- Keep existing URLs, IDs, translations, structured data, forms, analytics,
  consent, and integrations unless explicitly changed.
- Preserve the intentional semantics of registered Gutenberg blocks, patterns,
  builder metadata, and media associations. Legacy Custom HTML is migration
  input, not a target to preserve in refactored content. Rendered DOM is not a
  source-of-truth replacement.
- Do not copy rendered HTML into post content or disguise raw HTML in a generic
  block or unrelated attribute. HTML emitted by a registered block through its
  supported serialization or render callback remains valid.
- Inspect an image before assigning descriptive alt text. Do not infer
  subjects, ingredients, people, claims, or accessibility meaning from a
  filename alone.
- Keep new and substantially rewritten content as drafts unless publication
  is explicitly in scope.
- Do not copy competitor prose, images, distinctive layouts, or unlicensed
  video.
