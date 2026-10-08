---
name: erpnext-content-analytics
description: Expertly inspect, plan, and safely operate ERPNext website, portal, web shop, marketing content, newsletters, knowledge base, translations, reports, dashboards, data imports, exports, prepared reports, and analytics. Use for Website Manager, Knowledge Base Contributor, Knowledge Base Editor, Translator, Dashboard Manager, Report Manager, Prepared Report User, Analytics, and related work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext Content, Website, Knowledge and Analytics

First apply `erpnext-operations`, including its browser account/site/company selection
and browser management workflow. Optional read-only diagnostics must match that context.

## Content and presentation

Inspect Website Settings, Web Page, Blog Post, Web Form, Portal Settings, Item website fields,
Product Listing, shopping/cart settings, Website Theme, Navbar/Footer, About/Contact content,
Newsletter, Email Group, Knowledge Base, translation records and publication/workflow status.

Content publication, email distribution, portal exposure, pricing visibility, forms that collect
personal data, scripts/styles, redirects and domain/routing changes require a rendered preview,
audience/impact explanation and explicit approval. Verify the real public or authenticated page
after publication. Do not expose internal-only data through a report, web form, portal, or export.

## Reports, dashboards and data movement

For Report Builder, Query Report, Script Report, Dashboard, Dashboard Chart, Number Card, Prepared
Report, Data Import and Data Export, first identify source DocTypes, filters, permissions, row
volume, field sensitivity, company scope and intended audience.

Treat SQL/query/script changes, scheduled/prepared reports, broad exports, data imports, mass
updates and dashboard publication as high-impact. Never put secrets in a report query or exported
artifact. Preview imports with validation errors and row counts before execution; keep the source
file and a rollback/correction plan. Verify exact imported/failed counts and sample records after
execution.
