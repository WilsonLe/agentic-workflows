# Vercel browser deployments, secrets, and recovery

Apply [service browser operations](browser-selection.md). Onboarding stops before
project creation/linking and deployment. For a deployment task, resolve the team,
project, environment, source repository/branch/revision, current deployment, and URL.

Use dashboard controls for source/configuration, deploy/redeploy, promotion,
domains, protection, environment changes, and rollback. Production and preview are
separate effects; bind authority to the exact environment and source revision.
If a local/prebuilt upload lacks a supported UI path, report that gap before an
explicitly directed alternative channel. Do not silently run CLI deployment.

Inspect environment names and metadata without values. For secret changes use a
verified concealed UI entry path; otherwise the user completes private entry.
Never display decrypted variables, `env pull` output/files, or auth files.
Identify whether changes need a redeployment before claiming they are active.

Build/runtime logs may use optional CLI diagnostics after independent identity,
team/project/environment matching. Bound the deployment and time window and
sanitize output. Keep protection enabled; use the authorized browser login for
protected previews. Do not weaken access to make a check pass.

Preserve the previous healthy deployment and configuration/data recovery needs.
After deployment/rollback, observe terminal status, reopen the deployment, verify
revision/alias/URL, and exercise the relevant user flow. Configuration and durable
state need their own readback; successful upload is not live availability.
