# Global Vercel onboarding

Fetch and follow the current [Vercel agent setup playbook](https://vercel.com/get-started.md).
Use its current commands rather than treating this reference as a frozen manual.
Record blocked steps and continue independent setup. Run machine setup once and
guidance/MCP setup once per agent; link projects only for later project work.

## CLI and identity

Check `vercel --version`. If missing or reporting an update, install with
`npm install --global vercel@latest`, then check the executable actually resolved
by `command -v vercel` and its version. A different npm prefix can update a
binary that is shadowed on PATH; fix the intended user installation and verify
bare `vercel` again. Inspect Node.js availability when npm installation needs it.

Run `vercel whoami`. Reuse a valid existing login. If no account is authenticated,
use `vercel login` for an existing account, or `vercel signup` when creating an
account is requested. Pause while the user completes authentication, then verify
`whoami` and read-only team inventory. Do not read or print the CLI's auth file.
Do not request token values in chat or put them in process arguments. For a
requested token-based automation, use an inspected concealed transfer to the
approved secret store and a narrowly scoped child `VERCEL_TOKEN` environment.

## Official guidance

Inspect installed plugins before changing them. Reuse an enabled official Vercel
plugin, including the Codex marketplace package named `vercel` that packages
`vercel/vercel-plugin`. Verify its source, version, installed/enabled state,
and discoverable skills or status command. Do not install another copy under
the upstream `vercel-plugin` name merely because its identity differs.

Otherwise follow the preferred route:

```sh
node --version
npx plugins add vercel/vercel-plugin
```

Choose the current agent and user/global scope. Inspect `npx plugins --help`
when selecting a noninteractive target. For errors other than unsupported
plugins or unavailable Node.js, consult the
[plugin documentation](https://vercel.com/docs/agent-resources/vercel-plugin)
once before using the playbook's standalone-skills fallback. Install the
official guidance plugin or the standalone pack, never both. This suite's
account skill is complementary account guidance, not that standalone pack.
Reload only if the host does not discover newly installed guidance.

## Shared MCP

Inspect existing entries and merge only the Vercel configuration; preserve
unrelated servers, settings, and approval controls. Verify the endpoint is
exactly `https://mcp.vercel.com`. Never use project-scoped setup by default.
If an existing shared connection works, reuse it. A connected Vercel app is
a distinct route: record it as app-managed, without claiming a local MCP
configuration exists. Avoid installing a redundant connection in that host.

For Codex CLI, inspect `codex mcp list`, then, if missing:

```sh
codex mcp add vercel --url https://mcp.vercel.com
```

This configures the user-wide `~/.codex/config.toml`. If configured but
unauthenticated, use `codex mcp login vercel`. Codex is not a supported
`vercel mcp --clients` target. For Claude Code inspect existing servers and use:

```sh
claude mcp add --transport http vercel --scope user https://mcp.vercel.com
```

Use Claude's `/mcp` authentication action. Follow the live playbook's specific
route for another client. Use only one route per client. Pause while the user
completes OAuth; never extract browser tokens or copy OAuth secrets into notes.

After authentication, call `search_vercel_documentation` and authenticated
`list_teams` through that connection. Refresh tools if missing, then resume a
session or reload only if refreshing fails. An OAuth success and saved URL
alone do not prove that these tools are available in the active session.
Keep human confirmation enabled for every MCP mutation.

## Completion readback

Report only verified state: CLI version and username; official guidance plugin
or fallback and scope; shared MCP endpoint, route, config location and auth
state; documentation search and `list_teams` result; and any reload needed.
Reconcile different CLI/MCP accounts before claiming they operate one account.
Report pending authentication or missing active-session tools explicitly.
