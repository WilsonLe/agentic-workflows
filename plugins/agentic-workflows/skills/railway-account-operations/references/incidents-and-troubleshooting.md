# Railway incidents and troubleshooting

Use the [Infisical-backed CLI channel](../../agentic-workflows/references/service-browser-operations.md).
Resolve provider identity, exact workspace/project/environment/service and incident
window before bounded reads. Inspect installed command help and current official
provider documentation. Missing tokens require Infisical recovery; denied permissions
or absent CLI commands remain blockers without account/channel switching.

Bound retries of transient reads. Unknown write outcomes require saved-state readback
before another mutation. Capture and sanitize deployment/log results before tool
output; never dump environment values, credentials, private records or raw traces.

Separate diagnosis from mitigation authority. Present evidence, hypothesis, blast
radius, smallest reversible action, verification and recovery. Reuse a request
covering that exact emergency effect, apply one change at a time, and stop when
stable or the next step broadens scope. Observe terminal status and live health.
