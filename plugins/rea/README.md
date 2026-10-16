# REA

A thin wrapper around [REA's upstream setup flow](https://rea.tools/get-started/),
kept as a customization point. The `rea-setup` skill runs
`npx rea-agents@latest setup`, shows the setup plan for approval, and verifies the
installation after approved setup. REA supplies its own investigation skill.

This component is included in the `agentic-workflows` bundle for Codex, Claude Code,
and OpenCode. Installing the bundle makes the wrapper discoverable; REA setup runs
only when requested. Start a new session after installing or updating the bundle.

Example request:

> Install REA and connect it to this coding agent using npx rea-agents@latest setup.
> Show me the setup plan for approval, then verify the installation.
