# Railway deployment runbook

## Command distinction

- `railway up` uploads and deploys local source.
- `railway deploy` provisions a template such as a database.
- `redeploy` rebuilds or redeploys the latest deployment without uploading new
  source.
- `restart` restarts the latest deployment without rebuilding.
- `down` removes the most recent deployment.

Never use `deploy` as a synonym for `up`.

## Plan

1. Resolve repository path, workspace, project, environment, service, current
   deployment, domains, and production classification.
2. Inspect `.gitignore` and `.railwayignore`. Do not use `--no-gitignore`
   without reviewing the complete upload set for credentials and local data.
3. Confirm root-directory and `--path-as-root` behavior for monorepos.
4. Run the repository's build and tests before upload.
5. Record the last known healthy deployment or recovery mechanism.
6. Present the exact command, source revision, target IDs, upload scope,
   expected health check, log checks, and rollback.
7. Obtain write approval and separate production approval when applicable.

## Execute and verify

Prefer explicit project, environment, and service flags supported by the
installed CLI. Attached or CI mode must reach a terminal success; detached mode
only proves queuing and requires polling.

After deployment:

1. read the deployment list/status as JSON;
2. inspect bounded build and deployment logs;
3. verify replicas and service state;
4. test the real domain or health endpoint;
5. confirm the deployed revision when observable.

Stop further rollout on `FAILED`, `CRASHED`, an unhealthy service, or an
unexpected target. Redeploy, restart, down, rollback, scaling, and template
provisioning are separate mutations and need their own approved plan.
