---
name: trend-product-onboarding
description: Initialize a project-local Trend to Product workspace; create demographic audience revisions, read-only source registrations, and configured tracking profiles with explicit Git, privacy, and automation boundaries.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

<!-- claude-code-notes:start -->
## Claude Code

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

<!-- claude-code-notes:end -->

# Trend Product Onboarding

Resolve the exact project before writing. Read [onboarding and ingress](references/workflow.md).
Use `${CLAUDE_PLUGIN_ROOT}/scripts/trend_to_product.py` for deterministic records. Never persist
credentials, cookies, browser profiles, raw headers, or session identifiers.
Creating a tracking profile records intent only; it is not active until a
separately authorized scheduler identifier is bound.
