# DigitalOcean domains and DNS runbook

Use the [Codex connected-app channel](../../agentic-workflows/references/service-browser-operations.md).
Verify connected identity and the exact target through read-only tools. Missing
connections, operations, or permissions remain blockers; recover through Codex
without local-token or dashboard fallback.

## Inspect

1. Discover connected domain/record tools and their required inputs.
2. List domains, then list records for the exact domain through connected tools.
3. Resolve record IDs and capture type, name, data, priority, port, TTL, weight, and flags where
   applicable.
4. Check nameserver delegation separately before diagnosing propagation.

## Plan, apply, and verify

1. State the old and new record values and the exact domain and record ID.
2. Check CNAME conflicts, apex behavior, mail records, verification records, SRV fields, and TTL.
3. Define rollback from the captured record.
4. Follow `change-management.md`, then re-list or read the record.
5. Validate authoritative DNS separately when propagation evidence is required.

Treat domain deletion, production record removal, and nameserver changes as high impact. Do not
treat successful record creation as proof an origin, certificate, email service, or application is
healthy.
