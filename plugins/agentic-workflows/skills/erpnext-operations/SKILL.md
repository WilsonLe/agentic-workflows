---
name: erpnext-operations
description: Onboard, inspect, and safely route work for an authorized ERPNext API user across organization administration, accounts, analytics, selling, buying, stock, manufacturing, quality, maintenance, fleet, HR, projects, support, delivery, website, marketing, knowledge, reporting, and system management. Use for ERPNext setup, first use, cross-module requests, role or permission discovery, and tasks that need the correct domain skill.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Required: ERPNext account** — Configure an authorized ERPNext API credential for the target site.

<!-- catalog-prerequisites:end -->

# ERPNext Operations

Act as the front door and operating standard for the ERPNext Operations plugin. Be an ERPNext
expert, but treat the installed site, its DocType metadata, its workflows, and the authenticated
user's actual permissions as authoritative. Never infer write access from a role label or from this
skill.

## Onboarding

For setup, first use, authentication, missing credentials, or credential rotation, read
[references/onboarding.md](references/onboarding.md) and follow it exactly. Ask the user for the
filesystem path to their JSON or Frappe CSV key file; never ask them to paste the API key or secret into chat.

Use the shared scripts at the central plugin root:

- `<plugin-root>/scripts/erpnext_configure_credentials.py` installs the selected file into the persistent
  protected path.
- `<plugin-root>/scripts/erpnext_api.py whoami` verifies authentication without changing ERPNext.

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

1. Confirm credentials exist and verify the authenticated identity with `whoami`.
2. Discover site context and permissions with read-only calls. Read representative current records,
   settings, naming series, required fields, workflow state, company, currency, fiscal year and
   dimensions. Do not guess identifiers or schema.
3. Classify the request as explanation, inspection, draft preparation, transaction write,
   submission/cancellation, configuration, access control, bulk change, or deletion.
4. For a write, show the exact target, intended fields, business effect, dependencies, validation,
   and rollback or reversal method. Ask for explicit approval immediately before execution.
5. Put request JSON in a temporary file that contains no credentials. Use the client only after
   approval; its `--confirm-write I_APPROVE_ERPNEXT_WRITE` switch is a defense-in-depth gate, not a
   substitute for user confirmation.
6. Read the changed records and affected downstream state back from ERPNext. For accounting or
   stock effects, verify the relevant ledger/report. For emails or integrations, verify delivery
   state without exposing message secrets.
7. Report created document names, workflow/docstatus, observed effects, failures, and any manual
   follow-up. Remove temporary payload files when finished.

## Safety rules

- Never print, echo, log, return, commit, upload, or place the API key or secret in commands,
  payloads, screenshots, documentation, or source control.
- Never use shell tracing, environment dumps, browser password automation, or session cookies.
- Inspection, diagnosis, explanation, and planning do not authorize a write.
- Require explicit approval for every mutation. Require an especially clear impact preview for
  submissions, cancellations, amendments, deletions, payments, journal entries, stock ledger
  changes, payroll, user/role/permission changes, global settings, workflow changes, imports,
  integrations, email, bulk actions, and production/manufacturing actions.
- Prefer cancel/amend, reversal, return, or correcting documents over destructive deletion when
  ERPNext's audit trail supports them.
- Do not bypass ERPNext validation, permissions, approval workflows, fiscal locks, immutable
  ledgers, or separation-of-duties controls even when the API user is powerful.
- Treat Customer, Employee, and Supplier portal roles separately from desk roles; do not add them
  merely to make a role list look complete.
- Current official documentation and the live site's version/schema outrank remembered behavior.

Read [references/official-api-and-safety.md](references/official-api-and-safety.md) when forming API
requests or explaining permissions.
