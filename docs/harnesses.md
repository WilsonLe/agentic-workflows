# Harness support

The catalog declares support per package and skill. Both harnesses use the same canonical instructions and prerequisites. Codex uses `.agents/plugins/marketplace.json` and canonical `plugins/` packages. Claude Code uses `.claude-plugin/marketplace.json` and generated packages under `generated/claude/plugins/`.

A skill appears in the Claude package only when its catalog entry includes `claude-code`. Skills that require Codex task controls or Codex-specific browser/image tools remain Codex-only. No host runtime adapter is included. Provider tools, API credentials, and CLIs are configured when the selected skill requires them.

## Development checks

Run `uv run python scripts/generate_plugin_packages.py --check` to verify generated prerequisites, mirrors, and marketplaces. Run `claude plugin validate .` and validate each generated package when Claude CLI is available.
