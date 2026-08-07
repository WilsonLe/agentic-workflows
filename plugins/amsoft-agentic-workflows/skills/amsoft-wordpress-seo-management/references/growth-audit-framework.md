# SEO and growth audit framework

Use this framework when the request is a full SEO audit, an SEO growth audit, a competitor
review, or a content-gap study. The output is an evidence chain and an action roadmap, not a
single SEO score, a ranking forecast, or a promise of traffic or revenue.

## Define growth before collecting evidence

Translate “growth” into a measurable business path before looking for topics:

1. **Discovery:** qualified search impressions, clicks, search appearances, and new audiences.
2. **Engagement:** a visitor completes the page task, explores a relevant next page, uses site
   search, or reaches a decision point.
3. **Conversion:** the agreed key event, lead, booking, enquiry, purchase, call, or other
   business action occurs.
4. **Return or retention:** a repeat visit, subscription, saved resource, or other legitimate
   relationship outcome when the business actually measures it.

Choose one primary business outcome and the smallest useful set of leading indicators. Record the
baseline date range, comparison period, timezone, attribution caveats, and observation window.
Keep these categories separate:

- `observed`: directly read from WordPress, an authorised first-party property, a public page, or
  a bounded search observation;
- `estimate`: supplied by a third-party tool or rounded/limited source;
- `hypothesis`: a proposed explanation or expected change that still needs testing.

Organic clicks are not conversions, rankings are not revenue, and a competitor's visibility is not
proof that the same opportunity will work for this site.

## Phase 0: create the audit charter

Read [onboarding-and-access.md](onboarding-and-access.md) first. Record the canonical HTTPS site,
environment, market, language, audience, offerings, excluded topics, priority conversions,
seasonality, editorial capacity, reviewer, approval owner, and requested mode. If a fact is
unknown, mark it as unknown and continue with a smaller evidence set; never fill the field with a
guess.

Return readiness for:

| Surface | Readiness question |
| --- | --- |
| Public site | Can the logged-out pages, robots response, sitemap, and representative templates be inspected? |
| WordPress | Is read access available, and are the required content types and fields actually exposed? |
| First-party search | Is Search Console or Bing evidence available for the named property and date range? |
| First-party behaviour | Are Analytics, internal search, key events, or other approved behaviour signals configured? |
| Competitors | Can relevant competitors be validated from public evidence without bypassing controls? |
| Content work | Is a reviewer and a separate draft/publication route known? |
| Measurement | Is there a rollback, annotation, and post-change verification route? |

Use `Ready`, `Needs input`, `Needs configuration`, or `Not selected`. A missing first-party
source narrows what can be concluded; it does not justify invented demand, traffic, or conversion
metrics.

## Phase 1: establish the site's baseline

Inventory the site before proposing new content. Join the following where possible by canonical
URL:

- WordPress content type, ID, URL, slug, status, title, heading, dates, taxonomy, author,
  excerpt, media, internal links, and relevant SEO fields;
- public response status, redirects, robots directives, canonical, sitemap inclusion, visible
  structured data, page template, mobile/desktop rendering, accessibility, and lab or field
  performance evidence;
- Search Console or Bing query/page data with market, device, search type, date range, row limit,
  aggregation, privacy omissions, and freshness recorded;
- analytics landing pages, paths, internal-search terms, and approved key events, with consent,
  attribution, timezone, and configuration limits recorded;
- the conversion path from an organic landing page to the next legitimate action.

Sample each important template and content type. Mark a finding as systemic only when the sample
supports a template-level conclusion. Treat a Search Console row as bounded evidence: Search
Analytics returns top rows subject to internal limits and is not a complete query or demand census.

## Phase 2: identify and qualify competitors

Do not begin with a competitor list copied from a directory. Build a candidate ledger from three
separate lenses:

1. **Commercial competitors:** businesses offering a similar product or service to the same
   audience and market.
2. **Search competitors:** domains that repeatedly appear for the site's validated query families
   or reader tasks in a bounded, locale-specific search sample.
3. **Audience alternatives:** publishers, directories, marketplaces, forums, tools, or other
   resources that solve the same reader task even when they are not direct businesses.

For every candidate, record:

| Field | Required evidence |
| --- | --- |
| Candidate and lens | Business, search, or audience alternative; do not collapse the categories |
| Audience and market fit | The same people, geography, language, or service area where relevant |
| Reader-task overlap | The question, problem, or decision the candidate helps complete |
| Public evidence | Search observation, canonical page, sitemap/feed, navigation, or supplied fact |
| Coverage relevance | Why its content is comparable to the site's opportunity |
| Decision | Include, hold, or decline, with a reason and date |
| Limits | Personalisation, sample size, incomplete inventory, estimate, or other uncertainty |

Validate supplied competitors against the same ledger. A large publisher, marketplace, or search
feature may be a useful format or audience alternative without being a direct business competitor.
Use the smallest bounded set that answers the decision, often three to five validated candidates,
and explain exclusions. Do not treat a domain as relevant merely because it shares a keyword.

## Phase 3: research each validated competitor (per-competitor pass)

Run the same bounded pass for every included competitor so comparisons are fair. Prefer public
`sitemap.xml` or sitemap indexes, RSS/Atom feeds, canonical pages, navigation, and a limited set of
representative URLs. Use a manual search sample to classify intent and result format. Use Common
Crawl only for historical URL evidence or coverage patterns, never as proof of current traffic,
ownership, indexing, or accuracy.

For each competitor, collect:

- representative URLs by reader task and journey stage;
- page/content type, apparent freshness, author or reviewer context, sourcing, media, visible
  interactive tools, internal-link patterns, calls to action, and conversion path;
- the useful outcome the page provides, the evidence or first-hand contribution it adds, and the
  parts that are thin, unclear, stale, inaccessible, or unsupported;
- observed search-result format, locale, device, date, and visible competitors for the matching
  task;
- independent need evidence from the site's own data, customer/support questions, Google Trends,
  Bing Keyword Research, or another explicitly labelled source;
- access method, source URL, collection date, evidence type, row/page limit, and coverage gaps.

Never scrape result pages, autocomplete, dashboards, or competitor sites at scale. Do not bypass a
login, paywall, bot protection, robots restriction, rate limit, or other technical control. Do not
collect personal data or reproduce substantial competitor content.

## Phase 4: compare reader tasks and classify gaps

Compare what the reader can accomplish, not heading strings, word counts, keyword density, or a
competitor's page count. Use one row per task or topic cluster:

| Field | Required content |
| --- | --- |
| Reader and task | Audience, journey stage, question, problem, or decision |
| Intent and need evidence | Dominant/mixed intent plus first-party, observed, open-data, or estimated support |
| Current site coverage | URL(s), status, current performance, intent match, and conversion role |
| Competitor coverage | Each relevant competitor URL and the useful outcome it provides |
| Gap class | Coverage, depth, experience, format, trust, journey, source, or technical/indexability |
| Missing value | The specific unanswered subtask, proof, example, media, tool, or path to action |
| Originality angle | What this site can contribute from verified facts, first-hand experience, data, or service capability |
| Recommended action | Keep, refresh, consolidate, redirect-plan, create, or decline |
| Cannibalisation check | Existing URL role and why a new URL is or is not justified |
| Priority evidence | User value, business fit, evidence strength, likely impact, effort, risk, confidence |

A competitor topic alone is not a content gap. Treat a gap as supported only when all of the
following are true:

1. It represents a real audience need or business-relevant reader task.
2. The current site has no useful answer or has a material weakness for that task.
3. The site can add a credible, original contribution that fits its purpose and expertise.
4. The evidence and limits are recorded well enough for a reviewer to challenge the conclusion.

Classify the missing value precisely:

- **Coverage:** no useful answer exists for a relevant task.
- **Depth:** an existing answer omits steps, evidence, edge cases, or decision support.
- **Experience:** competitors summarise, while the site can add tested examples, original data,
  demonstrations, or operational knowledge.
- **Format:** the task needs a comparison, checklist, calculator, image set, video, glossary,
  location page, or tool rather than another generic article.
- **Trust:** sourcing, authorship, review, maintenance, or commercial context is insufficient.
- **Journey:** the page attracts interest but does not help the reader take the next legitimate
  step.
- **Source:** a claim needs a better current, authoritative, or first-party source.
- **Technical/indexability:** the useful answer exists but discovery, rendering, canonical,
  sitemap, or status evidence blocks it.

## The “same thing, better” originality gate

“Better” means better for the reader's task, not a longer or cosmetically similar copy. A valid
improvement can add one or more of:

- verified first-hand experience, testing, examples, or original analysis;
- more accurate, current, local, or transparent facts;
- clearer decision support, comparisons, caveats, or practical steps;
- a more accessible, faster-to-understand, mobile-friendly page experience;
- a useful tool, image, video, table, checklist, or other appropriate format;
- trustworthy authorship, review, sourcing, maintenance, and commercial disclosure;
- a natural internal-link and conversion path that helps the reader act.

Reject an opportunity when the proposed value is only to copy competitor prose, headings, order,
images, data, distinctive creative expression, or unverified claims. Do not prescribe a word count,
keyword density, mass-produced pages, fake reviews, link schemes, doorway pages, or content made
only to attract search visits.

## Phase 5: prioritize the growth backlog

Write each opportunity as a testable growth hypothesis:

> Because **[evidence]**, if we **[smallest coherent change]** for **[audience/task]**, then
> **[leading indicator or user behaviour]** may improve and could contribute to **[business
> outcome]**. We will observe **[metrics]** against **[baseline]** for **[window]**, subject to
> **[limits and competing changes]**.

Use ordinal ratings, not invented precision:

- user value: low, medium, high;
- business fit: low, medium, high;
- evidence strength: weak, moderate, strong;
- likely SEO impact: low, medium, high;
- effort: small, medium, large;
- risk: low, medium, high;
- confidence: low, medium, high.

Sequence the backlog as:

1. discovery/indexability or trust blockers affecting important existing URLs;
2. high-value existing pages with strong evidence of query mismatch, decay, weak page experience,
   or a broken conversion path;
3. consolidation or internal-link improvements where the site already has authority for the task;
4. validated competitor/content gaps with a credible original contribution;
5. lower-confidence experiments that have an explicit measurement and stop condition.

Do not turn ordinal ratings into a synthetic universal score. A high-impact label with weak
evidence remains low confidence and should usually be researched before implementation.

## Phase 6: return the audit packet

Use [growth-audit-report-template.md](growth-audit-report-template.md) and include:

1. executive summary, scope, assumptions, and blocked inputs;
2. readiness and evidence coverage with collection dates and limits;
3. technical, on-page, architecture, trust, local, media, and page-experience findings;
4. the validated competitor ledger and one research summary per competitor;
5. the reader-task/content-gap matrix and declined opportunities;
6. a now/next/later roadmap tied to business outcomes and owners;
7. original content briefs or refresh briefs for the highest-priority items;
8. internal-link, structured-data, media, and conversion-path recommendations where supported;
9. measurement baseline, annotation, observation window, and refresh triggers;
10. risks, dependencies, and explicit “not known” statements.

An audit, comparison, recommendation, or plan is read-only. Route page/post/media/design changes
to the WordPress Content workflow, and route server, database, cache, redirect, WP-CLI, plugin,
theme, or deployment work to the WordPress DevOps workflow. Keep new or substantially rewritten
content as a draft unless publication is separately authorised. Refetch immediately before any
write, preserve rollback state, verify the rendered result, and never claim ranking or revenue
improvement before comparable post-change evidence exists.

## Research basis

The framework combines current primary guidance with bounded, tool-agnostic competitive research:

- [Google Search Essentials](https://developers.google.com/search/docs/essentials) for technical
  requirements, spam-policy boundaries, crawlable links, and people-first best practices;
- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
  for original value, expertise, page experience, and the “Who, How, and Why” review;
- [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
  for crawlability, canonicalisation, links, media, promotion, and realistic time-to-measure
  expectations;
- [Search Analytics: query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
  for bounded first-party query/page evidence and its top-row/internal-limit caveat;
- [Google crawling and indexing](https://developers.google.com/search/docs/crawling-indexing)
  and [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
  for discovery, sitemap, canonical, and indexing boundaries;
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/) for authenticated,
  capability-discovered content inventory and the distinction between public and private data;
- [Google Trends API alpha](https://developers.google.com/search/apis/trends) as an explicitly
  restricted source, never a required dependency;
- [Ahrefs Content Gap](https://help.ahrefs.com/en/articles/9025740-how-to-use-content-gap-to-find-keyword-ideas-from-competitor-websites)
  and [Semrush competitor discovery](https://www.semrush.com/kb/844-discover-competitors/) as
  secondary examples of domain comparison. Their proprietary metrics remain optional, labelled
  estimates, and are not required for this plugin's core workflow.
