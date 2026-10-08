---
name: erpnext-manufacturing-assets
description: Expertly inspect, plan, and safely operate ERPNext manufacturing, BOM, production planning, work orders, job cards, subcontracting, quality, maintenance, assets, and fleet. Use for Manufacturing User, Manufacturing Manager, Quality Manager, Maintenance User, Maintenance Manager, Fleet Manager, Fulfillment User, and related operational work.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for the bundled protected command-line clients.
- **Required: Authenticated service CLI** — Use Protected ERPNext command-line client; verify authentication and exact project account/target before remote operations.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# ERPNext Manufacturing, Quality, Maintenance, Assets and Fleet

First apply `erpnext-operations` for authenticated CLI execution, browser-assisted
credential setup, and browser fallback only for unsupported client capabilities.
Then apply its business controls.

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
