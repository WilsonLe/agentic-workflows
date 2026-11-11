# Source assessment and adaptation

Inspected on 2 November 2026. This is an Agentic Workflows adaptation of selected
methods from [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo/tree/6be93f45064ffbadced572b5d5c95f55fd263af0),
revision `6be93f45064ffbadced572b5d5c95f55fd263af0`, by agricidaniel.
The [upstream MIT copyright and license](../licenses/claude-seo-MIT.txt) are
preserved verbatim. Instructions are rewritten for this bundle's existing
responsibility, evidence, tool and authority contracts. This is not an upstream
endorsement or an installation of Claude SEO.

## Adoption map

Paths below are relative to that pinned upstream tree. Source inspection is
evidence of available methods, not proof of runtime behavior or ranking outcomes.

| Source paths | Useful method adopted | Local modification |
| --- | --- | --- |
| `skills/seo`, `skills/seo-audit` | Site-type detection, shared audit synthesis, dependencies and failure/leading-indicator checks per recommendation | One portable audit owner, bounded inspection and explicit coverage; remove mandatory agent fan-out, model selection, weighted health scores and promotional footer. |
| `skills/seo-technical`, `skills/seo-schema`, `skills/seo-hreflang` | Separate crawl/index/render checks, structured-data inventory/validation and locale relationships | Refresh current primary guidance; distinguish eligibility from observation, source/DOM/search state and vocabulary from rich-result support. No fixed URL-length or click-depth ranking rules. |
| `skills/seo-content`, `skills/seo-geo` | Audience intent, who/how/why, claim evidence and AI-search access/content/observation | Remove word-count floors, link quotas, universal quality/citability scores, unsourced market statistics and causal claims from correlations. No special AI-file requirement. |
| `skills/seo-ecommerce`, `skills/seo-programmatic`, `skills/seo-local`, `skills/seo-sitemap` | Template-aware inventory and conditional product, location, programmatic and sitemap checks | Use supported facts and actual page usefulness rather than numeric uniqueness/page-count gates; preserve existing campaign/account owners. |
| `skills/seo-drift`, `skills/seo-backlinks` | Preserve before/after observations, missing-data states and source-labelled link coverage | Reuse project records with compatible comparisons; no bundled SQLite monitoring, provider scoring, link database or automatic disavow. |

No upstream scripts, installers, hooks, agents, external API clients or runtime
dependencies are imported. Optional providers remain task-selected evidence
channels, not automatic integrations or prerequisites. The separate `seo-flow`
framework and its CC BY material are not included. Media generation, account
operations, content production and engineering implementation keep their existing
owners. The skill does not authorize fresh-agent trials or automatically delegate
audits.

## Primary guidance and freshness

Reviewed current primary pages for the core distinctions on the inspection date:

- [AI features](https://developers.google.com/search/docs/appearance/ai-features):
  ordinary SEO applies; no special AI text file or markup is required for Google's
  AI features. This is not a statement about every answer-engine vendor.
- [Noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing):
  a crawler needs access to see the rule; crawl disallow and index removal differ.
- [Structured-data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
  and [policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies):
  supported feature eligibility and actual display are separate.
- [Web Vitals](https://web.dev/articles/vitals): field data and lab tests serve
  different purposes; a load-only Lighthouse test does not measure INP.
- [Helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content),
  [localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
  and [local ranking](https://support.google.com/business/answer/7091):
  audience usefulness, alternate relationships and local observation context.
- [Indexing API](https://developers.google.com/search/apis/indexing-api/v3/using-api):
  use is restricted to eligible job-posting and livestream-event pages.

Other linked primary documentation is a task-time starting point. Reopen the
relevant platform documentation for current feature eligibility, crawler policy,
metric thresholds, API scope and jurisdiction before making a live recommendation.
If it cannot be checked, disclose the stale/unverified part and avoid asserting a
specific current feature rule. The upstream snapshot is attribution, not an
authority overriding current primary guidance or the user's instructions.
