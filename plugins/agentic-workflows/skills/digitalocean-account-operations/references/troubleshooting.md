# DigitalOcean connected-operation troubleshooting

Follow [the shared provider contract](../../agentic-workflows/references/service-browser-operations.md).
Resolve the intended account/project/resource, then inspect actual connected tool
schemas and applicable plugin instructions. Do not guess CLI flags or raw API calls.

- Missing/expired/mismatched connection: recover through Codex and reverify identity.
- Denied access: report the exact permission gap without another account or token.
- Unsupported resource/action: report the missing tool capability; continue independent work.
- Wrong target: stop and resolve stable IDs before further calls.
- Rate limit/transient read error: follow bounded retry guidance supplied by the tool.
- Unknown mutation outcome: read saved state before considering another write.
- Asynchronous action: poll its returned ID to terminal status, then verify workload health.

Keep diagnostics bounded and sanitized. Never dump environments, tokens, kubeconfig,
registry/database secrets, or raw traces. Investigation does not authorize incident
mitigation; reuse only authority covering the exact target and effect.
