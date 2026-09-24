# DNS runbook

## Inspect

1. Find the zone with a read-only curl request to `/zones`.
2. Read `/zones/{zone_id}/dns_records` with encoded filters such as `type` and `name`.
3. Check existing records, TTL, proxied state, comments, tags, and record-specific data.
4. Inspect zone status and nameserver state before diagnosing propagation.

## Plan a record change

1. Identify the exact record ID.
2. Prefer `PATCH /zones/{zone_id}/dns_records/{dns_record_id}` for partial changes when supported.
3. State the old and new type, name, content, TTL, and proxied value.
4. Check for CNAME conflicts, apex behavior, mail records, verification records, and proxy eligibility.
5. Define rollback using the captured old record.

## Apply and verify

1. Follow `change-management.md`.
2. Read the record after the write.
3. Validate authoritative DNS separately when the task requires propagation evidence.
4. Do not interpret a successful API response as proof that an origin, certificate, email flow, or application is healthy.

Treat record deletion, DNSSEC changes, nameserver changes, and production proxy-state changes as high-impact.
