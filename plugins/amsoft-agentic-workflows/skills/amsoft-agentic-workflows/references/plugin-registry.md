# AMSoft Plugin Registry

This is the source of truth for authored plugins registered with AMSoft Agentic Workflows.
“Bundled” means the central plugin contains an integrated copy of the capability. Registration
does not install one plugin from another.

| Plugin | Display name | Version | Source | Marketplace | Capabilities | Central status | Verified |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `amsoft-agentic-workflows` | AMSoft Agentic Workflows | `0.1.0+codex.20260727042309` | `/Users/wilsonle/plugins/amsoft-agentic-workflows` | `personal` | Suite onboarding with conditional GitHub CLI authentication checks, router, registry, academic writing, verified literature research, Humanizer, food image editing, Cloudflare operations | Central plugin; self-registered | 2026-07-27 |
| `academic-writing` | Academic Writing | `1.0.0+codex.local-20260727-042002` | `/Users/wilsonle/plugins/academic-writing` | `personal` | Onboarding, context-complete academic planning, review-gated drafting, verified literature bundles | Bundled as `academic-writing-workflow` and `verified-literature-research`; Hermes skills remain runtime dependencies rather than copied code | 2026-07-27 |
| `humanizer` | Humanizer | `2.5.1+codex.local-20260727-042002` | `/Users/wilsonle/plugins/humanizer` | `personal` | Onboarding, natural-language rewriting and AI-pattern audit | Bundled as `humanizer` | 2026-07-27 |
| `image-editing` | Image Editing | `0.1.0+codex.local-20260727-042002` | `/Users/wilsonle/plugins/image-editing` | `personal` | Onboarding, critical food-image review, angle-aware composition, measurable tone and color correction, deterministic ImageMagick editing, provenance and verification | Bundled as `food-image-editing`; ImageMagick is an external local runtime dependency; no generative tools or code are bundled | 2026-07-27 |
| `cloudflare-account` | Cloudflare Account | `0.1.0+codex.local-20260727-042002` | `/Users/wilsonle/plugins/cloudflare-account` | `personal` | Onboarding, Cloudflare account inspection and approval-gated changes | Bundled as `amsoft-cloudflare-account-operations` with namespaced MCP server and tools | 2026-07-27 |

## Registration rules

- Keep one row per normalized source-plugin name.
- Replace a row when its plugin changes; do not append duplicate history rows.
- Record the installed source version, not an intended version.
- Update the central plugin’s own version row after applying its cachebuster.
- For catalog-only entries, state why the capability is not bundled.
- Never store credentials, tokens, or secret values here.
