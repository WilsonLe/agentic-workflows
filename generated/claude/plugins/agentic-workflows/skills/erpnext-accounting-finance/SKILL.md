---
name: erpnext-accounting-finance
description: Expertly inspect, plan, and safely operate ERPNext accounting and finance, including chart of accounts, receivables, payables, invoices, payments, journal entries, banking, taxes, assets, budgets, cost centers, dimensions, periods, closing, audit, and financial reports. Use for Accounts User, Accounts Manager, Auditor, Analytics, and finance work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# ERPNext Accounting and Finance

First apply `erpnext-operations` for authenticated CLI execution, browser-assisted
credential setup, and browser fallback only for unsupported client capabilities.
Then apply its business controls. Treat submitted accounting documents and ledger effects as
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

Draft creation still requires approval. Submission, cancellation, amendment, reconciliation,
allocation, write-off, exchange gain/loss, asset posting, closing, or ledger-affecting imports
require an impact preview with totals and affected accounts.

After submission, verify the document, General Ledger entries, outstanding balances, and the
relevant financial report. Reverse through credit/debit notes, returns, cancellation/amendment, or
correcting journal entries as ERPNext supports; do not delete posted history.

Do not give tax, audit, or statutory advice as fact. Preserve jurisdiction, filing period, source
documents, approvals, and uncertainty, and ask for a qualified review when required.
