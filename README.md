# MSoft Generic Workflow Codex Plugin

Private GitHub marketplace for the reusable MSoft workflow suite in Codex.

The published Codex package currently uses the technical plugin identifier
`amsoft-agentic-workflows`. It bundles reviewed workflows for:

- academic writing and verified literature research
- natural-language humanization
- non-generative food image editing
- approval-gated Cloudflare account operations

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

```bash
codex plugin add amsoft-agentic-workflows@amsoft
```

### 4. Start a new Codex session

Bundled skills and MCP tools are loaded at session start. Open a new Codex
session after installation, then ask:

```text
Onboard me to AMSoft Agentic Workflows and check only the relevant prerequisites.
```

### 5. Verify the installation

```bash
codex plugin list
```

Confirm that `amsoft-agentic-workflows@amsoft` is installed and enabled.

## Updating

Refresh the private marketplace and reinstall the current package:

```bash
codex plugin marketplace upgrade amsoft
codex plugin add amsoft-agentic-workflows@amsoft
```

Start a new Codex session after updating.

## Cloudflare authentication

Cloudflare operations require:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Use a least-privilege account API token. Never store either value in this
repository. On macOS, the plugin includes a Keychain setup helper:

```bash
plugins/amsoft-agentic-workflows/scripts/configure-cloudflare-macos-keychain.sh
```

## Repository layout

- `.agents/plugins/marketplace.json` — private marketplace catalog
- `plugins/amsoft-agentic-workflows/` — distributable Codex plugin

## License

See the licenses bundled with the plugin and its individual workflow
components.
