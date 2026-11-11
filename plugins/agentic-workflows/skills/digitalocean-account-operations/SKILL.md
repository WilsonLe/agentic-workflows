---
name: digitalocean-account-operations
description: Use whenever inspecting or managing DigitalOcean accounts, projects, resources, deployments, or incidents. Use the configured Codex plugin/connected app, reuse Codex-managed authentication, and verify the exact target. Report missing connections or capabilities without local CLI tokens or dashboard fallback.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Connected DigitalOcean app** — Use the configured DigitalOcean plugin/connected app in Codex. Reuse Codex-managed authentication and verify the exact account/project/environment through tools. Recover missing connections through Codex and report unavailable operations or permissions without local CLI tokens or dashboard fallback.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# DigitalOcean Account Operations

Use the configured DigitalOcean plugin/connected app through Codex under the
[shared provider channel contract](../agentic-workflows/references/service-browser-operations.md).
Codex owns authentication. Reuse an existing healthy connection and verify the
exact account, project, region, and resource through read-only tools before
operations. Recover missing/expired connections through Codex; report unavailable
operations or permissions without CLI/token, raw account API, or dashboard fallback.
Never infer that this skill's installation establishes a connection.

Before writes or runtime-secret handling, apply
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).
Capture nonsecret pre-state, effect, target, cost/data/traffic impact, validation,
and recovery. Reuse existing in-scope authority; a configured connection grants
none. Preserve production, destructive, charge, and enforced human-approval gates.

## Runbooks

Read [connection onboarding](references/onboarding.md) when needed and
[change management](references/change-management.md) before mutations.

- [Compute/networking](references/compute-networking.md), [DNS](references/dns.md),
  [managed services](references/managed-services.md), and [troubleshooting](references/troubleshooting.md).

Confirm region, project association, billing impact, backups, and asynchronous
resource actions as relevant. A successful action is not workload health. SSH,
kubeconfig, database, registry, and application credentials must stay concealed.
Check actual connector capabilities for each product; a configured DigitalOcean
connection does not imply every managed-service operation is supported.

## Execution and evidence

Execute the smallest supported connected-tool operation. Read back saved state,
wait for asynchronous completion, and verify relevant workload behavior. Unknown
write outcomes require readback before retrying. Keep query/log results bounded;
never expose tokens, authorization data, private records, or environment values.
Report the actual tool, verified identity/target, operation, observed result,
verification limits, and recovery status. Local previews or an acknowledgement
alone do not prove remote success.
