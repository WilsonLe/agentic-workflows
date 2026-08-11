# AMSoft Generic Workflow Codex Plugin

Private GitHub marketplace for the reusable AMSoft workflow suite in Codex.

## Development

The repository uses Python 3.12 and `uv`. From a fresh checkout:

```bash
uv sync --locked
uv run python scripts/validate_repository.py
```

The validation entry point checks package structure and generated contracts, runs the complete
test suite, and applies Ruff to every Python surface.

The published Codex package currently uses the technical plugin identifier
`amsoft-agentic-workflows`. It bundles reviewed workflows for:

- standard software delivery through provenance-backed repository profiles, isolated worktrees,
  scoped execution contracts, fail-fast validation, resumable operations, frozen evidence,
  review gates, draft PRs, and optional staging
- academic writing, verified literature research, transparent non-systematic literature reviews,
  and auditable systematic evidence synthesis
- natural-language humanization
- food-image curation, preservation-first OpenAI edit prompting, and
  rights-aware real-object reference integration
- exact-payload QR code generation with deterministic themed SVG/PNG output,
  decoder verification, and safe image-generation-assisted backgrounds
- uncertainty-aware meal-image calorie and macro estimation with bounded public nutrition
  evidence and approval-gated private Google Drive/Sheets logging
- truthful, margin-aware, approval-gated restaurant marketing management
- instruction-only David Jones customer-service till guidance for Rewards lookup, scanning,
  authorized detagging, EFTPOS with no cash, receipt printing, and bagging
- authenticated ERPNext operations across administrative and business roles
- separate WordPress Content and WordPress DevOps operations: a lightweight, non-Git content loop
  from installed theme to blocks, patterns, layouts, copy/media, local browser verification, and
  rollback-backed live apply; plus separate provider/SSH/runtime/infrastructure operations
- WordPress project management, content-as-code synchronization contracts, checksum-guarded writes,
  guarded two-way WordPress Git synchronization with canonical managed objects, atomic
  compare-and-swap, migration waves, manifest media, extension adapters, and reviewed automation,
  evidence-led WordPress SEO and growth audits using free official APIs and Chrome research tools,
  and opt-in Stream
  audit logging
- approval-gated DigitalOcean, Cloudflare, and Railway account operations
- protected Excalidraw Plus REST API operations with a focused single-scene workflow
- protected, rights-aware YouTube inspection, media retrieval, and bounded archive sync through
  yt-dlp and browser-exported YouTube-only cookies
- bounded, read-only Reddit browsing through the user's connected Chrome session and the host's
  CDP-backed browser controls
- authenticated-encrypted workflow preference and cloud credential transfer across sessions,
  macOS, and Windows

The marketplace also publishes:

- `agent-orchestration`, with explicit same-project control-plane activation,
  Goal Mode clarity interviews, active open-issue triage, dedicated Codex
  sessions with new worktrees from refreshed `main`, asynchronous independent
  exact-head review sessions, bounded coordination, terminal archive, and safe
  cleanup;
- `literature-review`, with narrative, integrative, critical, conceptual/theoretical, and
  state-of-the-art method selection, transparent discovery and selection records, concept-centric
  synthesis, counterevidence checks, and dependency-free project validation;
- `erpnext-operations`, with eight focused business and administrative skills;
- `image-editing`, with food-image critique, preservation-first OpenAI edit
  prompts, semantic object mapping, provenance-verified online references,
  tool-directed integration, and visual drift review;
- `qr-code-generator`, with exact-payload styled QR rendering, real decoder
  verification, and image-generation-assisted backgrounds outside the QR safe area;
- `calorie-tracker`, with evidence-separated meal-image analysis, portion ranges, secret-safe
  USDA and keyless exact-barcode Open Food Facts reads, remembered private Google destinations,
  typed Sheet rows, and idempotent cross-service recovery;
- `railway-account`, with account-token-only Railway CLI operations;
- `excalidraw`, with protected personal-key onboarding, broad API reads, and
  exact-scene create/update/backup operations; it uses REST, not MCP;
- `restaurant-marketing`, with new-dish, offer, seasonal, local discovery, reputation, retention,
  event, and launch campaign management.
- `wordpress-seo`, with technical and on-page audits, first-party baselines, competitor qualification,
  per-competitor content-gap research, growth roadmaps, original briefs, safe WordPress editing, and
  outcome measurement.
- `payloadcms`, with Payload configuration, collections, globals, custom admin components,
  access-control design, Postgres migration generation and reversible validation, and three-layer
  unit, integration, and Playwright E2E testing.
- `wordpress-content`, an independent standard WordPress content-management workflow: start with
  the installed theme, then registered blocks, patterns, page layouts, copy and media; use temporary
  files, verify locally in a browser, apply live with a rollback ready, and roll back on failure.
  It does not invoke Standard Development Workflow or perform Git operations.
- `wordpress-devops`, with Railway or DigitalOcean target resolution, authorized SSH/WP-CLI,
  hosting, plugin/theme and filesystem operations, deployment, rollback, and committed
  infrastructure source changes; it never edits user-facing content.
- `wordpress-git-sync`, with a deterministic secret-safe CLI, optional WordPress CAS runtime,
  public-content automation contract, existing-project adoption techniques, evidence templates,
  and rollback-first operator runbooks.
- `david-jones-customer-service`, with the working Till Sale — EFTPOS (No Cash) procedure for
  Rewards lookup, item scanning, authorized detagging, payment, receipt printing, and bagging.
- `systematic-literature-review`, with cross-disciplinary method selection, versioned protocols,
  reproducible search/export lineage, reversible identity and deduplication, real human review
  gates, appraisal/synthesis/certainty controls, ledger-derived reporting, and a structural CLI.
- `youtube`, with media-free inspection, authorized video/audio/section retrieval, protected
  browser-exported cookie authentication, and bounded playlist/channel archive sync.
- `reddit`, with bounded Reddit page, subreddit, search, post, and visible-comment reads through
  Chrome/CDP; it performs no Reddit writes, credential extraction, or bulk scraping.

## Installation

### 1. Prerequisites

You need:

- access to this private GitHub repository
- Codex CLI installed
- GitHub credentials authorized to read the `anhminhsoft` organization

Authenticate GitHub CLI when needed and verify that the selected Git transport can read the
private repository without placing credentials in a URL:

```bash
gh auth login -h github.com
git ls-remote https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin.git HEAD
```

### 2. Add the private marketplace

```bash
codex plugin marketplace add \
  anhminhsoft/amsoft-agentic-workflow-codex-plugin \
  --ref main \
  --json
```

An already configured SSH transport may be used instead:

```bash
codex plugin marketplace add \
  git@github.com:anhminhsoft/amsoft-agentic-workflow-codex-plugin.git \
  --ref main \
  --json
```

Register the marketplace once. Later updates use `marketplace upgrade`.

### 3. Install the plugin

Install the complete AMSoft suite:

```bash
codex plugin add amsoft-agentic-workflows@amsoft --json
```

Or install only ERPNext Operations:

```bash
codex plugin add erpnext-operations@amsoft --json
```

Or install only Literature Review:

```bash
codex plugin add literature-review@amsoft --json
```

Or install only Image Editing:

```bash
codex plugin add image-editing@amsoft --json
```

Or install only QR Code Generator:

```bash
codex plugin add qr-code-generator@amsoft --json
```

Or install only Railway Account:

```bash
codex plugin add railway-account@amsoft --json
```

Or install only Excalidraw:

```bash
codex plugin add excalidraw@amsoft --json
```

Or install only Calorie Tracker:

```bash
codex plugin add calorie-tracker@amsoft --json
```

Or install only WordPress Git Sync:

```bash
codex plugin add wordpress-git-sync@amsoft --json
```

Or install only Restaurant Marketing:

```bash
codex plugin add restaurant-marketing@amsoft --json
```

Or install only WordPress SEO:

```bash
codex plugin add wordpress-seo@amsoft --json
```

Or install only Payload CMS:

```bash
codex plugin add payloadcms@amsoft --json
```

Or install only WordPress Content:

```bash
codex plugin add wordpress-content@amsoft --json
```

Or install only WordPress DevOps:

```bash
codex plugin add wordpress-devops@amsoft --json
```

Or install only Systematic Literature Review:

```bash
codex plugin add systematic-literature-review@amsoft --json
```

Or install only Trend to Product:

```bash
codex plugin add trend-to-product@amsoft --json
```

Or install only Agent Orchestration:

```bash
codex plugin add agent-orchestration@amsoft --json
```

Or install only YouTube:

```bash
codex plugin add youtube@amsoft --json
```

Or install only Reddit:

```bash
codex plugin add reddit@amsoft --json
```

Or install only David Jones Customer Service:

```bash
codex plugin add david-jones-customer-service@amsoft --json
```

### 4. Start a new Codex session

Bundled skills are loaded at session start. Open a new Codex
session after installation, then ask:

```text
Onboard me to AMSoft Agentic Workflows and check only the relevant prerequisites.
```

### 5. Verify the installation

```bash
codex plugin list --json
```

Confirm that `amsoft-agentic-workflows@amsoft` is installed and enabled.
If you installed Agent Orchestration, confirm that
`agent-orchestration@amsoft` is installed and enabled.
If you installed Literature Review, confirm that `literature-review@amsoft` is installed and
enabled.
If you installed the standalone ERPNext package, also confirm that
`erpnext-operations@amsoft` is installed and enabled.
If you installed Image Editing, confirm that `image-editing@amsoft` is installed
and enabled.
If you installed QR Code Generator, confirm that `qr-code-generator@amsoft` is installed
and enabled.
If you installed Calorie Tracker, confirm that `calorie-tracker@amsoft` is installed and enabled.
If you installed Railway Account, confirm that `railway-account@amsoft` is
installed and enabled.
If you installed Excalidraw, confirm that `excalidraw@amsoft` is installed and
enabled.
If you installed Restaurant Marketing, confirm that
`restaurant-marketing@amsoft` is installed and enabled.
If you installed WordPress SEO, confirm that `wordpress-seo@amsoft` is installed and enabled.
If you installed Payload CMS, confirm that `payloadcms@amsoft` is installed and enabled.
If you installed Systematic Literature Review, confirm that
`systematic-literature-review@amsoft` is installed and enabled.
If you installed Trend to Product, confirm that
`trend-to-product@amsoft` is installed and enabled.
If you installed YouTube, confirm that `youtube@amsoft` is installed and enabled.
If you installed Reddit, confirm that `reddit@amsoft` is installed and enabled.
If you installed David Jones Customer Service, confirm that
`david-jones-customer-service@amsoft` is installed and enabled.

## Updating

Refresh the private marketplace and reinstall the current package:

```bash
codex plugin marketplace upgrade amsoft --json
codex plugin add amsoft-agentic-workflows@amsoft --json
codex plugin add agent-orchestration@amsoft --json
codex plugin add literature-review@amsoft --json
codex plugin add erpnext-operations@amsoft --json
codex plugin add image-editing@amsoft --json
codex plugin add qr-code-generator@amsoft --json
codex plugin add calorie-tracker@amsoft --json
codex plugin add railway-account@amsoft --json
codex plugin add excalidraw@amsoft --json
codex plugin add restaurant-marketing@amsoft --json
codex plugin add wordpress-seo@amsoft --json
codex plugin add payloadcms@amsoft --json
codex plugin add systematic-literature-review@amsoft --json
codex plugin add trend-to-product@amsoft --json
codex plugin add youtube@amsoft --json
codex plugin add reddit@amsoft --json
codex plugin add david-jones-customer-service@amsoft --json
codex plugin list --json
```

Confirm the declared and installed versions agree, then start a new Codex session after updating.
To roll back, select a known prior Git ref for the marketplace, refresh it, and reinstall the
version declared by that revision. Never delete project repositories or retained workflow evidence
as part of plugin rollback.

## ERPNext authentication

ERPNext onboarding accepts either:

- JSON containing `site_url`, `api_key`, and `api_secret`; or
- a one-row Frappe CSV containing `api_key,api_secret`, with the site URL
  supplied separately.

Never paste credentials into chat or commit them to this repository. Onboarding
copies normalized credentials to `~/.config/amsoft/erpnext/credentials.json`,
sets the directory to `0700` and the file to `0400`, then verifies the
authenticated identity using a read-only API call.

## Cloudflare authentication

Cloudflare onboarding accepts a scoped user/account API-token file, rejects
Global API Keys, installs a protected record under `~/.config/amsoft/cloudflare`,
and verifies it read-only before optionally archiving the exact source.

## Railway authentication

Railway onboarding accepts only an account token created in Account Settings
with **No workspace** selected. This is Railway's broadest token class and is
exposed to the CLI only as `RAILWAY_API_TOKEN`.

Never paste the token into chat or commit it. Onboarding accepts its local path
and installs a normalized protected copy at
`~/.config/amsoft/railway/credentials.json`, with directory mode `0700` and
file mode `0400`. Project, workspace, OAuth, and interactive-login credentials
are outside this plugin's contract.

## DigitalOcean authentication

DigitalOcean onboarding accepts a personal access-token file. A supplied
`digitalocean.config.yml` is used only to prove that its embedded token matches;
its command defaults are never imported. The protected wrapper injects the
token only into a `doctl` child process.

## Excalidraw authentication

Excalidraw onboarding accepts only a user-confirmed personal MCP/API key from a
local file. It installs a normalized owner-read-only record at
`~/.config/amsoft/excalidraw/credentials.json`, verifies
`GET /collections?limit=1&offset=0`, and only then archives the original
source. The plugin uses the Excalidraw Plus REST API exclusively; it does not
install or call MCP.

## Encrypted configuration transfer

Ask the central plugin to export configuration to receive one `.amsoftx` file
containing allowlisted preferences and configured Railway, Cloudflare, and
DigitalOcean credentials under authenticated encryption. Same-machine mode
uses the OS user's protected key. Portable macOS/Windows mode uses a passphrase
entered through a masked local prompt. Attach the file in another compatible
central-plugin session and ask to import; all credentials verify read-only and
commit transactionally or the prior local configuration is restored.

## YouTube authentication

Public YouTube inspection and retrieval uses no account credential. Account-gated operations accept
only a browser-exported, YouTube-domain-only Netscape cookie file. The YouTube credential helper
validates the export locally and installs a protected copy at
`~/.config/amsoft/youtube/cookies.txt`, with directory mode `0700` and file mode `0400` on POSIX
systems and an owner-restricted ACL on Windows.

Cookie values never belong in chat, logs, evidence, repository files, or encrypted configuration
transfer. yt-dlp receives only the protected file path through `--cookies`. Direct
`--cookies-from-browser` use, broad multi-site jars, OAuth, passwords, PO-token values, proxy or
geo-bypass, and DRM circumvention are outside the plugin contract.

## Reddit browser access

Reddit browsing uses the host `control-chrome` skill and a connected Chrome extension with
CDP-backed browser control. The workflow reads rendered Reddit pages only; it does not bundle a
Reddit API client, scraper, proxy, credential store, or background crawler. Sign in directly in
Chrome when Reddit requires it. Never paste passwords, OTPs, cookies, tokens, or private messages
into chat.

## Repository layout

- `.agents/plugins/marketplace.json` — private marketplace catalog
- `plugins/amsoft-agentic-workflows/` — complete AMSoft workflow suite
- `plugins/agent-orchestration/` — standalone Goal Mode issue-triage, session-worktree, and asynchronous independent-review control-plane plugin
- `plugins/literature-review/` — standalone transparent non-systematic review plugin
- `plugins/erpnext-operations/` — standalone ERPNext Operations plugin
- `plugins/image-editing/` — standalone Image Editing plugin
- `plugins/qr-code-generator/` — standalone exact-payload QR generation plugin
- `plugins/calorie-tracker/` — standalone image-to-macros and Google logging plugin
- `plugins/railway-account/` — standalone Railway Account plugin
- `plugins/excalidraw/` — standalone Excalidraw REST API plugin
- `plugins/restaurant-marketing/` — standalone Restaurant Marketing plugin
- `plugins/wordpress-seo/` — standalone WordPress SEO and growth audit, competitor-gap research, and AMSoft proposal-deck plugin
- `plugins/payloadcms/` — standalone Payload CMS configuration, plugin, Postgres migration, access-control, and testing workflow
- `plugins/wordpress-content/` — standalone, non-Git WordPress content workflow with local browser verification and rollback-backed live apply
- `plugins/wordpress-devops/` — standalone WordPress DevOps plugin for hosting, SSH, runtime, filesystem, and releases
- `plugins/wordpress-git-sync/` — standalone guarded Git/WordPress synchronization, migration, runtime, and runbook plugin
- `plugins/systematic-literature-review/` — standalone auditable Systematic Literature Review plugin
- `plugins/trend-to-product/` — standalone demographic trend-to-product research and design plugin
- `plugins/youtube/` — standalone YouTube inspection, media, and archive plugin
- `plugins/reddit/` — standalone bounded Reddit browsing plugin for Chrome/CDP
- `plugins/david-jones-customer-service/` — standalone David Jones customer-service till plugin

## License

Every top-level plugin package in this repository is distributed under the
[AMSoft Proprietary License](LICENSE) and declares
`LicenseRef-AMSoft-Proprietary`. Use is restricted to AMSoft and authorized
AMSoft personnel for AMSoft business purposes.

Bundled third-party components retain their own license files, notices, and
attribution. The AMSoft Proprietary License does not replace or restrict those
third-party terms.
