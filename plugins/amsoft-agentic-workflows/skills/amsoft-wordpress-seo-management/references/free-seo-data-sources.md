# Free SEO data sources

Recheck access, quotas, terms, and product status before each material project. “Free” does not mean
anonymous, unlimited, open source, or suitable for competitor analysis. Record one of these access
labels: `free public`, `free with verified ownership`, `free with account`, `limited free tier`,
`alpha/restricted`, or `open data`.

## First-party site and search evidence

| Source | Access mode | Access label | What it can support | Important limits |
| --- | --- | --- | --- | --- |
| WordPress admin and REST API | Chrome UI and discovered REST endpoints | Free with authorized site access | Exact content inventory, status, taxonomy, dates, internal links, media, and editable source | Plugin metadata and page-builder fields may not be REST-exposed; rendered HTML is not lossless source |
| Google Search Console | Chrome UI, exports, and official API | Free with verified ownership | Queries, pages, clicks, impressions, CTR, average position, search appearance, index inspection, sitemaps, and crawl evidence | Query rows are privacy-filtered and truncated; data is canonical-aggregated, delayed, filtered, quota-bound, and not a complete demand census |
| Google Analytics 4 standard property | Chrome UI, exports, and Data API | Free with authorized property access | Landing-page engagement, paths, internal search when configured, key events, and business outcomes | Consent, collection, attribution, bot filtering, time zone, and event configuration affect meaning; it does not report general search demand |
| Bing Webmaster Tools | Chrome UI and official API | Free with verified ownership | Bing queries, traffic, keywords, links, crawl data, site scan, and sitemaps | Bing behavior is not Google behavior; API access uses protected site credentials and quotas |
| Microsoft Clarity | Chrome dashboard and browser extension | Free with account after approved instrumentation | Scroll, click, rage-click, dead-click, recording, and journey evidence for comprehension or conversion gaps | Installing tracking changes the site and privacy posture; require approval, consent review, and data-minimization checks before setup |

Prefer these sources for decisions about an owned site because they describe the real property or
its users. Never expose rare queries, recordings, personal data, credentials, or customer-level
events in research artifacts.

## Demand and search-intent discovery

| Source | Access mode | Access label | Best use | Do not infer |
| --- | --- | --- | --- | --- |
| Google Trends Explore | Chrome UI and export | Free public | Relative interest, seasonality, regional differences, related topics, and rising queries | Absolute search volume, conversion intent, or guaranteed future demand |
| Google Trends API | Official API for accepted testers | Alpha/restricted | Consistently scaled multi-term and longitudinal analysis when access has been granted | General availability; do not use unofficial reverse-engineered endpoints as a substitute |
| Bing Keyword Research | Chrome UI in Webmaster Tools | Free with account | Related phrases, questions, recent relevance, volume trends, countries, devices, top URLs, and associated topics | Google volume or the site's ability to rank |
| Google Ads Keyword Planner | Chrome UI; official Ads APIs only when already authorized | Free with account and billing setup | Keyword ideas, location/language segmentation, rounded historical estimates, and seasonality clues | Organic ranking difficulty, exact demand, or free frictionless access; advertiser competition is not organic competition |
| Google or Bing search results | Bounded manual Chrome observation | Free public observation | Dominant intent, result formats, freshness, titles/snippets, related questions, local packs, and representative competitors | A stable rank, a complete market, or an API dataset; results vary by time, location, device, language, and personalization |
| Site search and customer questions | WordPress, analytics, support, sales, or survey sources | Free with authorized access | Unanswered audience language, confusion, objections, and task failures | Public search demand unless independently corroborated |

Autocomplete, related questions, related searches, and result snippets are volatile UI observations,
not licensed bulk keyword feeds. Capture a small research sample in Chrome; do not automate scraping
or call undocumented suggestion endpoints.

## Technical and page-experience evidence

| Source | Access mode | Access label | Best use | Limits |
| --- | --- | --- | --- | --- |
| Lighthouse in Chrome DevTools | Chrome | Free public/local | Repeatable lab diagnostics for performance, accessibility, best practices, and basic SEO | Lab conditions and the Lighthouse version affect results; a score is not a ranking prediction |
| PageSpeed Insights | Browser UI and official API | Free public; API key recommended for repeated use | Lighthouse diagnostics and URL-level performance investigation | API behavior evolves; do not assume its field-data payload remains unchanged |
| Chrome UX Report | CrUX dashboard or official API | Free public; API key and free quota for API | Real-user field distributions for eligible URLs or origins | Only sufficiently popular Chrome-observed pages are included; absence is not failure |
| Rich Results Test and Schema Markup Validator | Browser UI | Free public | Eligibility-oriented rendering and schema syntax checks | Valid markup does not guarantee a rich result or accuracy of the visible claim |
| Chrome DevTools Network, Elements, Rendering, and Performance | Chrome | Free local | Rendered metadata, response behavior, JavaScript, layout, resource, and runtime diagnosis | One browser session is not population-level field evidence |

Use these tools to diagnose discoverability and user experience. Do not turn their scores into an
SEO opportunity backlog without connecting the finding to affected templates, readers, and business
goals.

## Owned-site third-party tools

- **Ahrefs Free:** use its browser UI for verified sites, bounded Site Audit, owned-site organic
  keywords, internal links, and backlinks. Label metrics as third-party estimates. Its free verified
  access does not provide general competitor analysis, and current credit limits can change.
- **Other limited free tiers:** include only after checking the provider's current official pricing,
  ownership requirements, export rights, privacy terms, and usable limits. Never design the core
  workflow around a trial, expiring credit, or tool that requires payment details without telling
  the user.

Prefer free and open-source tools when capability is equivalent. Record `open_source: yes/no/unknown`
separately from price; a free proprietary service is not open source.

## Competitor inventories and open-web evidence

- Use public `sitemap.xml` or sitemap indexes, RSS/Atom feeds, canonical pages, navigation, and
  public author/category archives to build a bounded competitor content inventory.
- Use the Common Crawl index as free open data to discover archived URLs or historical coverage
  patterns. Respect its rate guidance. A crawl record does not prove a page is current, indexed,
  popular, accurate, or owned by the current operator.
- Use public government, standards-body, university, first-party company, and reputable research
  datasets as factual source candidates appropriate to the industry. Verify current authority,
  license, methodology, geography, date, and primary-source status before briefing content.
- Use public forums, Q&A sites, reviews, and community discussions only to identify language and
  questions. Do not collect personal data, copy contributions, or treat anecdotes as representative
  demand or factual authority.

## Selection order

1. Exact WordPress inventory and verified business/audience facts.
2. First-party Search Console, Bing, analytics, internal-search, support, or conversion evidence.
3. Free public demand and intent evidence from Trends, Bing Keyword Research, and bounded search
   observations.
4. Public competitor inventories and authoritative factual sources.
5. Third-party estimates or open-web archives as labelled corroboration.

If a source is unavailable, continue with a smaller honest evidence set. State what cannot be known
instead of manufacturing a metric or pressuring the user to create an account.
