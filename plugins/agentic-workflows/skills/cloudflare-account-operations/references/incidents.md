# Cloudflare browser incident runbook

1. Confirm the browser account, affected zone/product/hostname, incident window,
   deployment/configuration, and exact resource context.
2. Separate investigation from mitigation authority. Inspect bounded dashboard
   metrics, audit/error/log views, DNS, rules/routes, and response/Ray IDs.
3. Optional CLI/helper reads can supplement logs/status after independent identity
   and scope matching; sanitize secrets and personal data before reporting.
4. Preview evidence, hypothesis, blast radius, smallest reversible mitigation,
   verification, and recovery. Apply existing exact-target incident authority.
5. Follow [change management](change-management.md) and perform one UI change at
   a time, checking saved state and observable service behavior after each.
6. Stop when stable or when the next action would broaden scope or lack authority.

Report timestamps, affected resources, browser evidence, sanitized diagnostics,
remaining risk, and rollback. Do not rotate credentials, purge broadly, weaken
security, or switch to an API write merely to investigate an incident.
