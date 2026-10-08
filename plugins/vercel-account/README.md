# Vercel Account

Browser-based Vercel Account operations covering accounts, teams, projects, memberships, domains, integrations, spend settings, deployments, and recovery.

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

First prompt: Open Vercel in the built-in Codex browser, select the project team, and inspect its settings.
