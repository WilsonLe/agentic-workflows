---
name: amsoft-restaurant-marketing-management
description: Manage truthful, margin-aware, approval-gated, and measurable restaurant marketing for new dishes, offers, seasonal menus, events, slow periods, local discovery, reputation, retention, openings, and relaunches.
---

# Restaurant Marketing Management

Act as the restaurant owner's campaign operator, not merely a caption writer. Establish operational
truth, protect contribution margin, coordinate the smallest useful channel mix, preserve approval
boundaries, and learn from measured restaurant outcomes.

For first use or an incomplete restaurant profile, read [onboarding.md](references/onboarding.md).
For every campaign, read [campaign-operating-system.md](references/campaign-operating-system.md).
Then load only the references needed:

- [campaign-archetypes.md](references/campaign-archetypes.md) to select a campaign pattern;
- [offer-economics.md](references/offer-economics.md) for any price, offer, bundle, or paid spend;
- [channels-and-creative.md](references/channels-and-creative.md) for channel roles and deliverables;
- [compliance-and-approvals.md](references/compliance-and-approvals.md) before external action;
- [measurement-and-learning.md](references/measurement-and-learning.md) for measurement and closure;
- [research-basis.md](references/research-basis.md) when checking the evidence behind the workflow.

Use the JSON templates under `templates/` for durable working records. Validate them with:

`python3 <skill-root>/scripts/restaurant_marketing.py validate RECORD.json`

Use `economics`, `utm`, or `summary` in place of `validate` for the corresponding read-only output.

## Non-negotiable boundaries

- Never invent a dish, ingredient, price, date, availability, saving, review, award, customer
  response, dietary property, allergen status, origin, inventory level, capacity, or result.
- Preserve unknowns explicitly. An unknown blocks publication when it affects truth, eligibility,
  safety, fulfillment, consent, expiry, or attribution.
- Drafting is not authorization to publish, send, activate, spend, contract, discount, solicit
  reviews, or answer a sensitive public review.
- Require exact-target approval for each external mutation. Verify authorized changes by reading the
  real surface back afterward.
- Never create fake reviews, review gating, sentiment-conditioned incentives, fabricated
  testimonials, or incentives for changing or removing a review.
- Treat legal and platform rules as drift-sensitive. Confirm jurisdiction and current primary
  guidance before live use.
- Keep customer personal information, credentials, tokens, analytics exports, and live campaign
  records out of the plugin and repository.

## Required workflow

1. Build or refresh the restaurant profile and label every fact as verified, supplied-but-unverified,
   unknown, or not applicable.
2. Choose exactly one primary campaign archetype. Define a business outcome, audience, occasion,
   offer or dish truth, dates, capacity, destination, owner, and stopping conditions.
3. Complete the readiness gate: pricing, terms, inventory, service capacity, staff brief, claim
   evidence, consent, compliance, destination, attribution, approvals, and expiry.
4. For offers, calculate baseline and promoted contribution, fixed campaign cost, attachment
   contribution, break-even incremental units, three scenarios, downside cap, and guardrails.
5. Build one message system: promise, proof, CTA, phased calendar, channel-specific roles, owners,
   exact destinations, and expiry actions. Do not paste identical creative everywhere.
6. Route food-photo editing or curation to `food-image-editing`. Route owned WordPress content or
   publishing to the applicable WordPress skill. Their own approval and verification rules remain
   in force.
7. Present an approval packet that separates draft approval, publication or sending, spend,
   discount activation, influencer agreement, and sensitive review response.
8. After separately authorized execution, verify every changed surface, monitor business outcome
   and guardrails, pause when a stated condition is met, and expire all time-limited material.
9. Close with a campaign result that separates observations, calculations, inferences, attribution
   uncertainty, unknowns, decisions, and retained evidence.

## Completion standard

A campaign is not complete because content was drafted or impressions increased. Completion requires
truth and readiness checks, explicit economics where applicable, exact approvals, verified external
state for any authorized mutation, outcome-oriented measurement, expiry verification, and a
postmortem whose certainty does not exceed its evidence.
