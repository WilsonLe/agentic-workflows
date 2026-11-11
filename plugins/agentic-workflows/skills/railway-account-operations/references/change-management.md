# Railway change runbook

Use [Codex connected apps](../../agentic-workflows/references/service-browser-operations.md)
for every remote mutation. Verify connected identity and exact workspace/project/
environment/service/deployment IDs through read-only tools. Capture nonsecret
pre-state, inspect tool inputs, classify production/account/destructive impacts,
and state the intended operation, cost/data/traffic effect, validation, and recovery.

Match the exact target and effect to the originating request or existing authority
under [the shared authority contract](task-authority-and-secrets.md). Reuse that
authority for necessary in-scope steps; retain enforced provider approvals and ask
only for genuinely missing authority or a material unresolved decision.

Execute the smallest supported connected operation. Stop on unexpected targets,
errors, or unknown outcomes; read back before retrying. Verify changed fields,
asynchronous terminal state, bounded logs, and external behavior when relevant.
Report target IDs, sanitized operation/result, saved-state comparison, behavior,
and recovery. Rollback is not automatic unless existing authority covers it.
