---
name: trend-product-operations
description: Build approval-gated product content, launch, measurement, and retirement packets from persisted trend-product artifacts without silently creating store items, publishing, buying inventory, or activating spend.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Trend Product Operations

Read [drop operations](references/workflow.md). Generate local packets only.
Store draft creation, publication, price/discount changes, inventory purchase,
posting, and spend are separate exact-target mutations. Record observations
separately from calculations and inferences. Expire products and claims when the
source trend cools or evidence becomes stale.
