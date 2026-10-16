---
name: rea-setup
description: Use this skill whenever the user asks to install REA, connect REA to this coding agent, or set up rea-agents. Delegate to upstream setup, show its plan for approval, then verify the installation.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: REA setup runtime** — Provide Node.js and npm/npx supported by the current REA release; check upstream setup requirements before running it.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# REA setup

This is a thin wrapper around [REA's setup flow](https://rea.tools/get-started/),
reserved for future customization. REA owns installation and its investigation skill.

1. Run `npx rea-agents@latest setup` for the current coding agent.
2. Show the concrete setup plan and wait for the user's approval before applying
   configuration changes or installing optional software. Package-download approval
   does not approve the setup plan.
3. After approved setup completes, verify the installation using REA's setup checks
   and the current agent's connection. If a restart is required, report it and verify
   the connection after restart. Report cancellation, errors, or unavailable connection
   evidence as incomplete setup.
