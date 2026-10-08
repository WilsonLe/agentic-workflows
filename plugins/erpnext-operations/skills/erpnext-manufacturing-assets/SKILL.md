---
name: erpnext-manufacturing-assets
description: Expertly inspect, plan, and safely operate ERPNext manufacturing, BOM, production planning, work orders, job cards, subcontracting, quality, maintenance, assets, and fleet. Use for Manufacturing User, Manufacturing Manager, Quality Manager, Maintenance User, Maintenance Manager, Fleet Manager, Fulfillment User, and related operational work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: ERPNext account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# ERPNext Manufacturing, Quality, Maintenance, Assets and Fleet

First apply `erpnext-operations`, including its browser account/site/company selection
and browser management workflow. Optional read-only diagnostics must match that context.

## Operational model

Trace demand and supply through Item, BOM/version, Operation, Workstation, Routing, Production Plan,
Work Order, Job Card, material transfer, manufacture/repack Stock Entry, subcontracting and
finished-goods receipt. Include Quality Inspection, Quality Goal/Procedure/Review/Action, equipment
maintenance, Maintenance Schedule/Visit, Asset maintenance/movement/depreciation, Vehicle,
Vehicle Log and expense records where installed.

Before changes, verify company, BOM status/version, quantities and UOMs, source/WIP/finished
warehouses, available/reserved stock, scrap/by-products, operations, workstation capacity,
planned dates, costs, serial/batch requirements, quality template and linked sales/material demand.

## Controls and verification

Releasing production, submitting stock movements/manufacture, completing job cards, accepting or
rejecting quality inspections, changing BOMs, recording downtime, moving/disposal of assets, or
changing vehicle logs can alter stock, capacity, costs, accounting, compliance, or safety records.
Show impact and obtain explicit approval.

After execution, verify Work Order/Job Card completion, consumed and produced quantities, Stock
Ledger, WIP and valuation, quality status, asset history, maintenance schedule, and General Ledger
when applicable. Never fabricate inspection results, completion times, meter readings, serials, or
maintenance evidence.
