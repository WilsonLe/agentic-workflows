---
name: erpnext-accounting-finance
description: Expertly inspect, plan, and safely operate ERPNext accounting and finance, including chart of accounts, receivables, payables, invoices, payments, journal entries, banking, taxes, assets, budgets, cost centers, dimensions, periods, closing, audit, and financial reports. Use for Accounts User, Accounts Manager, Auditor, Analytics, and finance work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext Accounting and Finance

First apply `erpnext-operations`, including its browser account/site/company selection
and browser management workflow. Optional read-only diagnostics must match that context. Treat submitted accounting documents and ledger effects as
high-impact.

## Operating knowledge

Trace every request through the relevant master data, document chain, and ledger:

- Customer/Supplier, Item, Account, Cost Center, Project, Finance Book and Accounting Dimension;
- Sales/Purchase Invoice, Payment Entry, Journal Entry, credit/debit note, advance and allocation;
- Bank Account, Bank Transaction, reconciliation and payment order;
- tax templates, tax rules, withholding, currency/exchange rate and payment terms;
- Asset, depreciation, capitalization, movement and disposal;
- Budget, period closing, opening balances and year-end closing;
- General Ledger, receivable/payable, trial balance, P&L, balance sheet, cash flow and audit trail.

Before any write, verify company, posting date/time, fiscal year, currency, exchange rate, party,
accounts, dimensions, references, taxes, totals, outstanding amounts, workflow, and `docstatus`.
Never guess debit/credit direction or use a suspense account merely to force submission.

## Transaction controls

Draft creation still requires task authority covering the document and business effect. Submission, cancellation, amendment, reconciliation,
allocation, write-off, exchange gain/loss, asset posting, closing, or ledger-affecting imports
require an impact preview with totals and affected accounts.

After submission, verify the document, General Ledger entries, outstanding balances, and the
relevant financial report. Reverse through credit/debit notes, returns, cancellation/amendment, or
correcting journal entries as ERPNext supports; do not delete posted history.

Do not give tax, audit, or statutory advice as fact. Preserve jurisdiction, filing period, source
documents, approvals, and uncertainty, and ask for a qualified review when required.
