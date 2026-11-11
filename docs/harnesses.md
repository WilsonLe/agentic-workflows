# Codex support

Agentic Workflows supports Codex only. Install the complete suite from `main`
through `.agents/plugins/marketplace.json`; see [onboarding](../plugins/agentic-workflows/skills/agentic-workflows/references/onboarding.md).
All catalog skills target Codex. There are no alternate-host packages, manifest
adapters or host fallback instructions.

The [Delegation skill](../plugins/agentic-workflows/skills/delegation/SKILL.md)
uses Codex native task/session controls and saved settings. New independent Git
sessions use an isolated worktree by default. Verify actual working directory,
configuration and required capabilities before dependent work. The suite supplies
instructions; installing it does not create missing native task or browser tools.

Remote provider operations use configured Codex plugins/connected apps under the
[shared provider contract](../plugins/agentic-workflows/skills/agentic-workflows/references/service-browser-operations.md).
Codex owns authentication. Reuse connections and verify the exact account, project,
and environment through tools; recover missing connections through Codex. Missing
connections, operations, or permissions remain explicit blockers. The suite does
not provision local CLI tokens, export/import provider credentials, or copy agent
authentication into worktrees. Local development tools and application runtime
configuration remain separately scoped.

Browser, rendering, image, media and provider workflows still need the tools
listed in their prerequisites. Chrome extension verification requires a
Chrome-capable extension channel; the in-app browser cannot prove extension
execution. Local research or render output is distinct from saved provider state.

Every skill links to the generated package-local `CAPABILITIES.md`. Use Codex
plugin discovery for external companion tools. The automatic-title hook remains
the sole install-time behavior exception; ordinary workflow routing uses skill
metadata. See [session title policy](../plugins/agentic-workflows/skills/agentic-workflows/references/session-title-policy.md).

Verify discovery and workflow behavior in fresh Codex tasks with ordinary requests.
Inspect the loaded skill, scope, approvals, actual tool calls and final readback.
Catalog/package checks establish distribution integrity, not future agent adherence.

## Development checks

Edit `plugins/agentic-workflows` and the existing catalog. Refresh metadata with
`uv run python scripts/generate_plugin_packages.py --write`. Run focused tests,
targeted Ruff, package validation, generated metadata parity and ADR checks before
opening or updating a PR. Run `uv run python scripts/run_local_ci.py` only when
merging is requested; it requires `uv` and ImageMagick 7. Focused checks are not
full-suite evidence.

Release changes also build and verify a portable Codex distribution in a new or
empty directory outside the checkout on a filesystem with executable permissions:

```sh
stage_dir=$(mktemp -d)
uv run --locked python scripts/generate_plugin_packages.py --build "$stage_dir"
uv run --locked python scripts/generate_plugin_packages.py --check-build "$stage_dir"
uv run --locked python scripts/validate_plugin_packages.py --build-root "$stage_dir"
```

The distribution contains `.agents/plugins/marketplace.json` and the complete
`plugins/agentic-workflows` tree, including native manifest, UI metadata, helpers,
licenses and the title hook. Generation performs no host transformations. Parity
checks reject missing/changed/unexpected files, unsafe entries and mode drift.

The **Publish Codex plugin distribution** workflow builds and verifies current
`main`, archives the verified tree with file modes, and publishes it to `dist`
with a `Source-Commit` trailer. Stale source builds are skipped, identical trees
retain the previous commit, and failed verification or push leaves the last
release intact. Codex marketplace installation continues to use `main`.

For rollout, inspect the Actions log, compare the source trailer and verify the
published tree from a fresh checkout. Retry the workflow from current `main` on
transient failure. Recover a bad release by reverting its source on `main` and
verifying the resulting forward publish. The next successful publish replaces
legacy distribution paths; no manual branch rewrite is needed.
