# Measure the cycle and decide

Read before instrumentation planning, channel comparisons or performance reviews.
Use the product's existing event/analytics owner; this reference defines the
questions and interpretation, not another tracking implementation or data store.

## Define the measurement contract before execution

Choose a business outcome suited to the product: a qualified activated user,
retained account, purchase or net revenue. Define activation as delivery of the
core value, not automatically a signup. A prelaunch cycle can measure qualified
interest, but cannot claim activation or revenue without those observations.

Record source, event semantics, counting unit (user/account/session/order),
deduplication rule, entry cohort, date range/timezone, attribution model/window,
conversion lag, exclusions and owner. State the success criterion and maximum
hours/cash before the experiment. Set thresholds from baseline, economics,
available sample and decision cost rather than a universal percentage.

Trace organic landing → relevant CTA → signup/purchase → core-value action →
retained use where applicable. Record landing URL/content ID and acquisition source
using the existing privacy/consent approach. Avoid UTMs on internal links; they can
overwrite acquisition attribution. Campaign tags belong on appropriate external
distribution links. Verify a permitted test journey and event receipt, including
cross-domain flows if present, before calling the funnel measurable. Instrumentation
changes need their own task authority. Without it, deliver the plan and data request.

## Keep discovery and business evidence separate

| Layer | Evidence and interpretation |
| --- | --- |
| Availability | Published URL, crawl eligibility and actual indexing observations; distinct states |
| Discovery | Search impressions, clicks, CTR and query/page context; visibility and visits |
| Value | Qualified activations, paid customers, net revenue and retained use from defined cohorts |
| Guardrails | Refunds, churn, product quality, support load, abuse and time/cash costs |

Use rates only with explicit aligned denominators. For example:

- Search CTR = Search Console clicks / impressions in the same report scope.
- Landing activation = distinct activated users from an eligible landing cohort /
  distinct eligible users in that cohort, allowing the stated conversion window.
- Paid conversion = distinct paid users / eligible users from the same cohort and window.
- Retention = eligible activated users returning for the defined core-value event /
  activated users whose full retention window has elapsed.
- Acquisition cost = declared acquisition costs / attributed new customers;
  include content/engineering labor and maintenance when claiming fully loaded cost.
  With zero customers, cost per customer is undefined, not zero.

Do not divide independently aggregated Search Console clicks by analytics users
to manufacture a funnel rate. Search Console describes search exposure/clicks;
product analytics or transaction records establish business events. Query-level
conversions usually cannot be assigned from aggregate query and page tables.
Keep landing-page cohorts separate from query hypotheses unless a valid join
exists. Preserve consent gaps, unknown attribution, incomplete exports and missing
events as unknown or lower-bound data, rather than zeros.

Google reports AI-feature traffic within overall Web search performance under
its current documentation. Do not label aggregate Search Console changes as
AI Overview conversions. Visible citations are observations, not proof of clicks
or revenue; verify reporting capabilities if they change.

## Review on the right clock

Weekly or fortnightly is a decision cadence, not a promise of SEO impact. Align
equal-duration windows, weekday mix, locale, device and branded/non-branded scope.
Keep release dates, page age, indexing date if known and material product/pricing
changes visible. Seasonal comparisons need corresponding periods where possible.
Separate preliminary data and allow conversion/retention windows to mature.

Compare SEO with paid/social using comparable customer cohorts, attribution,
outcomes, maturity and fully loaded costs. Do not stop a paid channel merely
because organic impressions increased. Observational before/after changes support
associations; causal claims require an appropriate experiment or design accounting
for other changes. Show sample counts and uncertainty; sparse results do not
justify precise uplift forecasts or automatic scaling.

## Choose the next action

| Observation | Next diagnostic or decision |
| --- | --- |
| Not indexed or eligibility unclear | Inspect technical availability/index state before judging demand |
| Indexed, little exposure | Check query fit, competition, seasonality and page age; maintain if immature |
| Exposure, few clicks | Inspect actual result appearance and intent; test title/answer fit |
| Visits, little core value | Check tracking, audience, CTA and onboarding; prioritize the bottleneck |
| Activation, weak paid/retained outcomes | Investigate pricing/value and retention before scaling acquisition |
| Mature meaningful outcomes within caps | Expand the supported topic/asset pattern; state attribution limits |
| Missing events or immature/small cohort | Insufficient evidence; repair measurement or wait to the dated review |
| Guardrail breached or cost cap reached | Pause the affected authorized experiment; record recovery/owner |

At review, update the same cycle record with observed counts, calculated rates,
inferences, unknowns, action, owner and next review. Keep asset IDs, URLs and prior
decisions so “resume” continues the existing work. Publishing finishes an asset;
learning needs observations or a stated evidence gap. Neither proves growth alone.
