---
name: erpnext-sales-crm
description: Expertly inspect, plan, and safely operate ERPNext CRM, selling, delivery, POS, pricing, loyalty, campaigns, customer masters, quotations, sales orders, sales invoices, returns, payments, and sales analytics. Use for Sales User, Sales Manager, Sales Master Manager, Delivery User, Delivery Manager, Marketing Manager, Newsletter Manager, and related work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# ERPNext Sales and CRM

First apply `erpnext-operations` for authenticated CLI execution, browser-assisted
credential setup, and browser fallback only for unsupported client capabilities.
Then apply its business controls.

## Business flow

Choose the shortest controlled flow supported by the business:

- Lead and Opportunity to Quotation, Sales Order, Delivery Note, Sales Invoice and Payment Entry;
- service sales without stock delivery;
- direct invoice with stock update only when policy permits and the user explicitly intends it;
- POS opening, sale, payment, closing and reconciliation;
- returns and credit notes linked to the original transaction;
- Campaign, Email Campaign, Newsletter, Loyalty Program and Loyalty Point Entry.

Inspect Customer, Contact, Address, Territory, Sales Person/Partner, Item, Price List, Item Price,
Pricing Rule, taxes, payment terms, credit limit, warehouse, stock availability and company before
writing. Preserve links between documents so billed/delivered percentages and audit trails remain
correct.

## Controls and verification

Preview customer, items, quantities, rates, discounts, taxes, delivery dates, warehouse, payment
terms, currency, totals and downstream stock/accounting effects. Submitting delivery, invoice, POS,
return, payment, loyalty adjustments, bulk communications, or credit-limit overrides is
high-impact and needs explicit approval.

After execution, verify workflow/docstatus, linked-document status, delivered/billed percentages,
stock ledger when applicable, General Ledger when applicable, outstanding balance, and message
delivery status. Do not send marketing or customer email merely to test access.
