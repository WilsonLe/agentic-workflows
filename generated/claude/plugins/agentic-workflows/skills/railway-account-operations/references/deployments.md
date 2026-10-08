# Railway browser deployment runbook

Apply [change management](change-management.md). Use dashboard controls for service
creation, source configuration, deploy/redeploy/restart, scaling, domains, volumes,
and rollback. CLI diagnostics do not authorize deployment commands.

1. Resolve workspace/project/environment/service and current deployment in the UI.
2. Verify source repository, branch/revision, root directory, build/start settings,
   domains, health checks, production impact, and last known healthy deployment.
   Run project build/tests when source changes are part of the task.
3. Distinguish creating a service, deploying a revision, redeploying existing
   source, restarting, and removing a deployment by the observed UI action/effect.
4. Capture rollback/recovery and execute the smallest authorized dashboard action.
5. Observe a terminal deployment state. Inspect bounded build/runtime logs through
   the UI or optional independently matched CLI diagnostics.
6. Reopen deployment and service settings; verify active revision, replicas,
   domain/health endpoint, and relevant application flow when observable.

A queued job is not deployed health. Stop rollout on failure, crash, an unexpected
revision, or an unhealthy service. If local-source upload or another action lacks
supported UI controls, disclose the gap and obtain explicit channel direction
before using an alternative mutation. Do not silently run `railway up`.
