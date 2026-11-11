# Onboarding and restaurant source of truth

Create one restaurant profile before managing campaigns. Ask only for facts not discoverable from
authorized sources and never convert silence into an assumption.

## Minimum profile

- restaurant name, location, timezone, locale, service modes, cuisines, positioning, audiences,
  languages, and a short voice description;
- owned and third-party surfaces, exact URLs, access status, and who can approve changes;
- opening hours, order modes, booking and catering paths, kitchen or service constraints, stock
  dependencies, and staff briefing process;
- available measurement sources such as POS item sales, bookings, redemptions, landing-page events,
  call tracking, or a manual tally;
- evidence sources for menu facts, prices, dietary and allergen information, provenance, awards,
  testimonials, and availability;
- direct-marketing consent, sender identity, unsubscribe and suppression processes;
- who approves facts, creative, discounts, spend, publishing, influencer activity, and review
  responses.

Classify each surface as `verified`, `unverified`, or `unavailable`. Record unresolved questions in
`unknowns`. Never place credentials, customer lists, personal identifiers, or raw exports in the
profile.

Use `<skill-root>/templates/restaurant-profile.json` as the durable record. Recheck facts whose source or
`updated_at` may have drifted before each live campaign.
