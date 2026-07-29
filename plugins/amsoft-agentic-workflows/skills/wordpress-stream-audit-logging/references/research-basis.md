# Stream research basis

Refresh these primary sources before installation, upgrade, security, compatibility, scheduler,
integration, or deletion decisions:

- WordPress.org plugin page: https://wordpress.org/plugins/stream/
- XWP upstream repository: https://github.com/xwp/stream
- XWP Stream security policy: https://github.com/xwp/stream/blob/develop/security.md
- Upstream connector inventory: https://github.com/xwp/stream/blob/develop/connectors.md

Verified on 2026-07-29:

- WordPress.org listed Stream 4.3.0 as stable and tested through WordPress 7.0.2.
- Stream exposed filtered activity records, role-based viewing, exclusions, export, multisite, and
  a WP-CLI query command.
- Version 4.3.0 used a scheduler abstraction for automatic purging, preferring Action Scheduler
  with a WP-Cron fallback, and exposed an auto-purge filter.
- Upstream warned against trusting raw `HTTP_*` forwarded headers for client IP.
- Upstream documented uninstall-time data removal as temporarily disabled because deletion is
  impactful and unresolved edge cases remain.
- Stream 4.2.x exposed abilities through WordPress Abilities API/MCP Adapter when those components
  are present.

Treat every version, date, compatibility, security, connector, scheduler, and uninstall statement
as drift-sensitive. Record the exact release/tag and verification date used for a real site.
