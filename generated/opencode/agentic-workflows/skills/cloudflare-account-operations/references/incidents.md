# Incident runbook

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

## Stabilize

1. Confirm the affected account, zones, products, hostnames, and start time.
2. Keep read-only investigation separate from mitigation authority.
3. Gather current configuration, recent deployments, audit logs, DNS state, rules, routes, and Cloudflare response identifiers such as Ray IDs.
4. Prefer the smallest reversible mitigation.

## Decide

1. State evidence, hypothesis, blast radius, mitigation, verification, and rollback.
2. Use explicit user approval for writes unless the user already authorized a clearly bounded emergency action.
3. Do not broaden an emergency instruction from one zone, hostname, script, or rule to the whole account.

## Mitigate

1. Capture the pre-change state.
2. Apply one change at a time when practical.
3. Verify observable service behavior and configuration after each change.
4. Stop when the service is stable or the next action requires broader authority.

## Close

Report timestamps, changed resources, sanitized CLI and API results, validation evidence, remaining
risk, and rollback status. Recommend credential rotation only when exposure is plausible; never
rotate or delete a token without approval.
