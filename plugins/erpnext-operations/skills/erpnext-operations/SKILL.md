---
name: erpnext-operations
description: Use this skill whenever the user asks about ERPNext setup or first use, roles or permissions, an ERPNext task or explanation that spans modules (such as procure-to-pay or order-to-cash), or an ERPNext request whose domain skill is unclear. Onboards, inspects, and safely routes work for an authorized ERPNext API user across organization administration, accounts, analytics, selling, buying, stock, manufacturing, quality, maintenance, fleet, HR, projects, support, delivery, website, marketing, knowledge, reporting, and system management.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the host's browser controls (the built-in Codex browser in Codex, Claude in Chrome in Claude Code) for supported login or secure key/token acquisition, or let the user complete that step, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# ERPNext Operations

Read [authenticated CLI and browser assistance](references/browser-selection.md)
before operating this service. Default to a supported authenticated CLI or bundled
command-line client. Resolve the current project's intended account and exact
target, check existing authentication read-only, and reuse it only when they match.
If authentication is missing or mismatched, use the host's browser controls (the
built-in Codex browser in Codex, Claude in Chrome in Claude Code) for supported
login or secure key/token acquisition. Without a browser tool in this session,
give the user the exact login step instead of offering to perform it. Then
return to the CLI and verify.
Use browser service operations only after the authenticated CLI is proven unable
to perform the requested action. Missing authentication is not that capability gap.


Act as the front door and operating standard for the ERPNext Operations plugin. Be an ERPNext
expert, but treat the installed site, its DocType metadata, its workflows, and the authenticated
user's actual permissions as authoritative. Never infer write access from a role label or from this
skill.

## Onboarding

Read [onboarding](references/onboarding.md). Use the protected command-line client
`<plugin-root>/scripts/erpnext_api.py`; verify `whoami` and the exact
site/user/company/project before operations. If credentials are absent, acquire the
API key/secret through the official ERPNext User controls in the host's browser, or
let the user do it, using concealed protected transfer, then verify the client. Never ask for key values in chat or assume the
browser session authenticates the command-line client.

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
   and rollback or reversal method. Reuse existing exact-effect task authority; ask only when it does not cover the change.
5. Put request JSON in a temporary file that contains no credentials. Use the authenticated client only within
   exact-effect authority; its `--confirm-write I_APPROVE_ERPNEXT_WRITE` switch is a defense-in-depth gate, not a
   substitute for user confirmation.
6. Read the changed records and affected downstream state back from ERPNext. For accounting or
   stock effects, verify the relevant ledger/report. For emails or integrations, verify delivery
   state without exposing message secrets.
7. Report created document names, workflow/docstatus, observed effects, failures, and any manual
   follow-up. Remove temporary payload files when finished. If the authenticated client lacks
   the requested capability, record the exact gap and use supported browser UI
   on the same verified site/user/company/record, then read back saved state.

## Safety rules

- Never print, echo, log, return, commit, upload, or place the API key or secret in commands,
  payloads, screenshots, documentation, or source control.
- Never use shell tracing, environment dumps, browser password automation, or session cookies.
- Inspection, diagnosis, explanation, and planning do not authorize a write.
- Require exact-effect task authority for every mutation. Require an especially clear impact preview for
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
