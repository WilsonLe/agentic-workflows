# Vercel browser onboarding

Read [service browser operations](browser-selection.md). Browser operation is the
base; API tokens and provider CLI/MCP setup are not prerequisites.

1. Resolve https://vercel.com/dashboard and the current project's intended account from the task,
   repository, domain, or project documentation. Do not guess a private site URL.
2. Open or reuse a visible built-in Codex browser tab and inspect the signed-in
   identity. Let the user complete private password entry, MFA, CAPTCHA, or a
   human-only login step when necessary. Never extract browser credentials.
3. Inspect the account/team/workspace selector and choose the account matching
   this project. Resolve the exact team/account, project, environment, and deployment through observed UI.
   If multiple candidates remain, ask for that choice before acting.
4. Read only enough relevant resources/settings to verify actual access. Do not
   create a resource, generate a key, change permissions, or deploy as a test.
5. Report the browser URL, selected account and project context, reachable
   resources, missing permissions, and next safe step without private details.

Ready means the intended browser identity and target are verified and the UI
supports the requested operation. A login screen, account mismatch, ambiguous
project, or missing UI capability remains a concrete blocker for that step.

## Optional diagnostics

Read-only CLI/helper diagnostics may supplement browser investigation after their
identity and exact target independently match the browser. Prefer existing
authorized authentication. If missing, explain the optional requirement and
continue browser work; use protected setup only when the requested diagnostic
includes that authority. Do not create or rotate credentials for routine browser
onboarding. Non-browser management requires explicit direction for that operation
and disclosure of the UI limitation, as defined in the shared contract.

Suggested first prompt: Open Vercel in the built-in Codex browser,
select the account for this project, and inspect its relevant resources without changes.
