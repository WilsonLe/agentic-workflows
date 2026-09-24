---
name: erpnext-content-analytics
description: Expertly inspect, plan, and safely operate ERPNext website, portal, web shop, marketing content, newsletters, knowledge base, translations, reports, dashboards, data imports, exports, prepared reports, and analytics. Use for Website Manager, Knowledge Base Contributor, Knowledge Base Editor, Translator, Dashboard Manager, Report Manager, Prepared Report User, Analytics, and related work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Required: ERPNext account** — Configure an authorized ERPNext API credential for the target site.

<!-- catalog-prerequisites:end -->

# ERPNext Content, Website, Knowledge and Analytics

First apply `erpnext-operations`.

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
