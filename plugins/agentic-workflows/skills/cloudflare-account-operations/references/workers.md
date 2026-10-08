# Cloudflare browser Workers and Pages runbook

1. Verify dashboard account, Worker/Pages project, environment, and active version.
2. Inspect source/repository, deployment, compatibility settings, bindings, routes,
   custom domains, and secret names through UI without revealing secret values.
3. Determine the requested source/configuration/version/route/binding effect and
   retain the last healthy revision and recovery path. Check traffic implications.
4. Follow [change management](change-management.md). Use observed dashboard editor,
   project settings, deployment/version, and rollback controls for changes.
5. Reopen the exact project and verify saved configuration, active revision,
   routes/domains, and a relevant live endpoint/user flow.

Optional Wrangler/helper diagnostics are bounded reads after independent scope
matching. Do not deploy, set secrets, alter routes, or delete via Wrangler by
default. If dashboard controls cannot support the operation, disclose that gap
and obtain explicit user direction for an alternative mutation.
