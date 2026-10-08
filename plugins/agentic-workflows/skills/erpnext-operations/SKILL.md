---
name: erpnext-operations
description: Onboard, inspect, and safely route work for an authorized ERPNext browser user across organization administration, accounts, analytics, selling, buying, stock, manufacturing, quality, maintenance, fleet, HR, projects, support, delivery, website, marketing, knowledge, reporting, and system management. Use for browser-based ERPNext setup, first use, cross-module requests, role or permission discovery, and tasks that need the correct domain skill.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.


Act as the front door and operating standard for the ERPNext Operations plugin. Be an ERPNext
expert, but treat the installed site, its DocType metadata, its workflows, and the authenticated
user's actual permissions as authoritative. Never infer write access from a role label or from this
skill.

## Onboarding

Read [onboarding](references/onboarding.md). Open the exact ERPNext site in the
browser, verify the signed-in user and site, then select the company/project
context required for this task. Do not require a key file for browser access.

## Route by domain

- Users, roles, permissions, companies, departments, branches, defaults, email, workspace and
  system settings: `erpnext-organization-administration`.
- General ledger, receivables, payables, banking, taxes, assets, budgets, payments, invoices,
  closing, audit and financial reports: `erpnext-accounting-finance`.
- Leads, opportunities, customers, quotations, orders, delivery, invoicing, pricing, POS,
  campaigns, loyalty and sales analytics: `erpnext-sales-crm`.
- Suppliers, requests, quotations, purchase orders, receipts, warehouses, items, batches, serial
  numbers, replenishment, transfers and stock reconciliation: `erpnext-buying-stock`.
- BOMs, work orders, production, capacity, subcontracting, quality, maintenance and fleet:
  `erpnext-manufacturing-assets`.
- Employees, recruitment, attendance, leave, expense claims, projects, timesheets, support,
  service levels and issue resolution: `erpnext-people-projects-support`.
- Website, portal, web shop, content, newsletter, knowledge base, translation, dashboards,
  reports, imports and exports: `erpnext-content-analytics`.
- Mixed requests: load each relevant skill and preserve each skill's business controls.

## Universal operating sequence

1. Verify the browser identity, site origin, company, project, and actual permissions.
2. Inspect current records, form fields, workflows, naming series, required links,
   currency, fiscal year, and dimensions in the visible UI. Do not guess schema.
3. Classify the request as inspection, draft, transaction write, submission/cancellation,
   configuration, access control, bulk change, or deletion.
4. Preview the exact target, fields, business effect, dependencies, validation, and
   reversal. Reuse the user's explicit task authority; ask only for a material
   effect or target it does not cover. Keep enforced workflow approvals intact.
5. Create, update, submit, cancel, configure, or delete through ERPNext forms and
   supported controls. Optional read-only helper diagnostics must independently
   match the browser user/site/company; do not use API writes by default.
6. Reopen the changed record and affected downstream state. For accounting or stock,
   verify the relevant ledger/report; for integrations, verify delivery state.
7. Report document names, workflow/docstatus, observed effects, failures, and recovery.

## Safety rules

- Never print, echo, log, return, commit, upload, or place the API key or secret in commands,
  payloads, screenshots, documentation, or source control.
- Never use shell tracing, environment dumps, browser password automation, or session cookies.
- Inspection, diagnosis, explanation, and planning do not authorize a write.
- Require task authority for every mutation. Require an especially clear impact preview for
  submissions, cancellations, amendments, deletions, payments, journal entries, stock ledger
  changes, payroll, user/role/permission changes, global settings, workflow changes, imports,
  integrations, email, bulk actions, and production/manufacturing actions.
- Prefer cancel/amend, reversal, return, or correcting documents over destructive deletion when
  ERPNext's audit trail supports them.
- Do not bypass ERPNext validation, permissions, approval workflows, fiscal locks, immutable
  ledgers, or separation-of-duties controls even when the browser user is powerful.
- Treat Customer, Employee, and Supplier portal roles separately from desk roles; do not add them
  merely to make a role list look complete.
- Current official documentation and the live site's version/schema outrank remembered behavior.

Read [permissions and safety](references/official-api-and-safety.md) when explaining access
or using optional protected read-only diagnostics. UI capability gaps require a
concrete limitation and explicit user direction before any non-browser mutation.
