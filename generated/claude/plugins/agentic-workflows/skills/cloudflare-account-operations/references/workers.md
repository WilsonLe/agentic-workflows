# Workers runbook

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

## Inspect

Use the validated project `.cli/cloudflare` record and child-only Wrangler
authentication described in [onboarding](onboarding.md#project-store); do not
silently fall back to an unrelated global OAuth login.

1. Confirm the configured account and inspect `npx wrangler --help`.
2. Discover the current script, service, route, domain, deployment, and version identifiers.
3. Read metadata, bindings, compatibility date and flags, routes, and recent deployment state.
4. Never retrieve or expose secret values. Report only secret names or binding metadata when the API supports that.

## Plan

1. Determine whether the task changes source, metadata, bindings, routes, domains, secrets, or deployment versions.
2. Prefer Wrangler for supported Worker workflows and consult current Workers documentation;
   commands, upload formats, and version/deployment APIs can change.
3. Preserve the currently deployed version identifier for rollback.
4. Check whether a route or custom domain can redirect production traffic.
5. Present validation and rollback before requesting approval.

## Apply and verify

1. Follow `change-management.md` and inspect the exact Wrangler command help.
2. Prefer versioned deployment flows when the product and endpoint support them.
3. Verify the active deployment/version and relevant routes after the write.
4. Run a bounded health check against the affected hostname or Worker when authorized.
5. If validation fails, stop additional rollout and report the last known good version.

Treat secret changes, route changes, custom-domain changes, production deployments, and script
deletion as high-impact. Wrangler reads `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` from the
environment; never place literal credentials in Wrangler configuration.
