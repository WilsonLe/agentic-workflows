# Railway CLI and token onboarding

Follow [the shared CLI-token contract](../../agentic-workflows/references/service-browser-operations.md)
and [Infisical Account Operations](../../infisical-account-operations/SKILL.md).
Inspect the installed `railway` version and command help. Resolve the exact workspace, project, environment, service and deployment
from task/project evidence before authentication or service operations.

1. Authenticate to the verified Infisical instance/profile and resolve project ID,
   environment slug, folder and key. Reuse human-present keyring login or an approved
   machine identity; never create a checkout token store.
2. Obtain `RAILWAY_TOKEN or RAILWAY_API_TOKEN` from Infisical inside the concealed process. Validate presence
   before launching `railway`; clear alternate credentials and bootstrap secrets from
   its child environment. Never send the value through arguments or tool output.
3. Verify provider identity/scope and target IDs with supported read-only CLI commands.
   A local link, token name or Infisical environment label does not select a service
   account or prove production/sandbox. Keep read results bounded and sanitized.
4. Missing/expired tokens require Infisical reauthentication or an authorized token
   update. Missing CLI support and permission denial remain explicit blockers;
   do not switch to connectors, cached CLI login, dashboard operations or a broader
   token. Complete independent work and report the exact gap.

Leave legacy files untouched. Do not harvest, migrate, export, rotate or delete
credentials merely to test access. Worktrees share access to the host keyring;
they never copy provider or Infisical authentication files.
