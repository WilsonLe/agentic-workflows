# Skills-first distribution audit

Audit date: 2026-10-31. Scope: PR #70 / issue #69, including the requested Git-worktree default.

This is a snapshot of this refactor, not a second maintained catalog. Discovery uses the existing catalog, mirror declarations, all installed source files and manifest/hook registration. It covers all 66 skill entrypoints, all 41 remaining executable helper source files, the single executable HTML task template, and every automatic registration. Canonical component sources and generated distributions are reconciled by the existing generator.

## Architecture and dispositions

- Ordinary feature entrypoints are skills, selected through names/descriptions and the suite router. Remove the custom repository workflow-routing hook and its implementation; ordinary routing does not depend on prompt injection.
- Retain the automatic-title hook as the user's explicit exception. Its three supporting code files and existing privacy/manual/pin protections remain unchanged.
- Keep the 38 task-specific helpers listed below for their concrete deterministic, protected-credential or evidence/data responsibilities. They run only for an explicit task, not merely because the plugin is installed. No new helper, launcher, host adapter or coordination engine is added.
- Delegation owns session/task lifecycle. Configuration transfer owns export/import/activation/restore. The earlier launch section remains a compatibility link, and duplicate orchestration readback prose is removed.
- New independent Git sessions default to a new isolated worktree before launch, including read-only audits. Explicit directory/lane choices, native subagents and resumes have distinct documented behavior. Verify the actual working directory and preserve source edits/local setup.
- Retain compatibility source packages and deterministic distribution mirrors with their existing consumers; README explains which file is canonical. Broad deletion/renaming without a migration would break those consumers.

## Install and automatic-entrypoint inventory

| Surface | Disposition | Evidence |
| --- | --- | --- |
| Published plugin | One `agentic-workflows` bundle | Both marketplaces and catalog publish only the complete bundle. |
| Skill discovery | Keep, 66 Codex / 56 portable skills | `skills: ./skills/`; canonical table below; generator checks all supported distributions. |
| UI prompts, prerequisite/executable lists and capability maps | Keep descriptive skill metadata | These describe invocation/setup; they do not execute an install command or add a background service. Explicit-only invocation policy remains intact where declared. |
| Repository workflow routing | Replace custom hook with skill discovery | `hooks/workflow_route.py` and its hook entry are removed; ordinary SDLC/router skill metadata remains. |
| Automatic titles | Keep explicit hook exception | The sole `UserPromptSubmit` handler is asynchronous `title_background.py`; its existing Windows command is retained. |
| Custom MCP servers / install scripts | None registered by this bundle | Central manifest has no MCP/server or install-command registration; optional provider CLIs remain task prerequisites. |
| Bundled Codex preset | Keep opt-in task asset | Only config-transfer activation applies it; generated Claude packages contain no `config.toml`. |
| Repository generator/tests/validators | Keep development tooling, outside installed bundle | They generate/check packages and do not add behavior to a consuming harness. |

## Every skill entrypoint

| Skill | Harnesses | Direct helper references in its Markdown |
| --- | --- | --- |
| [`academic-writing-workflow`](../plugins/agentic-workflows/skills/academic-writing-workflow/SKILL.md) | codex, claude-code, opencode | `init_academic_project.py` |
| [`agent-instruction-design`](../plugins/agentic-workflows/skills/agent-instruction-design/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`agentic-workflows`](../plugins/agentic-workflows/skills/agentic-workflows/SKILL.md) | codex, claude-code, opencode | `check_goal_continuity.py`, `diagnose_installed_plugins.py`, `session_title.py`, `title_background.py` |
| [`agentic-workflows-config-transfer`](../plugins/agentic-workflows/skills/agentic-workflows-config-transfer/SKILL.md) | codex | `agentic_workflow_config_transfer.py`, `codex_config.py` |
| [`audio-editing`](../plugins/agentic-workflows/skills/audio-editing/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`budgeting-account-sync`](../plugins/agentic-workflows/skills/budgeting-account-sync/SKILL.md) | codex | Native tools/instructions; companion skills retain their own helpers |
| [`budgeting-transactions`](../plugins/agentic-workflows/skills/budgeting-transactions/SKILL.md) | codex | Native tools/instructions; companion skills retain their own helpers |
| [`calorie-tracker`](../plugins/agentic-workflows/skills/calorie-tracker/SKILL.md) | codex | `calorie_tracker.py` |
| [`chrome-extensions`](../plugins/agentic-workflows/skills/chrome-extensions/SKILL.md) | codex, claude-code, opencode | `audit_extension.py` |
| [`cloudflare-account-operations`](../plugins/agentic-workflows/skills/cloudflare-account-operations/SKILL.md) | codex, claude-code, opencode | `cloudflare_api.py`, `cloudflare_configure_credentials.py` |
| [`david-jones-till-sales`](../plugins/agentic-workflows/skills/david-jones-till-sales/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`delegation`](../plugins/agentic-workflows/skills/delegation/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`digitalocean-account-operations`](../plugins/agentic-workflows/skills/digitalocean-account-operations/SKILL.md) | codex, claude-code, opencode | `digitalocean_cli.py`, `digitalocean_configure_credentials.py` |
| [`engineering-diagnosis`](../plugins/agentic-workflows/skills/engineering-diagnosis/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`engineering-exploration`](../plugins/agentic-workflows/skills/engineering-exploration/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`engineering-intake`](../plugins/agentic-workflows/skills/engineering-intake/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`engineering-review`](../plugins/agentic-workflows/skills/engineering-review/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-accounting-finance`](../plugins/agentic-workflows/skills/erpnext-accounting-finance/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-buying-stock`](../plugins/agentic-workflows/skills/erpnext-buying-stock/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-content-analytics`](../plugins/agentic-workflows/skills/erpnext-content-analytics/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-manufacturing-assets`](../plugins/agentic-workflows/skills/erpnext-manufacturing-assets/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-operations`](../plugins/agentic-workflows/skills/erpnext-operations/SKILL.md) | codex, claude-code, opencode | `erpnext_api.py`, `erpnext_configure_credentials.py` |
| [`erpnext-organization-administration`](../plugins/agentic-workflows/skills/erpnext-organization-administration/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-people-projects-support`](../plugins/agentic-workflows/skills/erpnext-people-projects-support/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`erpnext-sales-crm`](../plugins/agentic-workflows/skills/erpnext-sales-crm/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`excalidraw-api-operations`](../plugins/agentic-workflows/skills/excalidraw-api-operations/SKILL.md) | codex, claude-code, opencode | `excalidraw_api.py` |
| [`excalidraw-scene-operations`](../plugins/agentic-workflows/skills/excalidraw-scene-operations/SKILL.md) | codex, claude-code, opencode | `excalidraw_api.py`, `excalidraw_render.py` |
| [`food-image-editing`](../plugins/agentic-workflows/skills/food-image-editing/SKILL.md) | codex | Native tools/instructions; companion skills retain their own helpers |
| [`grill-me`](../plugins/agentic-workflows/skills/grill-me/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`guided-writing-coach`](../plugins/agentic-workflows/skills/guided-writing-coach/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`human-setup-guide`](../plugins/agentic-workflows/skills/human-setup-guide/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`humanizer`](../plugins/agentic-workflows/skills/humanizer/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`literature-review-workflow`](../plugins/agentic-workflows/skills/literature-review-workflow/SKILL.md) | codex, claude-code, opencode | `literature_review.py` |
| [`modern-web-guidance`](../plugins/agentic-workflows/skills/modern-web-guidance/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`motion-design`](../plugins/agentic-workflows/skills/motion-design/SKILL.md) | codex, claude-code, opencode | `verify_video.py` |
| [`music-composition`](../plugins/agentic-workflows/skills/music-composition/SKILL.md) | codex, claude-code, opencode | `synthesize_score.py` |
| [`orchestration`](../plugins/agentic-workflows/skills/orchestration/SKILL.md) | codex | `orchestration_state.py` |
| [`payloadcms-development`](../plugins/agentic-workflows/skills/payloadcms-development/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`ponytail`](../plugins/agentic-workflows/skills/ponytail/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`product-playtest`](../plugins/agentic-workflows/skills/product-playtest/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`qr-code-generation`](../plugins/agentic-workflows/skills/qr-code-generation/SKILL.md) | codex, claude-code, opencode | `qr_code_generator.py` |
| [`railway-account-operations`](../plugins/agentic-workflows/skills/railway-account-operations/SKILL.md) | codex, claude-code, opencode | `railway_cli.py`, `railway_configure_credentials.py` |
| [`rea-setup`](../plugins/agentic-workflows/skills/rea-setup/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`reddit-browsing`](../plugins/agentic-workflows/skills/reddit-browsing/SKILL.md) | codex | Native tools/instructions; companion skills retain their own helpers |
| [`restaurant-marketing-management`](../plugins/agentic-workflows/skills/restaurant-marketing-management/SKILL.md) | codex, claude-code, opencode | `restaurant_marketing.py` |
| [`sdlc-loop`](../plugins/agentic-workflows/skills/sdlc-loop/SKILL.md) | codex | `orchestration_state.py` |
| [`session-reflection`](../plugins/agentic-workflows/skills/session-reflection/SKILL.md) | codex | `reflection_state.py`, `session_evidence.py` |
| [`speech-to-text`](../plugins/agentic-workflows/skills/speech-to-text/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`standard-development-workflow`](../plugins/agentic-workflows/skills/standard-development-workflow/SKILL.md) | codex | `check_async_feedback.py`, `orchestration_state.py`, `project_adrs.py`, `standard_workflow_record.py` |
| [`supabase-cli`](../plugins/agentic-workflows/skills/supabase-cli/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`systematic-literature-review-workflow`](../plugins/agentic-workflows/skills/systematic-literature-review-workflow/SKILL.md) | codex, claude-code, opencode | `systematic_review.py` |
| [`text-to-speech`](../plugins/agentic-workflows/skills/text-to-speech/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`trading-strategy-research`](../plugins/agentic-workflows/skills/trading-strategy-research/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`trend-product-design`](../plugins/agentic-workflows/skills/trend-product-design/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`trend-product-discovery`](../plugins/agentic-workflows/skills/trend-product-discovery/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`trend-product-onboarding`](../plugins/agentic-workflows/skills/trend-product-onboarding/SKILL.md) | codex, claude-code, opencode | `trend_to_product.py` |
| [`trend-product-operations`](../plugins/agentic-workflows/skills/trend-product-operations/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`trend-product-opportunity`](../plugins/agentic-workflows/skills/trend-product-opportunity/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`typography`](../plugins/agentic-workflows/skills/typography/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`ui-design`](../plugins/agentic-workflows/skills/ui-design/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`vercel-account-operations`](../plugins/agentic-workflows/skills/vercel-account-operations/SKILL.md) | codex, claude-code, opencode | Native tools/instructions; companion skills retain their own helpers |
| [`verified-literature-research`](../plugins/agentic-workflows/skills/verified-literature-research/SKILL.md) | codex, claude-code, opencode | `verify_research_bundle.py` |
| [`video-editing`](../plugins/agentic-workflows/skills/video-editing/SKILL.md) | codex, claude-code, opencode | `index_assets.py`, `verify_video.py` |
| [`youtube-content-inspection`](../plugins/agentic-workflows/skills/youtube-content-inspection/SKILL.md) | codex, claude-code, opencode | `youtube_yt_dlp.py` |
| [`youtube-library-sync`](../plugins/agentic-workflows/skills/youtube-library-sync/SKILL.md) | codex, claude-code, opencode | `youtube_yt_dlp.py` |
| [`youtube-media-operations`](../plugins/agentic-workflows/skills/youtube-media-operations/SKILL.md) | codex, claude-code, opencode | `codex_browser_cookies.mjs`, `youtube_cookie_store.py`, `youtube_yt_dlp.py` |

A helper imported by another helper is accounted for in the full code inventory below; absence from a skill's direct Markdown references does not imply an unowned automatic entrypoint.

## Every executable helper source file

| Installed file | Canonical owner | Supporting responsibility and necessity |
| --- | --- | --- |
| `hooks/session_title.py` | [plugins/agentic-workflows/hooks/session_title.py](../plugins/agentic-workflows/hooks/session_title.py) | **Title exception:** Tracks exact event identity, opt-out, manual/pinned protection and verified title writes; retained with the expressly permitted title hook. |
| `hooks/title_background.py` | [plugins/agentic-workflows/hooks/title_background.py](../plugins/agentic-workflows/hooks/title_background.py) | **Title exception:** Runs the permitted title operation asynchronously and confines native title writes to the originating session. |
| `hooks/title_generator.py` | [plugins/agentic-workflows/hooks/title_generator.py](../plugins/agentic-workflows/hooks/title_generator.py) | **Title exception:** Bounds isolated title inference and rejects sensitive/malformed output; belongs only to the permitted title feature. |
| `scripts/account_credential_common.py` | [plugins/excalidraw/scripts/account_credential_common.py](../plugins/excalidraw/scripts/account_credential_common.py) | **Protected provider credentials:** Enforces protected paths, private file permissions and concealed credential transport shared by explicit provider tasks. |
| `scripts/agentic_workflow_config_transfer.py` | [plugins/agentic-workflows/scripts/agentic_workflow_config_transfer.py](../plugins/agentic-workflows/scripts/agentic_workflow_config_transfer.py) | **Configuration transfer:** Implements authenticated encryption, protected key/passphrase handling, staged verification and rollback for an explicit transfer operation. |
| `scripts/calorie_tracker.py` | [plugins/calorie-tracker/scripts/calorie_tracker.py](../plugins/calorie-tracker/scripts/calorie_tracker.py) | **Calorie tracking:** Normalizes nutrition data and constructs validated/idempotent Sheets payloads; the skill/native connector owns analysis and writes. |
| `scripts/cloudflare_api.py` | [plugins/agentic-workflows/scripts/cloudflare_api.py](../plugins/agentic-workflows/scripts/cloudflare_api.py) | **Cloudflare operations:** Runs scoped API requests without placing protected tokens in model-visible output or arguments. |
| `scripts/cloudflare_configure_credentials.py` | [plugins/agentic-workflows/scripts/cloudflare_configure_credentials.py](../plugins/agentic-workflows/scripts/cloudflare_configure_credentials.py) | **Cloudflare setup:** Conceals token entry/storage and verifies the selected account on an explicit setup request. |
| `scripts/codex_browser_cookies.mjs` | [plugins/youtube/scripts/codex_browser_cookies.mjs](../plugins/youtube/scripts/codex_browser_cookies.mjs) | **Authorized media retrieval:** Provides the existing origin-scoped concealed CDP-to-stdin cookie channel; not a registered JS plugin or automatic hook. |
| `scripts/diagnose_installed_plugins.py` | [plugins/agentic-workflows/scripts/diagnose_installed_plugins.py](../plugins/agentic-workflows/scripts/diagnose_installed_plugins.py) | **Plugin troubleshooting:** Checks provider/source/cache parity and captured discovery without exposing credentials; native inventory alone does not check those invariants. |
| `scripts/digitalocean_cli.py` | [plugins/agentic-workflows/scripts/digitalocean_cli.py](../plugins/agentic-workflows/scripts/digitalocean_cli.py) | **DigitalOcean operations:** Supplies protected account credentials to native doctl and redacts credential-bearing failures. |
| `scripts/digitalocean_configure_credentials.py` | [plugins/agentic-workflows/scripts/digitalocean_configure_credentials.py](../plugins/agentic-workflows/scripts/digitalocean_configure_credentials.py) | **DigitalOcean setup:** Conceals local token installation and verifies the intended account. |
| `scripts/erpnext_api.py` | [plugins/erpnext-operations/scripts/erpnext_api.py](../plugins/erpnext-operations/scripts/erpnext_api.py) | **ERPNext operations:** Provides concealed authenticated requests and consistent error handling for explicit module tasks. |
| `scripts/erpnext_configure_credentials.py` | [plugins/erpnext-operations/scripts/configure_credentials.py](../plugins/erpnext-operations/scripts/configure_credentials.py) | **ERPNext setup:** Conceals credential installation and verifies the intended ERPNext instance. |
| `scripts/excalidraw_api.py` | [plugins/excalidraw/scripts/excalidraw_api.py](../plugins/excalidraw/scripts/excalidraw_api.py) | **Excalidraw operations:** Validates typed operations and exact destructive targets while keeping the personal key concealed. |
| `scripts/excalidraw_configure_credentials.py` | [plugins/excalidraw/scripts/excalidraw_configure_credentials.py](../plugins/excalidraw/scripts/excalidraw_configure_credentials.py) | **Excalidraw setup:** Conceals personal-key installation and verifies the selected account. |
| `scripts/excalidraw_credential_common.py` | [plugins/excalidraw/scripts/excalidraw_credential_common.py](../plugins/excalidraw/scripts/excalidraw_credential_common.py) | **Excalidraw credential binding:** Binds the shared protected credential primitives to the correct provider namespace; no independent credential framework. |
| `scripts/excalidraw_render.py` | [plugins/excalidraw/scripts/excalidraw_render.py](../plugins/excalidraw/scripts/excalidraw_render.py) | **Excalidraw scene rendering:** Validates scene data and drives deterministic PNG rendering; the skill owns design and API decisions. |
| `scripts/orchestration_state.py` | [plugins/agent-orchestration/scripts/orchestration_state.py](../plugins/agent-orchestration/scripts/orchestration_state.py) | **Explicit orchestration evidence:** Validates coordination records, revision compare-and-swap and exclusive worktree claims for invoked control-plane tasks; does not register or launch a background harness engine. |
| `scripts/qr_code_generator.py` | [plugins/qr-code-generator/scripts/qr_code_generator.py](../plugins/qr-code-generator/scripts/qr_code_generator.py) | **QR generation:** Encodes exact payloads, composes safe pixels and checks real decoding; prose or image synthesis cannot establish pixel-level correctness. |
| `scripts/railway_cli.py` | [plugins/railway-account/scripts/railway_cli.py](../plugins/railway-account/scripts/railway_cli.py) | **Railway operations:** Runs native Railway CLI with scoped concealed credentials and checked noninteractive behavior. |
| `scripts/railway_configure_credentials.py` | [plugins/railway-account/scripts/railway_configure_credentials.py](../plugins/railway-account/scripts/railway_configure_credentials.py) | **Railway setup:** Conceals token setup and verifies the intended account before explicit operations. |
| `scripts/trend_to_product.py` | [plugins/trend-to-product/scripts/trend_to_product.py](../plugins/trend-to-product/scripts/trend_to_product.py) | **Trend/product artifacts:** Checks versioned project artifacts and approval/economics consistency; no store publishing or autonomous scheduler. |
| `scripts/youtube_cookie_store.py` | [plugins/youtube/scripts/youtube_cookie_store.py](../plugins/youtube/scripts/youtube_cookie_store.py) | **Authorized media retrieval:** Protects cookie exports and temporary scoped files with cleanup; no browser/session scanner is installed. |
| `scripts/youtube_yt_dlp.py` | [plugins/youtube/scripts/youtube_yt_dlp.py](../plugins/youtube/scripts/youtube_yt_dlp.py) | **Media inspection/retrieval:** Bounds native yt-dlp calls, request inputs and download scopes; the skill controls authorization and selection. |
| `skills/academic-writing-workflow/scripts/init_academic_project.py` | [plugins/agentic-workflows/skills/academic-writing-workflow/scripts/init_academic_project.py](../plugins/agentic-workflows/skills/academic-writing-workflow/scripts/init_academic_project.py) | **Academic workspace setup:** Creates the repeated stage/file contract without overwriting existing work; the skill retains its manual-structure fallback and approval decisions. |
| `skills/agentic-workflows/scripts/check_goal_continuity.py` | [plugins/agentic-workflows/skills/agentic-workflows/scripts/check_goal_continuity.py](../plugins/agentic-workflows/skills/agentic-workflows/scripts/check_goal_continuity.py) | **Goal evidence replay:** Checks supplied secret-free continuation traces; never creates or drives a host goal and cannot prove live adherence. |
| `skills/agentic-workflows-config-transfer/scripts/codex_config.py` | [plugins/agentic-workflows/skills/agentic-workflows-config-transfer/scripts/codex_config.py](../plugins/agentic-workflows/skills/agentic-workflows-config-transfer/scripts/codex_config.py) | **Explicit Codex activation:** Preserves TOML comments/unrelated settings and atomically backs up/restores explicit local activation; installation does not invoke it. |
| `skills/chrome-extensions/scripts/audit_extension.py` | [plugins/chrome-extensions/skills/chrome-extensions/scripts/audit_extension.py](../plugins/chrome-extensions/skills/chrome-extensions/scripts/audit_extension.py) | **Chrome extension audit:** Performs bounded offline MV3 checks without executing extension code. |
| `skills/literature-review-workflow/scripts/literature_review.py` | [plugins/literature-review/skills/literature-review-workflow/scripts/literature_review.py](../plugins/literature-review/skills/literature-review-workflow/scripts/literature_review.py) | **Literature-review artifacts:** Checks research artifact structure and consistency; does not substitute for reading or synthesizing papers. |
| `skills/motion-design/scripts/verify_video.py` | [plugins/agentic-workflows/skills/motion-design/scripts/verify_video.py](../plugins/agentic-workflows/skills/motion-design/scripts/verify_video.py) | **Video delivery verification:** Checks decoded deliverable properties against requested values using native media tools. |
| `skills/music-composition/scripts/synthesize_score.py` | [plugins/agentic-workflows/skills/music-composition/scripts/synthesize_score.py](../plugins/agentic-workflows/skills/music-composition/scripts/synthesize_score.py) | **Music synthesis:** Produces deterministic PCM/cues from an original score; an explicit media-generation helper, not a harness feature. |
| `skills/restaurant-marketing-management/scripts/restaurant_marketing.py` | [plugins/restaurant-marketing/skills/restaurant-marketing-management/scripts/restaurant_marketing.py](../plugins/restaurant-marketing/skills/restaurant-marketing-management/scripts/restaurant_marketing.py) | **Restaurant campaign artifacts:** Checks campaign records, required approval/economics fields and consistency without publishing or contacting services. |
| `skills/session-reflection/scripts/reflection_state.py` | [plugins/agentic-workflows/skills/session-reflection/scripts/reflection_state.py](../plugins/agentic-workflows/skills/session-reflection/scripts/reflection_state.py) | **Reflection coverage ledger:** Updates compact opaque-ID/source-time coverage data and only skips an unchanged complete trace; no monitor or retrospective runs automatically. |
| `skills/session-reflection/scripts/session_evidence.py` | [plugins/agentic-workflows/skills/session-reflection/scripts/session_evidence.py](../plugins/agentic-workflows/skills/session-reflection/scripts/session_evidence.py) | **Reflection evidence projection:** Filters captured history to bounded secret-safe observations before model exposure; native history controls remain authoritative. |
| `skills/standard-development-workflow/scripts/check_async_feedback.py` | [plugins/agentic-workflows/skills/standard-development-workflow/scripts/check_async_feedback.py](../plugins/agentic-workflows/skills/standard-development-workflow/scripts/check_async_feedback.py) | **Async verification evidence:** Checks supplied observation traces and runtime identities; does not drive or certify the application. |
| `skills/standard-development-workflow/scripts/project_adrs.py` | [plugins/agentic-workflows/skills/standard-development-workflow/scripts/project_adrs.py](../plugins/agentic-workflows/skills/standard-development-workflow/scripts/project_adrs.py) | **Project ADR maintenance:** Checks document structure, links and index freshness; architecture choices remain in the skill/project. |
| `skills/standard-development-workflow/scripts/standard_workflow_record.py` | [plugins/agentic-workflows/skills/standard-development-workflow/scripts/standard_workflow_record.py](../plugins/agentic-workflows/skills/standard-development-workflow/scripts/standard_workflow_record.py) | **Explicit delivery evidence:** Checks optional structured records and evidence identities; it supplies no task controls, execution authority or autonomous delivery loop. |
| `skills/systematic-literature-review-workflow/scripts/systematic_review.py` | [plugins/systematic-literature-review/skills/systematic-literature-review-workflow/scripts/systematic_review.py](../plugins/systematic-literature-review/skills/systematic-literature-review-workflow/scripts/systematic_review.py) | **Systematic-review artifacts:** Checks structured review records/counts and consistency for reproducible evidence; no literature conclusions are delegated to code. |
| `skills/verified-literature-research/scripts/verify_research_bundle.py` | [plugins/agentic-workflows/skills/verified-literature-research/scripts/verify_research_bundle.py](../plugins/agentic-workflows/skills/verified-literature-research/scripts/verify_research_bundle.py) | **Research bundle verification:** Checks local PDF/note/source structure for a supplied bundle without inventing paper evidence. |
| `skills/video-editing/scripts/index_assets.py` | [plugins/video-editing/skills/video-editing/scripts/index_assets.py](../plugins/video-editing/skills/video-editing/scripts/index_assets.py) | **Media asset indexing:** Indexes explicit local media through native probing while preserving source files and editorial decisions. |

## Executable task templates and remaining assets

| Asset class | Disposition | Reason |
| --- | --- | --- |
| [`motion-design/templates/index.html`](../plugins/agentic-workflows/skills/motion-design/templates/index.html) | Keep necessary task template | A 41-line browser scene contains inline GSAP animation code and references the task-local GSAP runtime. The Motion Design skill copies/adapts it as editable video artwork. It does not execute at installation or register a harness hook. This is the one executable template beyond the 40 Python and one MJS helper files above. |
| Markdown, YAML, JSON and TOML | Keep skill/configuration/schema/template data | Names/descriptions, prerequisites, explicit invocation prompts, record schemas and the opt-in Codex asset are interpreted only by their existing native loaders or explicitly invoked task helpers. The sole automatic hook registration is separately listed above. |
| CSV, BibTeX, text, PDF and extensionless license files | Keep task examples, research assets and notices | These are task data or notices, not executable harness integrations. The five extensionless files are licenses; no undisclosed shell script or install executable is present. |

Discovery scanned all distributed file types, not only filename extensions used
for helpers. The central bundle contains exactly one HTML file and no additional
JS/TS/shell/PowerShell/batch/SVG/XML assets with hidden executable entrypoints.
The existing catalog/generator carries the Motion Design template into supported
distributions; it introduces no new adapter or code implementation in this PR.

## Verification and limits

Package/catalog checks reconcile all rows with supported distributions; the title-hook test rejects additional automatic handlers. Existing helper tests retain their relevant data/credential/evidence contracts. Fresh-agent trials separately exercise plain-language selection and delegated worktree/configuration behavior. Removing tests for the retired routing implementation does not count as testing skill adherence.

This exhaustive distribution/activation audit is not a claim that every domain algorithm or remote provider operation was revalidated. Native host capability and skill-adherence claims require observed evidence. Live OpenCode delegation was previously unavailable; do not turn package parity into a runtime pass. Preserve existing private ledgers, credentials, user configuration and unrelated plugin state during update.
