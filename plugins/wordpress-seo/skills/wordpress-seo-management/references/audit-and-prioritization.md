# Audit and prioritization

## Audit layers

Sample enough URLs from each important template and content type to distinguish a page-level issue
from a systemic issue.

1. **Discovery and indexability:** status codes, robots controls, canonical targets, XML sitemaps,
   pagination, duplicate/parameter URLs, redirects, orphaning, soft errors, and index coverage when
   first-party data is available.
2. **Rendering and page experience:** mobile rendering, main-content availability, navigation,
   intrusive elements, accessibility, image behavior, and performance evidence. Separate lab
   diagnostics from field data.
3. **On-page communication:** descriptive title, one clear main heading, useful snippet candidate,
   intent alignment, scannable structure, media purpose, alt text based on the image's function,
   and accurate dates/bylines.
4. **Content quality and trust:** originality, completeness for the reader's task, first-hand
   experience, verified sources, author/reviewer context, factual maintenance, and transparent
   commercial intent.
5. **Architecture and internal links:** click paths, hubs, anchor clarity, broken links,
   cannibalization, taxonomy value, breadcrumbs, and paths to conversion.
6. **Structured data:** eligibility for a currently supported search feature, visible-content
   parity, required properties, factual accuracy, validation, and template-wide side effects.
7. **Business-specific surfaces:** local, product, image, video, multilingual, news, or other
   vertical requirements only when they apply.

Do not use a generic score as the sole diagnosis. Preserve the page evidence, sampling method, and
limits behind every finding.

## Prioritization model

Assign transparent ordinal ratings rather than invented precision:

- user value: low, medium, high;
- business fit: low, medium, high;
- evidence strength: weak, moderate, strong;
- likely SEO impact: low, medium, high;
- effort: small, medium, large;
- risk: low, medium, high;
- confidence: low, medium, high.

Sequence blockers and systemic defects first, followed by high-value existing-content improvements,
then original new content. Separate quick wins from foundational work and experiments. A high-impact
claim with weak evidence stays low confidence.

## Finding format

| Field | Requirement |
| --- | --- |
| Evidence | Observable page, WordPress, search, or first-party-data evidence |
| Scope | Exact URL(s), content type, template, language, device, and date |
| Consequence | User and search-discovery effect without rank guarantees |
| Recommendation | Smallest coherent correction |
| Verification | Readback, rendered check, validator, or measurement method |
| Priority | Ratings, dependencies, risk, and confidence |
