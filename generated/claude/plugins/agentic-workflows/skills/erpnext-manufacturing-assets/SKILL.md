---
name: erpnext-manufacturing-assets
description: Expertly inspect, plan, and safely operate ERPNext manufacturing, BOM, production planning, work orders, job cards, subcontracting, quality, maintenance, assets, and fleet. Use for Manufacturing User, Manufacturing Manager, Quality Manager, Maintenance User, Maintenance Manager, Fleet Manager, Fulfillment User, and related operational work.
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
