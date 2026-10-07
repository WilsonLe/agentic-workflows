# Harness support

The catalog declares support per package and skill. Both harnesses use the same canonical instructions and prerequisites. Codex uses `.agents/plugins/marketplace.json` and canonical `plugins/` packages. Claude Code uses `.claude-plugin/marketplace.json` and generated packages under `generated/claude/plugins/`.

The focused [UI Design](../plugins/ui-design/README.md) package shares
one instruction-only design skill across both harnesses. It has no additional
runtime dependencies; rendered inspection and implementation use the tools
available in the current host and project.

The focused [Chrome Extensions](../plugins/chrome-extensions/README.md) package
provides two shared skills and a dependency-free Python manifest audit. Chrome
DevTools MCP is optional and configured separately in the selected host; the
package does not register a server or attach to a browser profile on installation.
Runtime verification requires a compatible Chrome/server connection with extension
tools. The in-app browser can inspect websites but cannot prove extension execution.

A skill appears in the Claude package only when its catalog entry includes `claude-code`. Skills that require Codex task controls or Codex-specific browser/image tools remain Codex-only. No host runtime adapter is included. Provider tools, API credentials, and CLIs are configured when the selected skill requires them.

The central Codex package adds a `UserPromptSubmit` hook that provides conditional
Standard Development Workflow routing guidance when the task's working directory
is inside a Git repository. It runs only where Codex supports and the user trusts
plugin hooks. It is a routing reminder, not a PR creation or completion gate;
`$sdlc-loop` autopilot still requires direct invocation. Claude Code receives
the shared router text, but neither this hook nor the Codex-only Standard
Development Workflow skill runs there.

After installing or updating the central Codex package, review and trust its
hook definition before testing. In a fresh task on a Git repository with a
writable remote, request a small edit in plain language without naming a skill
or asking for a PR. Confirm that the agent loads the ordinary workflow and
creates or reuses a tracking issue before implementation and hands off a linked PR
at the exact changed head before its final response. Confirm the issue lists that PR
and the PR lists that issue. Repeat with several issues in one PR and one issue
spanning several PRs to check many-to-many tracking and complete-issue closure. Repeat with
an existing matching PR to check that it is updated rather than duplicated.
Use separate read-only and explicit local-only tasks to verify the no-PR
boundaries. Do not use a hook-trust bypass for acceptance; a rejected or
untrusted hook is an incomplete routing test, even if direct hook invocation
prints the expected guidance.
In a disposable Git repository with no remote, a tracked edit must remain
recoverable and the final response must name the missing remote as the PR
handoff blocker. The route supplies that specific fact without exposing remote
URLs.

The same package has a separate asynchronous `UserPromptSubmit` hook for automatic
session titles. Its background worker generates and writes the exact session title
without delaying the user turn. It fails closed when the local Codex thread store,
bundled app-server, or title protection state is unavailable; see
[automatic session titles](../plugins/agentic-workflows/skills/agentic-workflows/references/session-title-policy.md).

## Development checks

Run `uv run python scripts/run_local_ci.py` before opening or updating a pull
request. It checks generated prerequisites, mirrors, and marketplaces, runs the
repository tests and Ruff, validates every Claude package, and smoke installs a
shared package. The full run requires `uv`, ImageMagick 7, and Claude Code CLI.
