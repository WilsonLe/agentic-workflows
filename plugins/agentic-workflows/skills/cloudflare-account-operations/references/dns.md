# Cloudflare browser DNS runbook

1. Verify the dashboard account and exact zone/hostname.
2. Open the zone's DNS controls and inspect type, name, record target, TTL,
   proxy state, comments/tags, and zone/delegation status without revealing secrets.
3. Preview old/new values and recovery. Check CNAME conflicts, apex behavior,
   mail/verification records, and proxy eligibility.
4. Follow [change management](change-management.md); create/edit/delete using
   supported UI controls, then reopen the exact record to compare saved fields.
5. Verify authoritative DNS through an available browser diagnostic/status view
   when propagation is required. Report unavailable propagation proof explicitly.

DNSSEC, nameservers, production proxy changes, and deletion need exact-effect
scope. Saved records do not prove origin, certificate, email, or application health.
Optional read-only helper inventory must match browser identity and zone; API
PATCH/DELETE is not the default change path.
