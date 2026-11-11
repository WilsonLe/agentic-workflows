# Railway target resolution

Use [Codex connected apps](../../agentic-workflows/references/service-browser-operations.md).
Resolve the intended workspace, project, environment, service, and deployment from
the request and repository evidence, then verify stable IDs and connected identity
through read-only tools. Local directory/link state does not select a remote target.

Production classification uses environment IDs, active domains/traffic, service
role, deployment documentation, and the user's request. An unclear classification
must not be treated as non-production for a write. Resolve it or retain production
impact safeguards and require authority covering that target and effect.

Immediately before consequential writes, re-read relevant state. Stop when the
workspace, project, environment, service, deployment, or configuration unexpectedly
changed. Names may collide or change; use explicit IDs accepted by the tool and do
not overwrite another operator's work from stale evidence.
