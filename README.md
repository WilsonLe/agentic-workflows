# Agentic Workflows

A private collection of reusable agent workflows for Codex and Claude Code. Copyright (c) 2026 Wilson Le. Distributed under the MIT license. The repository and marketplace remain private; installation requires repository access.

New to the suite? Start with the [onboarding guide](plugins/agentic-workflows/skills/agentic-workflows/references/onboarding.md) for choosing a skill, delegating in each harness or Codex voice mode, and choosing a model.

The engineering skills cover request intake, symptom-based diagnosis, two-axis change
review, design exploration, agent-instruction design, and manual setup guides. They
adapt ideas from [Matt Pocock's agent skills](https://github.com/mattpocock/skills)
to this suite's existing Standard Development Workflow and approval rules.

## Install

Make sure your Git credentials can read the private repository before adding its marketplace. Install the central package first; add a focused package from the list below when you need it.

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

For a focused package, replace `<package>` with a supported name from the list below, then use `codex plugin add <package>@agentic-workflows` or `claude plugin install <package>@agentic-workflows`.

## Update

Refresh the marketplace, then restart the host and invoke a skill in a new task or session. In Claude Code, update each installed package you use after refreshing the marketplace.
After reviewing and trusting the central Codex package's updated hooks, test
repository-change routing and background session-title updates in a fresh Codex
task rooted in a Git repository. The routing hook adds workflow guidance; it
does not create pull requests itself.

### Codex

```sh
codex plugin marketplace upgrade agentic-workflows
codex plugin list --marketplace agentic-workflows
```

### Claude Code

```sh
claude plugin marketplace update agentic-workflows
claude plugin update agentic-workflows@agentic-workflows
claude plugin list
```

For first-use verification and updates to focused packages, follow the [onboarding guide](plugins/agentic-workflows/skills/agentic-workflows/references/onboarding.md).

## Task authority and secrets

A requested outcome carries through necessary in-scope provider clicks and
credential setup without repeated confirmation. Supported concealed Copy →
Keychain → CLI transfer keeps secret values out of chat, tool output, process
arguments, logs, and Git. Follow the
[task authority and concealed secrets contract](plugins/agentic-workflows/skills/agentic-workflows/references/task-authority-and-secrets.md)
for exact targets, existing authority, safe transfer routes, and flow verification.

## Prerequisites

Each `SKILL.md` has a generated **Prerequisites** section listing required and optional tools, accounts, permissions, and setup steps. The same declarations live in [the catalog](catalog/plugins-v2.yaml). Most skills require no setup beyond installation until you choose a provider-specific workflow.

## Packages

- `agentic-workflows` — codex, claude-code; 45 skill(s)
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

`uv`, ImageMagick 7, and the Claude Code CLI are required for the complete local CI run
(validated with Claude Code 2.1.143).
Run it before opening or updating a pull request:

```sh
uv run python scripts/run_local_ci.py
```

This runs repository validation (package checks, all unit tests, and Ruff),
checks generated Claude packages, validates the marketplace and each package
with Claude Code, and smoke installs a shared package. GitHub Actions validation
is available by manual dispatch only.

```sh
uv sync
uv run python scripts/generate_plugin_packages.py --write
uv run python scripts/validate_plugin_packages.py
uv run python -m unittest discover -s tests -q
```

The source of truth is `catalog/plugins-v2.yaml` and the canonical `plugins/` tree. Generated Codex marketplace metadata and Claude packages are committed for review.
The [delivery continuity guide](plugins/agentic-workflows/skills/standard-development-workflow/references/efficient-delivery-and-external-work.md)
documents the task contract, measured verification manifest, and authenticated-source/provider
ledger used by the Standard Development Workflow.

### Reflection follow-ups

UI tasks reuse approved, project-scoped copy and component conventions. Deployment-triggering
merges must verify changed target prerequisites or safe feature inactivity before activation.
The title hook delegates generation to an ephemeral fast model (`gpt-5.6-luna`, reasoning `low`)
and validates a maximum of 10 words / 100 characters. It does not change the foreground model.
Exact-session title controls remain host-dependent; unavailable controls or generation leave
titles unchanged. See the [title policy](plugins/agentic-workflows/skills/agentic-workflows/references/session-title-policy.md)
for configuration, opt-out, deadlines and manual-title protections.
