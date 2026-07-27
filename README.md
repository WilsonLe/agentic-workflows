# AMSoft Generic Workflow Codex Plugin

Private GitHub marketplace for the reusable AMSoft workflow suite in Codex.

The published Codex package currently uses the technical plugin identifier
`amsoft-agentic-workflows`. It bundles reviewed workflows for:

- standard software delivery through isolated worktrees, review gates, draft PRs, and optional staging
- academic writing and verified literature research
- natural-language humanization
- non-generative food image editing
- authenticated ERPNext operations across administrative and business roles
- WordPress CLI operations and authenticated site management
- approval-gated DigitalOcean, Cloudflare, and Railway account operations

The marketplace also publishes:

- `erpnext-operations`, with eight focused business and administrative skills;
- `railway-account`, with account-token-only Railway CLI operations.

## Installation

### 1. Prerequisites

You need:

- access to this private GitHub repository
- Codex CLI installed
- GitHub credentials authorized to read the `anhminhsoft` organization

Authenticate GitHub CLI when needed:

```bash
gh auth login -h github.com
```

### 2. Add the private marketplace

```bash
codex plugin marketplace add anhminhsoft/amsoft-agentic-workflow-codex-plugin
```

### 3. Install the plugin

Install the complete AMSoft suite:

```bash
codex plugin add amsoft-agentic-workflows@amsoft
```

Or install only ERPNext Operations:

```bash
codex plugin add erpnext-operations@amsoft
```

Or install only Railway Account:

```bash
codex plugin add railway-account@amsoft
```

### 4. Start a new Codex session

Bundled skills are loaded at session start. Open a new Codex
session after installation, then ask:

```text
Onboard me to AMSoft Agentic Workflows and check only the relevant prerequisites.
```

### 5. Verify the installation

```bash
codex plugin list
```

Confirm that `amsoft-agentic-workflows@amsoft` is installed and enabled.
If you installed the standalone ERPNext package, also confirm that
`erpnext-operations@amsoft` is installed and enabled.
If you installed Railway Account, confirm that `railway-account@amsoft` is
installed and enabled.

## Updating

Refresh the private marketplace and reinstall the current package:

```bash
codex plugin marketplace upgrade amsoft
codex plugin add amsoft-agentic-workflows@amsoft
codex plugin add erpnext-operations@amsoft
codex plugin add railway-account@amsoft
```

Start a new Codex session after updating.

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

Cloudflare operations require:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Use a least-privilege account API token. Never store either value in this
repository. Cloudflare operations are CLI-first and use `curl` or Wrangler;
the current suite does not bundle a Cloudflare MCP server.

## Railway authentication

Railway onboarding accepts only an account token created in Account Settings
with **No workspace** selected. This is Railway's broadest token class and is
exposed to the CLI only as `RAILWAY_API_TOKEN`.

Never paste the token into chat or commit it. Onboarding accepts its local path
and installs a normalized protected copy at
`~/.config/amsoft/railway/credentials.json`, with directory mode `0700` and
file mode `0400`. Project, workspace, OAuth, and interactive-login credentials
are outside this plugin's contract.

## Repository layout

- `.agents/plugins/marketplace.json` — private marketplace catalog
- `plugins/amsoft-agentic-workflows/` — complete AMSoft workflow suite
- `plugins/erpnext-operations/` — standalone ERPNext Operations plugin
- `plugins/railway-account/` — standalone Railway Account plugin

## License

See the licenses bundled with the plugin and its individual workflow
components.
