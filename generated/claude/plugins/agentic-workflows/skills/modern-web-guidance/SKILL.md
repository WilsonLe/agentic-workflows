---
name: modern-web-guidance
description: Choose and verify modern web platform APIs, browser compatibility and fallbacks, accessible interactions, performance, or Chrome built-in AI for a web app or extension. Use for API modernization and platform decisions; pair with chrome-extensions for extension contexts. Consult current official sources rather than assuming cached API support.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Modern Web Guidance

This is an original Agentic Workflows companion inspired by Google's initiative. It does
not bundle or automatically update Google's skill collection. For the upstream collection,
follow [Chrome's setup guide](https://developer.chrome.com/docs/extensions/ai/build-with-ai#modern_web_guidance):
`npx modern-web-guidance@latest install --choose`, selecting `chrome-extensions` and
`modern-web-guidance`. Run that installer only when the user requests upstream installation;
check scope and avoid duplicate skill names shadowing the selected provider.

1. Identify the user journey, project stack, target browsers/versions, and execution context.
   Read the existing implementation and preserve its supported environments.
2. Consult current official documentation for each proposed feature. Use
   [Baseline](https://web.dev/baseline) for web-platform interoperability; it does not prove
   support for Chrome extension APIs or a particular user's device. Record the relevant
   browser/version constraints, feature detection, and fallback before implementation.
3. Use semantic HTML and platform controls where they meet the task. Keep labels, keyboard
   operation, visible focus, sensible reading order, contrast, reduced motion, and error
   recovery. Check extension popups and panels at their actual constrained dimensions.
4. Measure the changed journey before adding a performance optimization. For websites use
   [Web Vitals](https://web.dev/articles/vitals) and appropriate real/lab evidence; for
   extensions measure action latency, worker work, page impact, and model download costs.
   A single lab score does not establish field performance.
5. For built-in AI, read [AI availability and lifecycle](references/built-in-ai.md). For
   ordinary web APIs use documented detection (`CSS.supports`, API presence, and capability
   queries as appropriate), then exercise both supported and fallback paths.
6. Verify in the actual target context with suitable browser tools. Report API/source versions,
   tested states, measurements, fallback results, and unavailable runtime cases. Keep
   proposal, static compatibility evidence, and observed browser behavior distinct.
