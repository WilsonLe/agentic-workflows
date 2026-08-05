# Browser and API research runbook

Use this runbook to create a reproducible SEO research packet from free or already-authorized
sources. Prefer the smallest surface that provides the needed evidence.

## Choose API, connector, or Chrome

1. Check for an authorized purpose-built connector or official API that can return the required
   fields read-only.
2. Prefer the API for repeated, paginated, date-bounded extraction when authentication and quotas
   are already configured.
3. Prefer Chrome for existing signed-in dashboards, one-off filters, visual tools, exports, and
   services whose official API is unavailable or restricted.
4. Use public HTTP only for genuinely public endpoints such as sitemaps, feeds, PageSpeed Insights,
   CrUX with an approved key, or Common Crawl. Do not reverse-engineer private dashboard calls.
5. Fall back to a smaller browser sample when programmatic access would require new credentials,
   billing setup, an unofficial API, or terms-violating scraping.

Never ask for secrets in chat. Do not extract credentials from Chrome, inspect cookies or browser
storage, or copy tokens from developer tools. Use the browser session as a session, not as a secret
source.

## Chrome collection procedure

1. Use the existing signed-in Chrome profile only for the property and service the user authorized.
   Prefer an existing in-scope tab; if a new tab is required, mark it task-owned immediately.
2. Confirm the exact account, site/property, country, language, device, search type, and date range
   visible in the dashboard before reading data.
3. Keep the pass read-only. Installing an extension, adding analytics/Clarity code, linking accounts,
   changing consent, or verifying a new property is a separate consequential action requiring user
   approval.
4. Apply one documented question per view, such as “Which non-branded query families lost clicks
   year over year?” Avoid exploratory collection of unrelated customer or account data.
5. Record filters, comparison periods, time zone, row limit, omitted-query warnings, and whether the
   values are totals, sampled, truncated, normalized, estimated, or rounded.
6. Export CSV only when the task needs reusable rows and the user authorized the download. Store it
   in the selected project, name it with source and collection date, and never include credentials,
   recordings, user identifiers, or rare sensitive queries.
7. For manual search results, use a bounded query set and record locale, language, device, date,
   visible result types, representative URLs, and personalization uncertainty. Do not automate
   repeated searches or defeat bot checks.

After collection or verification, close every task-owned tab with the documented browser tab-close
method. Run this cleanup on normal completion and on blocked, failed, cancelled, or other early
exits. Never close pre-existing user tabs, unrelated tabs, or the browser; keep a task-created tab
open only when the user explicitly asks for it. Report `tab_cleanup_failed` when cleanup does not
succeed.

## Official API procedure

1. Verify the current official documentation, authentication method, read scope, quota, row limits,
   pagination, data freshness, and terms.
2. Use the least-privileged read-only identity. Keep API keys, OAuth tokens, service-account files,
   Bing keys, and WordPress application passwords outside prompts, repository files, URLs shown in
   logs, and research artifacts.
3. Bound the property, dates, dimensions, filters, page size, and total pages before the request.
   Cache or persist the approved response subset so repeated analysis does not waste quota.
4. Preserve raw field meanings. Search Console average position is not a rank tracker; Trends is
   relative interest; Keyword Planner values are rounded advertising estimates; CrUX is eligible
   Chrome field data; analytics outcomes depend on instrumentation.
5. Retry only safe reads, honor `429` and provider backoff guidance, and stop at quota or permission
   errors. Never broaden scope or switch identities to bypass a limit.
6. Save a provenance note containing endpoint family, property, collection time, filters,
   dimensions, row count, truncation, and a hash or stable path for any retained export. Do not save
   the credential or full raw response when the analysis needs only aggregates.

## Build a first-party opportunity pack

1. Export the WordPress canonical content inventory: URL, ID, type, status, title, dates, taxonomy,
   author, and internal links.
2. From Search Console, collect comparable query and page evidence by market/device/search type.
   Preserve anonymized-query and truncation limitations.
3. From analytics, collect organic landing engagement and agreed key events. Add internal-site-search
   terms only when configured and privacy-safe.
4. From Clarity, if already approved and installed, summarize aggregate behavior patterns; do not
   export session recordings or personal data.
5. Join by canonical URL. Flag query-to-page mismatches, decaying pages, weak journeys, missing
   internal links, and content with visibility but insufficient helpfulness.

## Build a competitor and demand pack

1. Confirm each competitor serves the same audience, market, and search task.
2. Inventory a bounded set of public competitor URLs from sitemaps, feeds, navigation, and canonical
   pages. Common Crawl may supply historical URL evidence when current inventories are incomplete.
3. Sample representative search results in Chrome to classify intent and result formats. Record the
   observation context; do not scrape.
4. Corroborate candidate tasks with Bing Keyword Research, Google Trends, customer questions, or
   another relevant first-party signal. Use Keyword Planner only when an already-configured Ads
   account makes its access appropriate.
5. Compare reader tasks, not heading strings or word counts. Record competitor coverage without
   copying prose or structure.
6. Apply the originality and expertise gate. Reject any topic the site cannot improve with real
   knowledge, evidence, examples, tools, or experience.

## Evidence matrix

Use one row per material signal:

| Field | Meaning |
| --- | --- |
| Source | Product, API family, public URL, export, or WordPress object |
| Access | API, connector, Chrome UI, public HTTP, or uploaded export |
| Access label | Free public, verified ownership, account, limited tier, restricted, or open data |
| Evidence type | First-party, public observation, open data, or estimate |
| Scope | Property/domain, market, language, device, search type, and dates |
| Signal | The exact observed or calculated result |
| Limits | Sampling, truncation, privacy omission, lag, normalization, rounding, or uncertainty |
| Decision | Keep, investigate, refresh, consolidate, create, decline, or measure |

Never merge sources by silently treating their metrics as equivalent. The output is an evidence
chain for a decision, not a synthetic universal “SEO score.”
