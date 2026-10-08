---
name: erpnext-people-projects-support
description: Expertly inspect, plan, and safely operate ERPNext and installed Frappe HR people operations, recruitment, attendance, leave, expense claims, projects, tasks, timesheets, support issues, SLAs, warranties, and service work. Use for HR User, HR Manager, Projects User, Projects Manager, Support Team, Academics User, and related work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# ERPNext People, Projects and Support

First apply `erpnext-operations` for authenticated CLI execution, browser-assisted
credential setup, and browser fallback only for unsupported client capabilities.
Then apply its business controls. Detect installed apps and live DocTypes before assuming Frappe HR,
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
