---
name: erpnext-buying-stock
description: Expertly inspect, plan, and safely operate ERPNext buying, supplier, item, warehouse, inventory, serial, batch, replenishment, receiving, stock transfer, reconciliation, valuation, and procurement workflows. Use for Purchase User, Purchase Manager, Purchase Master Manager, Stock User, Stock Manager, Item Manager, and supply-chain work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

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
