# Agentic Workflows onboarding

This public suite provides one `agentic-workflows` plugin with all 65 skills for
Codex and a harness-filtered subset for Claude Code and OpenCode V2. A skill explains **how** to work on a task. The host
controls **who** does the work and which model runs it.

## First use

1. Choose your harness for the plugin from the public
   [Agentic Workflows repository](https://github.com/wilsonle/agentic-workflows).
2. Install the central package using the commands below.
3. Start a new task or session. Ask for the outcome you need, or name a skill
   directly. Read that skill's **Prerequisites** before using provider tools or
   accounts. Set up only the prerequisites for the skill you chose.

### Codex

```sh
codex plugin marketplace add wilsonle/agentic-workflows
codex plugin add agentic-workflows@agentic-workflows
```

### Claude Code

```sh
claude plugin marketplace add wilsonle/agentic-workflows
claude plugin install agentic-workflows@agentic-workflows
```

Start a new session, or run `/reload-plugins` in an open one. Try
`/agentic-workflows:grill-me` or `/agentic-workflows:humanizer`, or describe the task
and let Claude load the matching skill. Smaller models such as Haiku load plugin
skills less reliably, so name the skill there. The package contains the 55
portable skills; Codex-only workflows and hooks are excluded.

Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` in the
helper commands of a loaded `SKILL.md`. In references read later, `<skill-root>` is
the loaded skill's base directory and `<plugin-root>` is two levels above it: the
installed plugin root under `~/.claude/plugins/cache/agentic-workflows/agentic-workflows/`.
Resolve both to absolute paths before running a helper or giving a command to the user.
If a skill's `SKILL.md` is read as a file instead of loaded, `${CLAUDE_SKILL_DIR}` is the
directory containing it and `${CLAUDE_PLUGIN_ROOT}` is two levels above.

Because the plugin cache is outside your project, Claude Code may ask before it reads
a skill's references or runs a helper. Approve those prompts, or add
`Read(/plugins/cache/agentic-workflows/**)` to `permissions.allow` in your user
settings (`~/.claude/settings.json`, or `settings.json` in `CLAUDE_CONFIG_DIR`); the
leading `/` anchors at that settings directory. Unattended `claude -p` runs also need
rules for the helper commands they use, or `--permission-mode auto`. Project
rules come from `CLAUDE.md`, or from `AGENTS.md` when no `CLAUDE.md` exists (Claude
Code 2.1.277 or later). Browser-assisted steps use Claude in Chrome when it is
connected (`claude --chrome` or `/chrome`); otherwise the agent gives you the step to
complete. See the [harness guide](https://github.com/wilsonle/agentic-workflows/blob/main/docs/harnesses.md#claude-code)
for the Agent SDK and other Claude surfaces.

### OpenCode V2

Clone this repository to a persistent local directory. Add its generated skills
directory to the `skills` array in `~/.config/opencode/opencode.json(c)` for all
projects, or a project's `opencode.json(c)` for that project only. Merge this entry
into existing settings; do not replace unrelated configuration:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["/absolute/path/to/agentic-workflows/generated/opencode/agentic-workflows/skills"]
}
```

The committed repository config enables these skills when OpenCode starts at this
repository root. Use an absolute path for other projects or nested working
directories: V2 resolves relative skill sources from the active working directory,
not the config file. Keep the complete generated bundle, not just its `skills/`
directory; shared helpers and capability maps live alongside it.

Start a fresh session and try `@grill-me`, `@engineering-review`, or `@humanizer`.
OpenCode discovers the 55 portable `SKILL.md` entrypoints and loads supporting files
on demand. `<skill-root>` means the loaded skill's base directory; `<plugin-root>`
means the generated bundle directory two levels above it (the parent of `skills/`).
Resolve these placeholders to real paths before executing a helper. They are not
shell variables or OpenCode-provided template substitutions.

This is a native skills source, not an OpenCode JavaScript plugin or a marketplace
install. No tools, MCP servers, hooks, credentials, or model settings are added.
Provider/browser/image workflows still require their declared tools; do not emulate
missing capabilities or claim verification without evidence. Standard Development
Workflow, SDLC autopilot, orchestration, session reflection, config transfer, Reddit,
food-image editing, and calorie tracking remain Codex-only. Local links to excluded
workflows resolve to upstream documentation, not an installed capability.

See [OpenCode V2 skills](https://opencode.ai/v2/docs/skills) for discovery and
permissions. If a skill is missing, check its exact directory-derived ID, skill
permission, configured absolute source path, and any later source with the same ID.

The marketplace lists only `agentic-workflows`. Check the
[skill support list](https://github.com/wilsonle/agentic-workflows/blob/main/README.md#packages):
some skills are Codex only. A successful install shows that the package is available;
run a small task using the chosen skill to confirm its tools and connections work.

## Find the right workflow

| You want to... | Start with... |
| --- | --- |
| Plan, implement, and verify software work | `standard-development-workflow` in Codex; `payloadcms-development` for Payload projects |
| Coordinate a full Codex delivery run | `orchestration` or `$sdlc-loop`, only when explicitly invoked |
| Research or write with source checks | `literature-review-workflow`, `systematic-literature-review-workflow`, or `guided-writing-coach` |
| Work with business systems or providers | `erpnext-operations`, `supabase-cli`, `railway-account-operations`, `vercel-account-operations`, or the central Cloudflare and DigitalOcean skills |
| Edit video and speech assets | `video-editing`, `speech-to-text`, `text-to-speech`, `audio-editing`, `typography`; integrate `motion-design` and `music-composition` |
| Develop product ideas and visual material | `trend-product-onboarding`, `motion-design`, `excalidraw-scene-operations`, `qr-code-generation`, or Codex-only `food-image-editing` |
| Design frontends or Chrome extensions | `ui-design`, `chrome-extensions`, or `modern-web-guidance` |
| Work with media, marketing, or personal tasks | `youtube-content-inspection`, `restaurant-marketing-management`, `david-jones-till-sales`, or Codex-only `reddit-browsing` and `calorie-tracker` |

The router can select a more specific skill once you describe your task.
In Codex, a trusted central-package prompt hook reminds the agent to use the
ordinary `standard-development-workflow` for Git repository changes, including
plain-language edits and terse follow-ups. The hook does not create a PR or
activate `$sdlc-loop` autopilot. The workflow's PR handoff remains an agent
responsibility, with explicit local-only and concrete-blocker exceptions.
After installing or updating the package, review and trust its hook definition
in Codex and verify the route in a fresh task. Without hook trust, skill metadata
alone cannot guarantee that Codex selects the workflow.
Claude Code and OpenCode receive the clarified router guidance, but the Standard Development
Workflow skill and this Codex prompt hook are not available there.
WordPress workflows have been retired from the current marketplace.
The [task-continuity guide](task-continuity.md) explains how the selected workflow keeps
deliverables, source access, and external setup evidence accurate across turns.

## Delegate simply

Describe the desired outcome in a sentence and let the delegate investigate
and choose an approach. Add a constraint only when it matters. For example:

> Improve this repository's onboarding and open a PR with the result.

- **Codex:** Give substantial, independent implementation work a separate
  project task and worktree. Ask another task to review or verify the result
  after implementation is ready. Do not have two tasks edit one worktree at
  the same time. If you explicitly designate a control plane or orchestration
  session, follow the Codex-only `orchestration` skill's stricter handoff and
  model rules.
- **Claude Code:** Use a subagent for a bounded investigation or review; ask
  the main session to integrate the findings. For independent implementation,
  use a separate session or worktree, such as `claude --worktree`.
  Keep the request outcome focused and open ended, for example: “Find the best
  way to simplify onboarding and report what you recommend.”
- **OpenCode:** Use the host's session/subagent tools only when the task and
  current instructions authorize delegation. Keep independent edits isolated and
  preserve the same scope, approval, and verification boundaries; installing these
  skills does not enable Codex task controls.

See [Codex task and worktree guidance](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)
and [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) for
current host controls. Delegation does not bypass a selected skill's safety,
approval, or verification rules.

### Codex voice mode

When speaking with a user in an active Codex voice chat, keep each response to
one or two short sentences. Answer simple questions directly. Prefer handing
sustained independent work to a separate Codex task and worktree, using a short,
open-ended outcome request; return with the result instead of narrating every
step. Follow any stricter handoff rules in the selected skill.

For a live delegated task, make the first status check after five seconds. If
there is no change, double the interval to 10, 20, then 40 seconds, capped at
one minute between later checks; reset to five seconds after meaningful
progress. Use the host's wait or status control for the same live task, and
respond immediately when it finishes, needs input, or the user asks for an
update. A quiet poll is not evidence that the task stopped.

## Choose a model

These are starting points, not model requirements for each skill. Select a
model available in your host and increase reasoning for difficult or
consequential work. Tool access and a skill's prerequisites still determine
whether the task can run. The Claude package contains only skills declared for
Claude Code in the catalog.

| Task | Codex starting point | Claude Code starting point |
| --- | --- | --- |
| Route to a skill, look up files, or summarize a small result | GPT-6 Luna, low or medium reasoning | Haiku |
| Routine development, provider operations, writing, and media work | GPT-6 Sol, medium or high reasoning | Sonnet |
| Architecture, hard debugging, complex research synthesis, or high-stakes decisions | GPT-6 Astra, high or xhigh reasoning | Opus |
| Independent review or verification outside formal orchestration | GPT-6 Sol or Astra according to complexity | Sonnet or Opus according to complexity |

Two Codex-only delivery skills provide their own model routing:

- `orchestration` requires `gpt-5.6-luna` at `max` reasoning for every review,
  review remediation, and verification task. The host must confirm the
  effective setting. Choose the implementation model for the work itself.
- `$sdlc-loop` has a phase-specific cost and independence matrix: Terra/high
  for control and implementation, Luna/medium for routine inventory, Sol/xhigh
  for planning, risk-scaled Luna/Terra/Sol review, and Luna/high for
  deterministic verification. Its [full routing table](https://github.com/wilsonle/agentic-workflows/blob/main/plugins/agent-orchestration/skills/sdlc-loop/SKILL.md#cost-and-topology-matrix)
  states the fallbacks and delivery settings. Treat that table as a preference
  where the skill says so; do not replace it with the generic table above.

Check Claude Code's `/model` menu for the aliases and versions your
installation actually offers.
In OpenCode, choose an available model in the host; the skills source does not
override model/provider settings.
See the [OpenAI model guide](https://developers.openai.com/api/docs/models) and
[Claude Code model guide](https://code.claude.com/docs/en/model-config) when
model availability changes.

## Update an existing installation

The marketplace name is `agentic-workflows` for Codex and Claude Code. Refresh it
and check the installed package:

### Codex

```sh
codex plugin marketplace upgrade agentic-workflows
codex plugin list --marketplace agentic-workflows
```

Restart the Codex app or CLI session, then invoke a skill in a new task.

### Claude Code

```sh
claude plugin marketplace update agentic-workflows
claude plugin update agentic-workflows@agentic-workflows
claude plugin list
```

Run `/reload-plugins` in an open session or start a new one, then invoke a skill.
Claude Code installs an update only when the plugin version changes. The generated
Claude version (`<release>+claude.<digest>`) changes with the package content, and the
commands above install it; auto-update stays off for this marketplace unless you
enable it in `/plugin`. Cache directory names show `+` as `-`. If `claude plugin
update` still reports an old version, uninstall the plugin and install it again.

### OpenCode V2

Update the persistent clone with a fast-forward-only pull, then use a fresh
OpenCode session to verify the selected skill. Committed generated assets need no
local generation or Python setup merely to install; helper dependencies remain
workflow-specific. Remove just the added `skills` source entry to uninstall,
preserving unrelated settings, credentials, and project artifacts.

In Codex, the marketplace upgrade refreshes the configured Git snapshot and its
installed plugin files; verify the package and skill in a new task. If either host
still shows an old version, inspect the installed source in its plugin manager.

For older focused installations, install or update `agentic-workflows` first and
verify the skills you use in a fresh session. Then remove the focused plugins
through the host's plugin manager, preserving credentials and local workflow data.
A marketplace refresh does not guarantee their removal; leaving them enabled can
expose duplicate skills. Component sources remain in the repository for maintenance.

If you installed the former AMSoft-named packages, follow the repository's
[migration notes](https://github.com/wilsonle/agentic-workflows/blob/main/README.md#updates-and-migration)
to remove old names and install current package names. Retired WordPress
workflows are covered by the
[operator migration guide](https://github.com/wilsonle/agentic-workflows/blob/main/docs/retired-site-workflows.md).

## Service account setup

For Supabase, Railway, Vercel, Cloudflare, DigitalOcean, ERPNext, and Excalidraw, follow
[authenticated CLI and browser assistance](service-browser-operations.md).
Check existing CLI authentication and exact project account/target first. Use
the host's browser controls (the built-in Codex browser in Codex, Claude in Chrome
in Claude Code) for supported login or secure key/token acquisition only when
needed, or let the user complete that step, then return to CLI verification. Execute supported operations
through authenticated CLI/client; browser service operations are fallback only
for an authenticated client capability gap. Do not expose credentials or extract
browser sessions.

Supabase, Vercel, Railway, Cloudflare, and DigitalOcean use project-local, gitignored `.cli/` credential storage.
Follow [the shared credential contract](task-authority-and-secrets.md#project-local-cli-credentials)
and their provider skills to authenticate, persist, and verify that storage.
Carry local env and `.cli/` files into new worktrees of the same project before
dependent work, then verify authentication and target selection again.
