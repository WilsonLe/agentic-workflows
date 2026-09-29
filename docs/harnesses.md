# Harness support

The catalog declares support per package and skill. Both harnesses use the same canonical instructions and prerequisites. Codex uses `.agents/plugins/marketplace.json` and canonical `plugins/` packages. Claude Code uses `.claude-plugin/marketplace.json` and generated packages under `generated/claude/plugins/`.

A skill appears in the Claude package only when its catalog entry includes `claude-code`. Skills that require Codex task controls or Codex-specific browser/image tools remain Codex-only. No host runtime adapter is included. Provider tools, API credentials, and CLIs are configured when the selected skill requires them.

The central Codex package adds a `UserPromptSubmit` hook that provides conditional
Standard Development Workflow routing guidance when the task's working directory
is inside a Git repository. It runs only where Codex supports and the user trusts
plugin hooks. It is a routing reminder, not a PR creation or completion gate;
`$sdlc-loop` autopilot still requires direct invocation. Claude Code receives
the shared router text, but neither this hook nor the Codex-only Standard
Development Workflow skill runs there.

## Development checks

Run `uv run python scripts/run_local_ci.py` before opening or updating a pull
request. It checks generated prerequisites, mirrors, and marketplaces, runs the
repository tests and Ruff, validates every Claude package, and smoke installs a
shared package. The full run requires `uv`, ImageMagick 7, and Claude Code CLI.
