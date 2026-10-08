# Repository checks

Before opening or updating a pull request, run `uv run python scripts/run_local_ci.py`
from the repository root. Report the result in the pull request. Fix failures
before requesting review; do not treat a partial run as a pass.

# Design and instruction changes

Edit the existing abstraction before introducing a new one. Inspect its responsibility,
callers, and contracts first. When a new boundary is necessary, keep it atomic: one
cohesive responsibility, explicit dependency direction and state ownership, and clear
input/output or data schemas, including validation and failure behavior.

Apply the shared [design method](plugins/agentic-workflows/skills/engineering-exploration/SKILL.md#existing-abstractions-first)
to this repository too. Extend the existing skill, reference, helper, or schema owner;
avoid parallel guidance or validators. Edit canonical package sources and regenerate
maintained mirrors with the existing catalog and generator.
