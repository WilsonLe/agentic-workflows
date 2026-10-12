# DevTools setup and testing

The plugin supplies skills and an offline helper. It does not register an MCP server,
install Google's skills, change global agent settings, or enable browser debugging on install.
Use an already configured compatible server when available. For setup, verify the current
Node.js LTS requirement, Chrome version, server flags, and host configuration format from
[the upstream README](https://github.com/ChromeDevTools/chrome-devtools-mcp),
[configuration](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/configuration.md),
and [tool reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md).

## Task-owned browser

Use a Chrome instance launched by the server with an isolated profile for ordinary extension
tests. It avoids changing an everyday profile and supports the pipe connection used by
extension tools. A generic MCP client example is:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--categoryExtensions", "--isolated", "--no-usage-statistics", "--no-performance-crux"]
    }
  }
}
```

Apply this only to the user's requested host/project configuration, preserving other servers.
For an authorized user-level Codex setup, use `codex mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --categoryExtensions --isolated --no-usage-statistics --no-performance-crux`.
This writes Codex's user configuration; a project-only request should use the host's
supported project configuration instead of that user-level command.
Claude Code supports `claude mcp add chrome-devtools --scope project -- npx -y chrome-devtools-mcp@latest --categoryExtensions --isolated --no-usage-statistics --no-performance-crux`.
Check current CLI help and the host's scope before writing configuration. `@latest` resolves a
mutable package; record the actual version for reproducibility. The privacy flags disable MCP
usage metrics and CrUX lookups, not all browser/network activity. Keep local fixtures private.

Prefer the host's in-app browser for ordinary web inspection. Chrome extension installation
and worker inspection require a Chrome-capable channel; a rendered web page in an in-app
browser cannot establish extension runtime behavior.

## Existing profile when the task requires it

Signed-in flows or built-in AI may require a configured Chrome profile. Identify the intended
profile and access scope first; connect only within user authorization. The guide proposes
`--autoConnect` with remote debugging enabled at `chrome://inspect/#remote-debugging` and a
browser permission prompt. Keep that native approval step with the user.

Check the installed Chrome/server combination before combining `--autoConnect` with
`--categoryExtensions`: upstream documents version-dependent restrictions on extension
tools with non-pipe connections. Do not assume both flags establish working extension tools.
Read back the tool inventory and browser identity. If installation/reload is unavailable,
use an authorized manual unpacked load or return to the isolated profile, and state which
flows remain unverified. Never enable global debugging or select another profile silently.

## Exercise the candidate

1. Build first. Discover the running server's tool schemas; tool prefixes/arguments may vary.
   Use `install_extension` with the absolute unpacked directory, then `list_extensions` to
   record the actual ID, version, enabled state, Chrome version, and profile mode.
2. Use `trigger_extension_action` and inspect each affected popup, side panel, options page,
   content-script page, and worker target. Verify user-visible outcomes and saved data, not
   only screenshots or an enabled extension flag. Collect relevant console/network failures
   without recording private page content or credentials.
3. Test permission denial/revocation, unsupported pages, repeated actions, missing/offline
   dependencies, and worker termination/restart where relevant. Close worker DevTools when
   testing suspension because inspection can affect lifetime. Test keyboard focus and labels.
4. After source edits, rebuild and `reload_extension` using the recorded task-owned ID.
   Refresh content-script test pages and re-open extension surfaces; stale injected code or
   an old popup is not evidence for the new build. Bind final results to the candidate commit.
5. Clean up only the extension, fixtures, and browser instance created for this task. Never
   uninstall unrelated extensions or terminate the user's existing browser session.

MCP server connection, tool availability, unpacked loading, successful flows, and store
acceptance are distinct evidence. Missing runtime access is a limitation, never a pass.
