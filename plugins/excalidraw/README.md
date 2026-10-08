# Excalidraw

Browser-based Excalidraw operations covering workspaces, collections, scenes, memberships/invites, canvas editing, backups, and recovery.

In Codex, open or reuse the built-in browser, verify the active signed-in account,
and select the current project's exact team/workspace/resource/environment before
acting. Use visible UI controls for management, creation, updates, and deletion;
reopen the resource to verify saved state and relevant live behavior.

Normal onboarding uses the browser session and UI permissions. No API token,
provider CLI installation, MCP connection, or credential export is required.
On other supported hosts, use authenticated browser controls available there.

CLI/protected helpers remain optional read-only supplements for bounded logs,
status, or diagnosis after independently matching browser identity and exact
scope. Existing helper write capabilities do not authorize CLI/API management.
If the UI cannot complete an operation, report the concrete limitation; use an
alternative mutation channel only under explicit user direction for that step.

Preserve task authority, enforced authentication/approval, secrets, backups, and
rollback. Read-only requests do not authorize changes. Private authentication
and secret entry stay with the user when supported tools cannot conceal them.

First prompt: Open Excalidraw in the built-in Codex browser and verify the account/workspace for this scene.

The legacy skill name `excalidraw-api-operations` remains for compatibility and
now routes account management through the browser. Local scene validation/PNG
rendering remains available for preparation; it does not prove live saved state.
See [render review loop](skills/excalidraw-scene-operations/references/render-review-loop.md).
