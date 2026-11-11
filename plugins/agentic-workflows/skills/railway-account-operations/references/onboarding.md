# Railway connection onboarding

Follow [the shared connected-app contract](../../agentic-workflows/references/service-browser-operations.md)
and the Railway plugin's own tool instructions. Reuse the configured connection;
no local provider-token installation or worktree authentication copy is needed.

1. Resolve the intended workspace, project, environment, service, and deployment from task and project evidence.
2. Discover the exposed connected capabilities and verify identity and target
   read-only. Do not select the first matching resource by name alone.
3. If missing, expired, or mismatched, recover the connection through Codex and
   let the user complete enforced private sign-in, then reverify the target.
4. Report unsupported operations or denied permissions precisely and finish
   independent work. Do not fall back to CLI login, raw account requests,
   broader credentials, or dashboard management.

Do not read, migrate, export, or delete legacy token files. Application runtime
configuration remains separate and follows the project's approved secret mechanism.
