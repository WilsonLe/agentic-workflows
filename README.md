# Agentic Workflows

A private collection of reusable agent workflows for Codex and Claude Code. Copyright (c) 2026 Wilson Le. Distributed under the MIT license. The repository and marketplace remain private; installation requires repository access.

## Install

### Codex

```sh
codex plugin marketplace add anhminhsoft/agentic-workflows
codex plugin add agentic-workflows@agentic-workflows
```

### Claude Code

```sh
claude plugin marketplace add anhminhsoft/agentic-workflows
claude plugin install agentic-workflows@agentic-workflows
```

See [the harness guide](docs/harnesses.md) for the support matrix and package selection. Packages for Claude Code are generated from the canonical catalog.

## Prerequisites

Each `SKILL.md` has a generated **Prerequisites** section listing required and optional tools, accounts, permissions, and setup steps. The same declarations live in [the catalog](catalog/plugins-v2.yaml). Most skills require no setup beyond installation until you choose a provider-specific workflow.

## Packages

- `agentic-workflows` — codex, claude-code; 39 skill(s)
- `agent-orchestration` — codex; 2 skill(s)
- `literature-review` — codex, claude-code; 1 skill(s)
- `guided-writing` — codex, claude-code; 1 skill(s)
- `erpnext-operations` — codex, claude-code; 8 skill(s)
- `image-editing` — codex; 1 skill(s)
- `calorie-tracker` — codex; 1 skill(s)
- `qr-code-generator` — codex, claude-code; 1 skill(s)
- `railway-account` — codex, claude-code; 1 skill(s)
- `excalidraw` — codex, claude-code; 2 skill(s)
- `restaurant-marketing` — codex, claude-code; 1 skill(s)
- `youtube` — codex, claude-code; 3 skill(s)
- `reddit` — codex; 1 skill(s)
- `systematic-literature-review` — codex, claude-code; 1 skill(s)
- `trend-to-product` — codex, claude-code; 5 skill(s)
- `david-jones-customer-service` — codex, claude-code; 1 skill(s)
- `payloadcms` — codex, claude-code; 1 skill(s)

## Updates and migration

This release renames owned packages and skills without compatibility aliases. Remove old installations, add the current private marketplace, and install the package names above. Review existing automation for old skill invocations and update them to names in the catalog. Back up local configuration before migration; the package contains no user credentials or site data.

WordPress-related workflows are retired. Stop invoking their plugin and skill names and uninstall those packages from each harness. This source change does not touch live sites, remote hosting, content, credentials, or existing backups. Preserve any site-specific runbooks outside this repository before updating.

Follow the [operator migration guide](docs/retired-site-workflows.md) for existing installations and deployed site runtimes.

## Development

```sh
uv sync
uv run python scripts/generate_plugin_packages.py --write
uv run python scripts/validate_plugin_packages.py
uv run python -m unittest discover -s tests -q
```

The source of truth is `catalog/plugins-v2.yaml` and the canonical `plugins/` tree. Generated Codex marketplace metadata and Claude packages are committed for review.
