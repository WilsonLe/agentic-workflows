---
name: chrome-extensions
description: Build, change, debug, or prepare Chrome extensions for the Chrome Web Store. Use for Manifest V3, content scripts, service workers, popups, side panels, extension permissions, Chrome DevTools extension testing, and CHROMEWEBSTORE.md. Follow the project's delivery workflow and explicit publication authority.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Optional: Python runtime** — Install Python 3.10 or newer to run the bundled offline manifest audit.
- **Optional: Chrome DevTools runtime** — For browser verification, configure Chrome DevTools MCP with extension tools and a compatible Chrome version; consult references/devtools-testing.md before connecting a profile.

<!-- catalog-prerequisites:end -->

# Chrome extensions

Use this workflow for extension projects. It supplies domain guidance; the project's
repository workflow still governs issues, checks, and PR delivery.

1. Inspect the extension source, build command, generated output, manifest, tests, and
   existing store metadata. Identify the user's single purpose, supported Chrome versions,
   affected surfaces, data flow, and acceptance cases. For a new extension, choose the
   smallest UI and permissions that serve that purpose; keep an existing stack for changes.
2. Read [architecture and security](references/architecture-and-security.md) before choosing
   execution contexts, permissions, or messaging. Use Manifest V3 for new projects. Fetch
   current official API documentation for the selected APIs and minimum Chrome version;
   cached examples cannot establish API availability.
3. Implement in the appropriate context. Keep privileged operations in the worker or an
   extension page, DOM work in a content script or page, and durable state in storage.
   Read [Modern Web Guidance](../modern-web-guidance/SKILL.md) for new web APIs, accessible UI,
   performance, or built-in AI. Bundle executable code with the extension.
4. Create or reconcile `CHROMEWEBSTORE.md` whenever creating or changing an extension, even
   when publication is deferred. Read [store readiness](references/store-readiness.md) and
   start from [the store template](templates/CHROMEWEBSTORE.md) only if the project has no
   existing format. Match every required/optional API and host permission to its actual use.
5. Build using the project's commands, then run the offline audit against the unpacked build:
   `python3 <skill-root>/scripts/audit_extension.py <unpacked-extension-directory>`.
   Replace `<skill-root>` with this installed skill's absolute directory. Exit 0 means only
   the documented static checks passed; inspect warnings and use Chrome for runtime validation.
6. Follow [DevTools setup and testing](references/devtools-testing.md) to install and exercise
   the exact unpacked output in a task-owned Chrome profile. Test the changed surfaces,
   worker restart, permission denial, and relevant empty/error states. If the tools or browser
   are unavailable, complete static checks and report the specific unverified runtime cases.
7. Report the candidate version/build path, static results, browser/profile/extension identity,
   exercised flows, and remaining limitations. Store preparation is complete when metadata
   matches behavior and unresolved facts are visibly marked. Submission or publication needs
   explicit authority for the exact extension/account; preparation alone does not grant it.

Read [evaluation scenarios](references/evaluation-scenarios.md) when revising this workflow.
These are acceptance prompts, not claimed agent benchmark results.
