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

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Trend Product Operations

Read [drop operations](references/workflow.md). Generate local packets only.
Store draft creation, publication, price/discount changes, inventory purchase,
posting, and spend are separate exact-target mutations. Record observations
separately from calculations and inferences. Expire products and claims when the
source trend cools or evidence becomes stale.
