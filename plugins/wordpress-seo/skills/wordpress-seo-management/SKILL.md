---
name: wordpress-seo-management
description: Run evidence-led SEO and growth audits for an authorized WordPress website. Use for technical and on-page audits, indexability and sitemap reviews, free SEO API and Chrome-based research, Search Console or analytics interpretation, audience and search-intent discovery, competitor qualification and per-competitor content-gap research, growth roadmaps, content inventories, editorial roadmaps, article briefs, post suggestions, content refreshes, internal linking, metadata and structured-data recommendations, draft creation, controlled publication, and SEO outcome measurement when Codex has an existing administrator session or other authorized site access.
---

# WordPress SEO Management

Improve search visibility through evidence-led research and controlled WordPress changes. Treat SEO
as a user-value and discoverability practice, not a promise of rankings. Prefer original,
people-first content with demonstrable experience over keyword-driven volume.

When the user asks for an SEO and growth audit, follow
[growth-audit-framework.md](references/growth-audit-framework.md) and return
[growth-audit-report-template.md](references/growth-audit-report-template.md). The growth lens
connects search discovery to an agreed business outcome while keeping observed evidence, tool
estimates, and hypotheses separate. It identifies and qualifies competitors before comparing each
competitor's coverage, then turns only supported reader-task gaps into original opportunities.
When the requested deliverable is a proposal or decision package, also follow
[proposal-deck-delivery.md](references/proposal-deck-delivery.md) and produce one editable,
audience-facing `.pptx` from AMSoft to the named project, business, or company. Use the
illustrative deck in `examples/amsoft-seo-growth-proposal.pptx` only as a structural and tonal
starting point; replace its illustrative framing with verified project evidence before delivery.

SEO is a specialized content add-on, not a third infrastructure boundary.
When a request changes pages, posts, media, videos, or user-facing design,
compose `wordpress-content-management`. When it requires SSH, WP-CLI,
hosting, plugin/theme code, filesystem, or deployment work, compose
`wordpress-devops-management`. Keep SEO research, Content changes, and DevOps
changes as separate records and approvals.

For first use on a site, read [onboarding-and-access.md](references/onboarding-and-access.md).
Never ask the user to paste a password, application password, cookie, nonce, API key, or recovery
code into chat. Use an existing signed-in administrator session or credentials supplied through an
approved secret mechanism.

## Select the operating surface

- Prefer an official connector or read-only API when it exposes the required data reliably. Use an
  existing signed-in Chrome session for authorized dashboards, interactive tools, exports, and
  observations that lack an appropriate API. Never inspect Chrome history, cookies, passwords,
  local storage, or unrelated tabs.
- Use the public site and web research for rendered pages, search results, competitors, citations,
  and search-intent evidence.
- Use the authenticated WordPress administrator UI or discovered REST capabilities for content and
  configuration inventory. Never assume an SEO plugin or its metadata is REST-writable.
- Use first-party Search Console, analytics, or business-profile data only when the user has granted
  access. Label conclusions based on third-party estimates or search-result samples as estimates.
- Route page/post/media/design changes to `wordpress-content-management`; route server, database,
  filesystem, cache, redirect implementation, or WP-CLI work to `wordpress-devops-management`.
  Do not use the built-in theme or plugin file editors.

For source selection, access requirements, and honest uses of free data, read
[free-seo-data-sources.md](references/free-seo-data-sources.md). For repeatable collection through
Chrome or official APIs, read
[browser-and-api-research-runbook.md](references/browser-and-api-research-runbook.md).

When Chrome is used, prefer an existing in-scope tab and establish tab ownership before opening a
new one. Mark every task-created tab immediately, then close task-created tabs with the documented
browser tab-close method after collection or verification and on blocked, failed, cancelled, or
otherwise early exits. Never close pre-existing user tabs, unrelated tabs, or the browser. Report
`tab_cleanup_failed` if a task-created tab cannot be closed; do not claim clean completion until that
limitation is visible.

## Run the SEO cycle

1. Establish the exact site, environment, market, language, audience, business goals, conversions,
   known competitors, and time horizon. For a growth audit, create the audit charter and readiness
   matrix in [growth-audit-framework.md](references/growth-audit-framework.md). Separate supplied
   facts, observations, estimates, and hypotheses.
2. Inventory the real site before proposing work: content types, URLs, status, templates,
   taxonomies, authors, dates, internal links, media, SEO plugin, index controls, canonicals,
   sitemaps, structured data, and rendered mobile/desktop experience.
3. Build a baseline from available first-party search and behavior data. Preserve query and user
   privacy; report data coverage, filters, time zone, and date ranges. Do not treat traffic,
   impressions, average position, search-volume estimates, or rank-tracker estimates as revenue.
4. Audit technical, on-page, content, authority/trust, local, image, and page-experience signals.
   Read [audit-and-prioritization.md](references/audit-and-prioritization.md).
5. Discover audience questions, query families, existing strengths, cannibalization, decay, and
   competitor coverage. Identify and qualify commercial, search, and audience-alternative
   competitors before comparing each included competitor. Read
   [content-discovery-and-gap-analysis.md](references/content-discovery-and-gap-analysis.md) and
   [growth-audit-framework.md](references/growth-audit-framework.md).
6. Prioritize opportunities by user value, business fit, evidence strength, likely impact, effort,
   confidence, dependencies, and risk. Prefer improving a strong existing URL when it already owns
   the intent; propose a new post only when it serves a distinct useful need.
7. Produce a change brief before editing. Preserve the URL unless a migration is explicitly in
   scope. Ground claims, author expertise, examples, media, and calls to action in verified facts.
8. Make only the authorized change and verify it. Follow
   [wordpress-editing-and-verification.md](references/wordpress-editing-and-verification.md).
9. Measure after a suitable observation window using the agreed baseline, annotated deployment
   date, leading search indicators, and business outcomes. Report uncertainty and external changes.
10. When a proposal or visual handoff is requested, create the editable AMSoft proposal deck
    after the evidence packet and roadmap are stable. Follow
    [proposal-deck-delivery.md](references/proposal-deck-delivery.md), keep the deck audience-facing,
    and render/inspect every slide before returning the `.pptx`.

## Required deliverables

Adapt the format to the request, but keep these fields explicit:

- **Audit finding:** observed evidence, affected URL or template, consequence, confidence, and
  recommended action.
- **Opportunity:** audience need, query or topic cluster, current-site coverage, competitor evidence,
  originality angle, suggested target URL, user/business value, effort, risk, and priority.
- **Research packet:** exact source, access mode, property or market scope, collection date, filters,
  evidence type (`first-party`, `public observation`, `open data`, or `estimate`), coverage limits,
  and the decision each item supports.
- **Content brief:** primary reader task, intent, verified facts and sources, first-hand contribution,
  outline, internal-link plan, media needs, title and snippet options, schema eligibility, conversion
  path, reviewer, and acceptance checks.
- **Change record:** before state, exact edited object and fields, draft/published state, preview or
  public URL, verification, rollback route, and measurement annotation.
- **Growth audit:** business outcome and leading indicators, readiness matrix, validated competitor
  ledger, per-competitor research summaries, reader-task/content-gap matrix, declined opportunities,
  originality angle, prioritised roadmap, growth hypotheses, and observation window.
- **Proposal deck:** one editable `.pptx` from AMSoft to the named recipient, with the decision,
  evidence limits, baseline, competitor qualification, supported content gaps, prioritized roadmap,
  sources in speaker notes, approval boundary, and next step. The deck is a proposal artifact, not
  proof that an audit finding or WordPress change has been executed.

## Content and research rules

- Do not copy competitor prose, structure, images, data, or distinctive creative expression.
  Competitors reveal audience needs and coverage patterns, not a template to reproduce.
- Do not recommend keyword stuffing, hidden text, doorway pages, fake reviews, link schemes, scaled
  low-value pages, fabricated expertise, arbitrary word counts, or mechanical keyword density.
- Do not invent search volume, rankings, backlinks, conversions, author credentials, product facts,
  locations, opening hours, prices, testimonials, or legal/medical/financial claims.
- Do not call every account-gated or limited tool “free.” Label sources as `free public`, `free with
  verified ownership`, `free with account`, `limited free tier`, `alpha/restricted`, or `open data`,
  and recheck current terms and limits.
- Do not scrape search-result pages, autocomplete endpoints, dashboards, or competitor sites at
  scale through Chrome. Use bounded human-visible observations or an authorized official API.
- Distinguish factual gaps from content gaps. A topic is not an opportunity unless the site can add
  useful, original, trustworthy value for its intended audience.
- A competitor topic or keyword gap is a lead, not a conclusion. Require an audience need, a
  current-site weakness, a credible original contribution, and evidence with stated limits before
  recommending new content.
- “Do the same thing better” means better task completion, accuracy, experience, evidence, trust,
  format, or conversion path. Never copy competitor prose, headings, order, images, data, or
  distinctive creative expression.
- A proposal deck must distinguish `verified fact`, `observed signal`, `estimate`, `proposal`, and
  `hypothesis` in the visible narrative or supporting notes. Do not make a polished `.pptx` look
  like completed research when the audit charter or evidence is still missing.
- Cite fresh sources for claims that can change. Read
  [standards-and-sources.md](references/standards-and-sources.md) when applying current search-engine
  requirements or structured-data rules.
- Treat accessibility, performance, and clear information architecture as user outcomes as well as
  search considerations. Do not reduce them to a single score.

## Approval boundaries

An audit, discovery, comparison, recommendation, or planning request is read-only. A request to
write or refresh content authorizes a proposed draft, not publication. Keep new and substantially
rewritten posts as WordPress drafts unless the user explicitly requests publication.

Require confirmation immediately before publishing or scheduling; changing a published slug,
permalink, canonical, redirect, robots directive, site visibility, sitemap behavior, structured data
template, taxonomy structure, navigation, SEO-plugin configuration, or shared template; bulk edits;
plugin/theme installation or activation; content deletion; or any site-wide production change.

Refetch immediately before writing and stop on unexpected concurrent edits. Capture the exact
before state needed for rollback. Never infer permission to alter a competitor, another property,
or a site not named by the user.

## Completion standard

API success or a saved wp-admin screen is not completion. Re-read the object, inspect the rendered
preview or public URL logged out, verify affected links and metadata, check relevant desktop and
mobile behavior, and report what remains a draft, cached, unmeasured, or awaiting recrawl. Never
claim ranking improvement before comparable post-change data exists.
