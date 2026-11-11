# Railway variables and secrets

Use [Codex connected apps](../../agentic-workflows/references/service-browser-operations.md).
Treat variable values as secrets. Discover a names-only/metadata tool or a supported
server-side projection before inventory. If a tool necessarily returns secret
values without a concealed output path, do not call it; report that capability gap.
Client-side redaction after the tool response has exposed a value is insufficient.

For an authorized change, resolve the exact environment/service and variable name,
check existence by metadata, and obtain the value through an approved concealed
runtime-secret input path. Never put secret values in chat, tool arguments/output,
logs, or process arguments. If the connector cannot accept the value without
exposure, report that blocked step rather than provisioning CLI credentials.

Confirm whether the operation stages or triggers deployment and match its actual
write/production effect to existing authority. Verify only presence, resulting
deployment state, and health; never read back the secret value. Sealed variables
do not make ordinary variables safe to display. Deletion needs the exact key,
target, impact, recovery source, and authority covering the destructive effect.
