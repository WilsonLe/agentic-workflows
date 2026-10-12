---
name: erpnext-accounting-finance
description: Expertly inspect, plan, and safely operate ERPNext accounting and finance, including chart of accounts, receivables, payables, invoices, payments, journal entries, banking, taxes, assets, budgets, cost centers, dimensions, periods, closing, audit, and financial reports. Use for Accounts User, Accounts Manager, Auditor, Analytics, and finance work.
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

<!-- claude-code-notes:start -->
## Claude Code

Claude in Chrome is available only when its browser tools are in this session's tool list. If they are absent, do not offer to open pages, create keys or tokens, or say you can use Claude in Chrome. Give the user the exact URL and steps to complete themselves; `claude --chrome` or `/chrome` enables browser help in a later session.

<!-- claude-code-notes:end -->

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
