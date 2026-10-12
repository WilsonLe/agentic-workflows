---
name: erpnext-buying-stock
description: Expertly inspect, plan, and safely operate ERPNext buying, supplier, item, warehouse, inventory, serial, batch, replenishment, receiving, stock transfer, reconciliation, valuation, and procurement workflows. Use for Purchase User, Purchase Manager, Purchase Master Manager, Stock User, Stock Manager, Item Manager, and supply-chain work.
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

# ERPNext Buying and Stock

First apply `erpnext-operations` for authenticated CLI execution, browser-assisted
credential setup, and browser fallback only for unsupported client capabilities.
Then apply its business controls.

## Business flow

Understand and preserve the chain from Material Request to Request for Quotation, Supplier
Quotation, Purchase Order, Purchase Receipt, Purchase Invoice and Payment Entry. For inventory,
cover Item/variant, UOM, warehouse tree, reorder rules, barcode, batch, serial number, quality
inspection, putaway, pick list, stock entry, transfer, delivery, landed cost and reconciliation.

Before a write, inspect Supplier, Item, UOM conversion, quantities, rates, taxes, schedule,
warehouse, company, cost center/project, batch/serial requirements, valuation method, stock level,
reserved/projected quantity and linked upstream documents.

## Controls and verification

Submitting receipts, invoices, stock entries, transfers, returns, landed costs, reconciliations,
opening stock, valuation adjustments, serial/batch changes, or negative-stock-affecting actions is
high-impact. Preview source/destination warehouses, quantities, valuation/accounting effects and
rollback path, then obtain explicit approval.

Verify linked procurement status, received/billed percentages, Stock Ledger, Stock Balance,
valuation, serial/batch state and General Ledger where perpetual inventory applies. Prefer returns,
cancellation/amendment, or correcting stock transactions over deleting inventory history.
