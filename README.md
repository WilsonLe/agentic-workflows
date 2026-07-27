# AMSoft Agentic Workflows for Codex

Private GitHub marketplace for the AMSoft Agentic Workflows Codex plugin.

The plugin bundles reviewed workflows for:

- academic writing and verified literature research
- natural-language humanization
- non-generative food image editing
- approval-gated Cloudflare account operations

## Install

You need access to this private GitHub repository and authenticated GitHub
credentials on the machine running Codex.

Add the marketplace:

```bash
codex plugin marketplace add anhminhsoft/amsoft-agentic-workflow-codex-plugin
```

Install the plugin:

```bash
codex plugin add amsoft-agentic-workflows@amsoft
```

Start a new Codex session after installation so the bundled skills and MCP
tools are available.

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

- `.agents/plugins/marketplace.json` — AMSoft marketplace catalog
- `plugins/amsoft-agentic-workflows/` — distributable Codex plugin

## License

See the licenses bundled with the plugin and its individual workflow
components.
