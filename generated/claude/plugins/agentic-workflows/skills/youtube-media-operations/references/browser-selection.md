# Browser selection

In Codex, prefer the Codex in-app browser for browser-based work, including
verification, provider dashboards, account setup, sign-in/OAuth, credential
creation, and authenticated source inspection. This is a preferred default;
the user's explicit browser, profile, or tab selection takes precedence.
On other hosts, use that host's supported browser controls.

1. Resolve the exact target and required account, interaction, and evidence
   capabilities. Preflight the Codex browser through the host's documented
   controls and read their documentation before operating a tab. Use a visible
   in-app tab when the user needs to follow or complete a browser step.
2. Use the Codex browser when it supports the required flow. Do not assume it
   shares Chrome's sign-in state, extensions, private-window support, cookie
   export, or browser-specific behavior.
3. If it is unavailable or lacks a required capability, record the limitation
   and use an already-authorized supported browser that reaches the same target
   and account and proves the same claim. Honor an explicitly required browser
   or control channel; if no equivalent satisfies it, report the blocker.
   Switching browsers cannot bypass login, CAPTCHA, access, or policy gates.
4. Record the actual browser/channel and result. A screenshot alone does not
   prove interaction, and browser access does not prove a credential works in
   its intended CLI, API, or integration.

For Railway, Vercel, Cloudflare, DigitalOcean, ERPNext, and Excalidraw, apply
the selected service's channel contract: authenticated CLI/client execution is
the default. Use the built-in Codex browser for missing login/key acquisition,
return to CLI verification, and use browser service operations only for a proven
authenticated client capability gap.
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
