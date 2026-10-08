---
name: erpnext-buying-stock
description: Expertly inspect, plan, and safely operate ERPNext buying, supplier, item, warehouse, inventory, serial, batch, replenishment, receiving, stock transfer, reconciliation, valuation, and procurement workflows. Use for Purchase User, Purchase Manager, Purchase Master Manager, Stock User, Stock Manager, Item Manager, and supply-chain work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext Buying and Stock

First apply `erpnext-operations`, including its browser account/site/company selection
and browser management workflow. Optional read-only diagnostics must match that context.

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
