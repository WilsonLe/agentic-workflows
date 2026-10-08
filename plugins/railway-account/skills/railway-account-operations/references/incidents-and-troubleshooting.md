# Railway incidents and optional CLI diagnostics

Establish the browser account/workspace/project/environment/service and incident
window first using [service browser operations](browser-selection.md).
Inspect dashboard status, deployment details, and bounded logs before mitigation.

## Read-only CLI supplement

Use existing authorized CLI access through the protected wrapper. Read
[credential contract](credential-contract.md) only if this optional path is needed.
Verify `whoami --json` and read-only target metadata independently against the
browser identity and scope. Inspect installed help for exact flags; help can
contact the provider, so do not assume a failing help command proves service health.

For log/status reads, constrain the service, environment, deployment/time window,
and line count. The wrapper requires
`--confirm-sensitive-output I_APPROVE_RAILWAY_SENSITIVE_READ` for sensitive output;
supply it only within diagnostic authority. Sanitize application secrets and
personal data before reporting. Never use unbounded log streams or environment dumps.
Missing/mismatched CLI authentication blocks only that diagnostic.

## Failures and mitigation

- Authentication/access failure: report the denied identity/target; do not replace
  credentials, broaden scopes, or select another account silently.
- Empty/missing resource: check dashboard scope, filters, pagination, and exact URL.
- Unknown command: inspect installed help and official documentation for read syntax.
- Transient read failure: use bounded retries; an unknown write outcome needs readback.

Preview evidence, hypothesis, blast radius, reversible mitigation, verification,
and recovery. Execute authorized mitigation through dashboard controls and follow
[change management](change-management.md); optional CLI reads do not authorize writes.
