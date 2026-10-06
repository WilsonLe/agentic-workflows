# Vercel Account

Agentic Workflows setup and account management for Vercel, using the official
Vercel CLI and the shared MCP endpoint at `https://mcp.vercel.com`.

Install the suite package:

```sh
codex plugin add vercel-account@agentic-workflows
# Claude Code
claude plugin install vercel-account@agentic-workflows
```

Then ask:

> Use $vercel-account-operations to set up Vercel globally and verify my CLI and MCP accounts without linking a project.

The skill follows the live [Vercel setup playbook](https://vercel.com/get-started.md):
verify or install the CLI, reuse or install the official Vercel guidance plugin,
and connect the shared MCP endpoint. This package adds account operations; it
does not vendor the official plugin, install a duplicate standalone skill pack,
or bundle credentials. Installing this package alone does not authenticate Vercel.

Account management covers identity, team and project inventory, membership and
role changes, access, domains, integrations, and billing or spend settings using
currently supported CLI, MCP, REST API, or authorized dashboard operations.
Each operation resolves the account and exact team first. CLI and connected-app
credentials can belong to different accounts; never assume their inventories match.

Global onboarding does not create or link a project, deploy, change billing,
or modify team membership. MCP writes retain human confirmation as required by
Vercel's playbook. See the [skill](skills/vercel-account-operations/SKILL.md) for
task authority, concealed credentials, verification, and recovery.
