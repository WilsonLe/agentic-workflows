# Workers runbook

Use the [Codex connected-app channel](../../agentic-workflows/references/service-browser-operations.md).
Verify connected identity and the exact target through read-only tools. Missing
connections, operations, or permissions remain blockers; recover through Codex
without local-token or dashboard fallback.

## Inspect

1. Confirm the connected account and discover exposed Worker tools.
2. Discover the current script, service, route, domain, deployment, and version identifiers.
3. Read metadata, bindings, compatibility date and flags, routes, and recent deployment state.
4. Never retrieve or expose secret values. Report only secret names or binding metadata when the API supports that.

## Plan

1. Determine whether the task changes source, metadata, bindings, routes, domains, secrets, or deployment versions.
2. Check the connected tool schema and current provider instructions for source,
   version, binding, and deployment support. Do not assume all Worker operations exist.
3. Preserve the currently deployed version identifier for rollback.
4. Check whether a route or custom domain can redirect production traffic.
5. Present validation and rollback before requesting approval.

## Apply and verify

1. Follow `change-management.md` and inspect the exact tool inputs.
2. Prefer versioned deployment flows when the product and endpoint support them.
3. Verify the active deployment/version and relevant routes after the write.
4. Run a bounded health check against the affected hostname or Worker when authorized.
5. If validation fails, stop additional rollout and report the last known good version.

Treat secret changes, route changes, custom-domain changes, production deployments, and script
deletion as high-impact. Keep application secret values concealed and separate from connector authentication.
