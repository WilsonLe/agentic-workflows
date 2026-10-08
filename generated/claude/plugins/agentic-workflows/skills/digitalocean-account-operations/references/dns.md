# DigitalOcean browser domains and DNS

1. Verify control-panel team/account/project and exact domain.
2. Inspect record type/name/data, priority, port, TTL, weight, and flags as applicable.
3. Preview old/new values and recovery. Check CNAME conflicts, apex behavior,
   mail/verification records, SRV fields, and nameserver delegation.
4. Follow [change management](change-management.md), save through UI, and reopen
   the exact record to verify fields.
5. Verify authoritative DNS using an available browser diagnostic when required;
   state any unavailable propagation evidence.

Domain deletion, production removal, and delegation changes need exact-effect
scope. Record creation alone does not prove origin, certificate, email, or app health.
Read-only doctl inventory is optional after independently matching browser scope.
