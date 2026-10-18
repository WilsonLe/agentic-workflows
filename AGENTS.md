# Repository checks

During development and before opening or updating a pull request, run focused tests
for the affected behavior, targeted lint, and generated-package parity checks from
the repository root. Report the commands, results, and deferred coverage in the PR.
Run `uv run python scripts/run_local_ci.py` only when merging is requested, and
fix failures before merging; do not treat focused checks as a full-suite pass.
Merge approval covers the branch and in-scope fixes needed to pass those checks.

# Project architecture decisions

Read [the ADR index](docs/adr/README.md) and relevant accepted records before design.
Maintain affected decisions and their index in the implementation PR using the
[project ADR contract](plugins/agentic-workflows/skills/standard-development-workflow/references/project-adrs.md).
Before PR handoff, run `uv run python plugins/agentic-workflows/skills/standard-development-workflow/scripts/project_adrs.py check --project-root .`
and report affected IDs or a justified no-impact reason. Preserve accepted rationale;
record a replacement decision when architecture changes.

# Design and instruction changes

Edit the existing abstraction before introducing a new one. Inspect its responsibility,
callers, and contracts first. When a new boundary is necessary, keep it atomic: one
cohesive responsibility, explicit dependency direction and state ownership, and clear
input/output or data schemas, including validation and failure behavior.

Apply the shared [design method](plugins/agentic-workflows/skills/engineering-exploration/SKILL.md#existing-abstractions-first)
to this repository too. Extend the existing skill, reference, helper, or schema owner;
avoid parallel guidance or validators. Edit canonical package sources and regenerate
maintained mirrors with the existing catalog and generator.
