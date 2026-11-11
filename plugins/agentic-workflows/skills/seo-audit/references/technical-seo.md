# Technical SEO inspection

Apply to the requested page/template scope. Keep raw response, rendered DOM,
deployed response and search-engine data as distinct observations. Use existing
tools; if a required channel is unavailable, mark that check unassessed.

## Fetching, discovery and indexing

Inspect status codes, redirect destinations/loops, HTTPS, robots rules, robots
meta and `X-Robots-Tag`, declared canonical, sitemap membership and crawlable
internal links. Record which agent/rule and intended environment each control
applies to. Private/staging exclusions may be correct.

Robots disallow controls crawling. It is not a reliable removal mechanism;
Google needs to fetch a page to observe its `noindex`. A publicly fetchable 200
page with a canonical is only evidence of eligibility, not proof of indexing or
Google's selected canonical. Use authorized URL Inspection/indexing data for
observed state, retaining the inspection/crawl date. A `site:` query or absence
from a sampled result cannot establish a site's total indexed pages.
See [Google's noindex documentation](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
and [canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).

For sitemap work, parse the retrieved XML and distinguish sitemap indexes from
URL sets, following child sitemaps within budget. Compare listed URLs with
intended canonical/indexable pages; sample status, exclusions, redirects and
actual modification dates. A robots declaration or `/sitemap.xml` guess is not
proof of a valid retrieved sitemap. Keep discovery failures separate from
confirmed defects. Generate a requested draft from an authorized canonical URL
inventory; preserve exclusions and split using current
[sitemap requirements](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).
Submission and search-engine processing are separate states.

## Rendering and page experience

Compare response HTML with the rendered page for main text, titles, headings,
links, canonical/robots metadata, structured data and the intended action.
Inspect representative mobile and desktop states when relevant; record viewport,
consent/login state, interaction and errors. JavaScript use alone is not a defect.
Missing raw text can motivate a rendering check without proving a crawler failure.

Inspect image dimensions, reserved layout space, responsive sources, loading
behavior and useful alt text. Prioritize the measured bottleneck rather than
recommending a format or lazy-loading every image, including the main hero.
Test that navigation and the primary task remain usable after proposed changes.

For performance, retain URL, device, tool/version, conditions, timestamp and
metric source. Core Web Vitals use LCP, INP and CLS; read the current
[Web Vitals guidance](https://web.dev/articles/vitals) for thresholds and aggregation.
Separate URL-level field data from origin-level fallbacks and lab diagnostics.
A Lighthouse load test's TBT is not measured INP, and its score cannot establish
a field pass. With no field sample, report field status unknown and use lab work
to investigate causes. Tie suggested image/script/font/cache changes to evidence.

## Structured data

1. Inventory actual JSON-LD, Microdata or RDFa types and properties in the
   response/rendered page. Preserve `@id` relationships and conflicting blocks
   from templates/plugins. A found block is not necessarily valid.
2. Compare the entities, author/business identity, products, prices, currency,
   availability and reviews with visible, supported page facts. Do not invent
   missing values to satisfy a validator.
3. Separate parsing, Schema.org vocabulary validity, Google's feature-specific
   eligibility and observed search appearance. Use the applicable validator and
   [current feature guidance](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data);
   record which checks actually ran. Valid vocabulary alone does not establish
   rich-result eligibility, and a passing Rich Results Test does not guarantee display.
4. When requested, draft markup only for supported entities and visible facts;
   identify unresolved required properties and the page/template insertion point.
   Recheck the rendered candidate and deployed output for duplicate/conflicting
   markup through the existing implementation owner.

Refresh support before recommending a specific rich-result type. Distinguish
existing semantic markup from a promise of a Google feature; do not recommend
removal solely because a feature is unavailable. Follow
[structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).

Do not propose Google's Indexing API as a general page-submission shortcut. Its
[documented use](https://developers.google.com/search/apis/indexing-api/v3/using-api)
is restricted to eligible job-posting and livestream-event pages. Audit findings
do not authorize submissions, removals or robots/canonical changes.
