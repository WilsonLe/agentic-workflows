---
name: excalidraw-api-operations
description: Inspect and manage Excalidraw Plus accounts, workspaces, collections, users, invites, and scenes through the built-in Codex browser using the active account selected for the current project. Optional protected read-only helper diagnostics supplement the browser; the legacy skill name remains for compatibility.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated browser** — In Codex, use the built-in browser; verify the active account and select the current project's exact target in the UI.
- **Required: Excalidraw account** — Sign in to the intended account/site with the UI permissions needed for this task; no API token is required for browser operation.
- **Optional: Read-only CLI diagnostics** — Use existing authorized CLI/helper access only for supplemental logs/status after independently matching the browser identity and target.

<!-- catalog-prerequisites:end -->

# Excalidraw Account Operations

Read [service browser operations](references/browser-selection.md) before operating
this service. In Codex, open or reuse the built-in Codex browser, select the active
account for the current project, and verify the exact target in the visible UI.
Browser operation is the base: use browser controls for management, creation,
updates, and deletion. Optional CLI/helper diagnostics are read-only supplements
and must independently match the browser account and target. Browser onboarding
does not require an API token or CLI installation.

The skill name `excalidraw-api-operations` is retained for existing invocations;
account operations now use the browser by default. For first use, read
[onboarding](references/onboarding.md). Use `excalidraw-scene-operations` for one
scene's canvas, content, backup, and visual verification.

## Core workflow

1. Open Excalidraw Plus and verify the signed-in identity and project workspace.
2. Resolve the exact collection, scene, user, or invite through visible lists,
   URLs, and metadata. Keep collection, scene metadata, and canvas content distinct.
3. Follow [change management](references/change-management.md). Capture pre-state,
   access impact, task authority, readback, and recovery before a mutation.
4. Create, rename, move, share, administer, or delete through supported UI controls.
5. Reopen the exact resource and compare saved state and effective access.
6. If save completion is uncertain, perform safe readback before any retry.

Inspection and planning authorize reads only. Communication, user removal,
sharing, and destructive operations need authority covering the exact effect.
Do not create an invite, collection, scene, or key as an authentication test.

## Optional diagnostics

Read [resource map](references/api-resource-map.md) and
[credential contract](references/credential-contract.md) only for a needed
read-only protected helper diagnostic. Browser work does not require a personal
API key. Match helper identity/workspace/resource independently to the browser
before a read; if identity cannot be proven, skip the diagnostic.
Do not use REST/MCP mutations by default. Missing UI support requires a concrete
limitation and explicit user direction for any alternative write channel.

## Evidence

Report the browser URL, selected account/workspace and resource, authority,
saved-state readback, visual/effective-access verification, and recovery.
Identify supplemental diagnostics separately. Keep private scene data, personal
keys, authorization headers, credential records, and unreviewed logs out of reports.
Read [failure handling](references/errors-and-rate-limits.md) for uncertain outcomes.
