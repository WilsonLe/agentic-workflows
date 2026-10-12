# Harness support

The catalog declares support per package and skill. All three harnesses use the same canonical instructions and prerequisites. Codex uses `.agents/plugins/marketplace.json` and canonical `plugins/` sources. Claude Code uses `.claude-plugin/marketplace.json` and generated sources under `generated/claude/plugins/`. Both marketplaces publish only `agentic-workflows`. OpenCode V2 loads the native skills bundle described below. Component packages remain as maintenance sources and compatibility artifacts; their supported skills are all included in the bundle.

The bundled [UI Design](../plugins/ui-design/README.md) package shares
one instruction-only design skill across all three harnesses. It has no additional
runtime dependencies; rendered inspection and implementation use the tools
available in the current host and project.

The bundled [Chrome Extensions](../plugins/chrome-extensions/README.md) package
provides two shared skills and a dependency-free Python manifest audit. Chrome
DevTools MCP is optional and configured separately in the selected host; the
package does not register a server or attach to a browser profile on installation.
Runtime verification requires a compatible Chrome/server connection with extension
tools. The in-app browser can inspect websites but cannot prove extension execution.

A skill appears in the Claude package only when its catalog entry includes `claude-code`. Skills that require Codex task controls or Codex-specific browser/image tools remain Codex-only. No host runtime adapter is included. Railway, Vercel, Cloudflare, DigitalOcean, ERPNext, and Excalidraw default to
authenticated provider CLIs or bundled protected command-line clients. Missing
authentication uses the built-in Codex browser on Codex (supported browser controls
on other hosts) for login or concealed key acquisition, followed by CLI identity
and target verification. Browser service operations are fallback only when the
authenticated client cannot perform the requested action. Local preparation tools
remain task-specific.

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

## OpenCode V2

OpenCode consumes `generated/opencode/agentic-workflows/skills` through its native
`skills` configuration. It is not a Codex/Claude marketplace or an OpenCode runtime
plugin. The 51 supported skills share canonical sources with Claude Code; the
catalog declares `opencode` explicitly and the existing generator supplies their
supporting assets, licenses, executable modes, filtered router, and capability map.
Codex-only skill trees, hooks, and runtime manifests are excluded. Links to excluded
skill documentation point upstream without advertising those skills as available.

See [installation and troubleshooting](../plugins/agentic-workflows/skills/agentic-workflows/references/onboarding.md#opencode-v2).
Use a persistent clone and absolute source path outside this repository. The
committed `opencode.json` is for sessions started at this repository root; V2
resolves relative skill paths from the working directory, not the config file.
The full generated package must remain together because skills reference shared
scripts via `<plugin-root>` and maps via `../../CAPABILITIES.md`. On OpenCode,
resolve `<skill-root>` to the loaded base directory and `<plugin-root>` to its
grandparent before running helpers. No implicit hook routing or Codex control-plane
behavior is promised. Follow project `AGENTS.md` and available host tools.

Generation/parity checks compare the complete OpenCode bundle: entrypoints,
references, templates, binary assets, helper scripts, executable permissions, and
unexpected files. A live discovery/load/workflow smoke test is separate from that
static parity check and does not establish full provider/browser compatibility.

### Rough quality smoke test

After installation, inspect the live registry for this checkout (substitute its
absolute directory; this uses OpenCode's existing shared service):

```sh
opencode --version
opencode api get '/api/skill?location[directory]=/absolute/path/to/agentic-workflows'
```

Confirm every `opencode`-supported catalog ID resolves to this generated bundle,
has a description, and does not include the eight Codex-only IDs. In fresh sessions:

- Ask Humanizer to simplify a sentence with a specific number and date. Check the
  skill tool actually loads the installed file, preserves facts, and does not edit files.
- Give Grill Me a fully settled interview-only brief. Expect a decision summary,
  no manufactured questions, and no implementation.
- Ask QR Code Generation for a plain exact-payload PNG/SVG in a disposable local
  workspace. Verify it runs the installed shared helper and reports a real decoder
  result. SVG's companion-PNG verification is not proof of direct SVG rasterization.

Use an available configured model rather than assuming the CLI default is healthy.
These samples test discovery, instruction loading, scope boundaries, asset paths,
and a local helper—not every workflow, provider integration, or host mode. Focused
checks and live test evidence belong in the PR; full CI remains a merge-time gate.

## Capability handoffs

Every skill entrypoint links to its package-local `CAPABILITIES.md`. The existing
catalog generator builds these maps from canonical skill descriptions and harness
support, with links for included skills and explicit bundle requirements for
other supported capabilities. Claude and OpenCode maps omit Codex-only entries. Shared handoff
guidance keeps state ownership, prerequisites, authority, and evidence explicit.
External plugins are discovered through the current host rather than assumed.

Music Composition and Motion Design share the scene's timeline: original local
synthesis consumes cue times and returns WAV plus editable inputs; Motion Design
owns final muxing and encoded-video verification. Standalone music uses Python's
standard library; FFmpeg is needed only for requested encoding or mixing.

## Development checks

Run focused affected tests, targeted Ruff checks, package validation, and
`uv run python scripts/generate_plugin_packages.py --check` before opening or
updating a pull request. Run `uv run python scripts/run_local_ci.py` when merging
is requested, as required by root `AGENTS.md`. The full run checks generated prerequisites, mirrors, and marketplaces, runs the
repository tests and Ruff, validates every Claude package, and smoke installs the
consolidated package. The full run requires `uv`, ImageMagick 7, and Claude Code CLI.
