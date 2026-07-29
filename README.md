# AMSoft Generic Workflow Codex Plugin

Private GitHub marketplace for the reusable AMSoft workflow suite in Codex.

The published Codex package currently uses the technical plugin identifier
`amsoft-agentic-workflows`. It bundles reviewed workflows for:

- standard software delivery through provenance-backed repository profiles, isolated worktrees,
  scoped execution contracts, fail-fast validation, resumable operations, frozen evidence,
  review gates, draft PRs, and optional staging
- academic writing and verified literature research
- natural-language humanization
- non-generative food image editing
- authenticated ERPNext operations across administrative and business roles
- WordPress CLI operations and authenticated site management
- approval-gated DigitalOcean, Cloudflare, and Railway account operations
- protected Excalidraw Plus REST API operations with a focused single-scene workflow
- authenticated-encrypted workflow preference and cloud credential transfer across sessions,
  macOS, and Windows

The marketplace also publishes:

- `erpnext-operations`, with eight focused business and administrative skills;
- `image-editing`, with non-generative food-image critique, mask preview,
  layering, composition, color correction, and verification;
- `railway-account`, with account-token-only Railway CLI operations.
- `excalidraw`, with protected personal-key onboarding, broad API reads, and
  exact-scene create/update/backup operations. It uses REST, not MCP.

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

Or install only Image Editing:

```bash
codex plugin add image-editing@amsoft --json
```

Or install only Railway Account:

```bash
codex plugin add railway-account@amsoft --json
```

Or install only Excalidraw:

```bash
codex plugin add excalidraw@amsoft --json
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
If you installed the standalone ERPNext package, also confirm that
`erpnext-operations@amsoft` is installed and enabled.
If you installed Image Editing, confirm that `image-editing@amsoft` is installed
and enabled.
If you installed Railway Account, confirm that `railway-account@amsoft` is
installed and enabled.
If you installed Excalidraw, confirm that `excalidraw@amsoft` is installed and
enabled.

## Updating

Refresh the private marketplace and reinstall the current package:

```bash
codex plugin marketplace upgrade amsoft --json
codex plugin add amsoft-agentic-workflows@amsoft --json
codex plugin add erpnext-operations@amsoft --json
codex plugin add image-editing@amsoft --json
codex plugin add railway-account@amsoft --json
codex plugin add excalidraw@amsoft --json
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

## Repository layout

- `.agents/plugins/marketplace.json` — private marketplace catalog
- `plugins/amsoft-agentic-workflows/` — complete AMSoft workflow suite
- `plugins/erpnext-operations/` — standalone ERPNext Operations plugin
- `plugins/railway-account/` — standalone Railway Account plugin
- `plugins/excalidraw/` — standalone Excalidraw REST API plugin

## License

See the licenses bundled with the plugin and its individual workflow
components.
