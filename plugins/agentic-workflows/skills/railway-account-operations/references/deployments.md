# Railway deployment runbook

Use [Infisical-backed service CLIs](../../agentic-workflows/references/service-browser-operations.md)
and inspect the exposed deployment CLI command's actual effect. Source upload/build,
template provisioning, redeploy, restart, teardown, and rollback are distinct;
do not infer one from a tool name. If the required operation is absent, report it.

Before deployment, resolve repository revision and exact workspace/project/
environment/service IDs, current deployment and domains. Review the entire source
upload set, root directory, monorepo selection, ignore rules, and secret exclusions.
Run the repository's required build/tests, capture a known healthy deployment or
recovery mechanism, and match traffic, production, billing, and data effects to
existing authority under [change management](change-management.md).

Use the supported CLI command with explicit target inputs. A queued or detached result
requires polling its returned operation/deployment ID to terminal status. Then
read deployment and replica/service state, inspect bounded sanitized logs, verify
the real domain/health endpoint, and confirm the deployed revision when observable.
Stop further rollout on failure, crash, unhealthy service, or an unexpected target.
Do not retry an unknown write outcome before readback. Rollback needs authority
covering that recovery; a successful deployment response alone is not health.
