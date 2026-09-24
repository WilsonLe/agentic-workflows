# Restaurant Marketing

A Codex plugin that helps a restaurant owner manage marketing as an operational campaign, not just
generate posts.

It supports new dishes, offers, seasonal dishes, events, slow periods, always-on local discovery,
reputation and guest recovery, retention and win-back, and major launches. Every workflow:

1. records only verified restaurant facts and explicit unknowns;
2. checks price, dates, terms, inventory, capacity, staff, destination, consent, allergen, and claim
   readiness;
3. protects contribution margin with transparent offer scenarios;
4. gives each channel a role, owner, approval, measurement, and expiry action;
5. separates drafting from publishing, sending, activation, spend, influencer, and review actions;
6. measures orders, covers, bookings, redemptions, contribution, and guardrails without treating
   reach as revenue;
7. closes with verified expiry and a postmortem that separates observation from inference.

The plugin does not bundle a scheduler, advertising account, CRM, POS, email platform, review
platform, customer list, or credentials. It never authorizes a live campaign by itself.

## Requirements

- Python 3.10 or newer
- No third-party Python packages

Start with:

```text
Help me market a new dish and check readiness before writing content.
```

See `skills/restaurant-marketing-management/SKILL.md` for the workflow. The helper validates
campaign records, calculates offer economics, creates UTM URLs, and produces concise status
summaries.
