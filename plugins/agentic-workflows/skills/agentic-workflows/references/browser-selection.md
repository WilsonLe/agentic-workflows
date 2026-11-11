# Browser selection

For PostHog and Polar, always use their configured Codex plugins/connected apps
under [the connected-operations contract](service-browser-operations.md#posthog-and-polar-connected-operations).
Codex owns authentication; exclude their tokens from `.cli/` setup and worktree
copies. Recover connections through Codex and report capability/permission gaps.

For Vercel, always use the [Vercel plugin/connected app in Codex](../../vercel-account-operations/SKILL.md).
Codex manages its authentication; exclude Vercel credentials from local `.cli/`
setup and worktree copies. Missing connection or operation support is a blocker.

In Codex, prefer the Codex in-app browser for browser-based work, including
verification, provider dashboards, account setup, sign-in/OAuth, credential
creation, and authenticated source inspection. This is a preferred default;
the user's explicit browser, profile, or tab selection takes precedence.
Without a browser tool, give the user the exact URL and step to complete, then
resume non-browser verification. Never report an unperformed browser action.

1. Resolve the exact target and required account, interaction, and evidence
   capabilities. Preflight the Codex browser tool and read its documentation before operating a
   tab. Use a visible tab when the user needs to follow or complete a browser step.
2. Use that browser when it supports the required flow. In Codex, do not assume
   the in-app browser shares Chrome's sign-in state, extensions, private-window
   support, cookie export, or browser-specific behavior.
3. If it is unavailable or lacks a required capability, record the limitation
   and use an already-authorized supported browser that reaches the same target
   and account and proves the same claim. Honor an explicitly required browser
   or control channel; if no equivalent satisfies it, report the blocker.
   Switching browsers cannot bypass login, CAPTCHA, access, or policy gates.
4. Record the actual browser/channel and result. A screenshot alone does not
   prove interaction, and browser access does not prove a credential works in
   its intended CLI, API, or integration.

For Railway, Cloudflare, and DigitalOcean, apply
the selected service's channel contract: authenticated CLI/client execution is
the default. Use the host's browser controls (the built-in Codex browser in Codex)
for missing login/key acquisition, return to CLI verification, and use browser
service operations only for a proven authenticated client capability gap.
For other tasks, keep supported APIs, connectors, CLIs, and repository test suites
as the execution layer when the task requires them. This preference selects the browser
for browser steps; it does not replace non-browser checks or required engine
coverage. Do not request a new confirmation merely to use an equivalent browser
within existing task authority.

For credentials, verify the supported concealed transfer path before copying or
creating a secret. Never extract or expose passwords, tokens, cookies, clipboard
values, or browser storage in tool output, screenshots, logs, or evidence. If
private entry or human-only authentication is required, let the user complete
that step in the selected browser, then resume and verify the requested flow.
