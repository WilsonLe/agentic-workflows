# DigitalOcean CLI troubleshooting

Follow the [shared CLI-token contract](../../agentic-workflows/references/service-browser-operations.md).
Resolve account/project/resource and inspect installed doctl help before calls.

- Missing/expired token: recover Infisical access or the authorized stored token.
- Denied permission: report the gap without another account or broader credential.
- Unsupported resource/action: report missing CLI coverage; continue independent work.
- Wrong target: stop and resolve stable IDs.
- Transient read failure: use bounded documented retries.
- Unknown mutation outcome: read saved state before another write.
- Asynchronous action: poll its returned ID, then verify workload health.

Keep diagnostics bounded and sanitized before tool output. Never dump tokens,
environments, kubeconfig, registry/database secrets or traces. Investigation does
not authorize mitigation. No connector, cached-login, raw account API or dashboard
fallback applies.
