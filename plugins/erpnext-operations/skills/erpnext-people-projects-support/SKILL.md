---
name: erpnext-people-projects-support
description: Expertly inspect, plan, and safely operate ERPNext and installed Frappe HR people operations, recruitment, attendance, leave, expense claims, projects, tasks, timesheets, support issues, SLAs, warranties, and service work. Use for HR User, HR Manager, Projects User, Projects Manager, Support Team, Academics User, and related work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext People, Projects and Support

First apply `erpnext-operations`, including its browser account/site/company selection
and browser management workflow. Optional read-only diagnostics must match that context. Detect installed apps and live DocTypes before assuming Frappe HR,
payroll, education, or helpdesk features are present.

## People operations

Cover Employee/User linkage, department/designation/branch, recruitment, onboarding, shifts,
attendance, leave, holidays, expense claims, travel, appraisal, training, separation and payroll
only where installed. Treat personal, medical, banking, compensation, tax, performance,
disciplinary and identity data as sensitive. Request and return only fields necessary for the task.

Never invent attendance, hours, approvals, qualifications, appraisal evidence, expenses, salary
components, tax declarations, or employee consent. Payroll processing, salary slips, bank outputs,
leave allocation, attendance correction, expense approval and employee status changes require an
explicit preview and approval.

## Projects and support

Trace Project, Task, dependency, milestone, Timesheet, Activity Type, costing/billing, Sales Order,
Issue, Customer, Contact, SLA, Warranty Claim, Maintenance Visit and communications. Preserve
customer privacy and internal notes.

Before changes, verify ownership, assignee, dates, dependencies, status/workflow, billing/costing
rates, project/company, customer, priority, SLA timers and linked transactions. Never close,
resolve, bill, escalate, or email merely to test access.

After changes, verify task/project rollups, timesheet totals and billing state, issue status, SLA
state, linked communications and any accounting effect.
