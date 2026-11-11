# Agentic Workflows onboarding

This public suite provides one `agentic-workflows` plugin with all 69 skills for
Codex. A skill explains **how** to work on a task. The host
controls **who** does the work and which model runs it.

## First use

1. Get the Codex plugin from the public
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

For opt-in full-access local defaults, ask to activate the bundled Codex configuration
using `agentic-workflows-config-transfer`. Its [activation guide](../../agentic-workflows-config-transfer/references/codex-configuration.md)
locates the installed `config.toml` asset and the preview/apply/restore commands.
Plugin installation and updates distribute the asset without applying user settings.
Activate separately on each machine; existing tasks can retain their earlier permissions.

For ordinary delegation, describe the task or invoke `delegation`: for example,
"start another session to audit this project; stay here and manage it." The skill
uses Codex's existing configuration unless an override is explicitly
requested and verifies settings before dependent work. New independent sessions in
Git repositories use a new isolated worktree by default, including read-only audits;
an explicit directory or existing lane request takes precedence. It requires no
launch hook or global instruction and does not activate the bundled Codex preset. Verify available Codex task controls before dispatch.

## Find the right workflow

| You want to... | Start with... |
| --- | --- |
| Plan, implement, and verify software work | `standard-development-workflow` in Codex, with `payloadcms-development` for Payload projects |
| Coordinate a full Codex delivery run | `orchestration` or `$sdlc-loop`, only when explicitly invoked |
| Research or write with source checks | `literature-review-workflow`, `systematic-literature-review-workflow`, or `guided-writing-coach` |
| Work with business systems or providers | `erpnext-operations`, `supabase-cli`, `railway-account-operations`, `vercel-account-operations`, or the central Cloudflare and DigitalOcean skills |
| Edit video and speech assets | `video-editing`, `speech-to-text`, `text-to-speech`, `audio-editing`, `typography`; integrate `motion-design` and `music-composition` |
| Develop product ideas and visual material | `trend-product-onboarding`, `motion-design`, `excalidraw-scene-operations`, `qr-code-generation`, or Codex-only `food-image-editing` |
| Design frontends or Chrome extensions | `ui-design`, `chrome-extensions`, or `modern-web-guidance` |
| Work with media, marketing, or personal tasks | `youtube-content-inspection`, `restaurant-marketing-management`, `david-jones-till-sales`, or Codex-only `reddit-browsing` and `calorie-tracker` |

The router uses skill descriptions to select ordinary `standard-development-workflow`
for Git repository changes across the three hosts, including terse follow-ups.
Verify discovery and the task's actual decisions in a fresh session after an update.
Codex's separate autopilot entry points retain their own activation requirements.
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
See [Codex task and worktree guidance](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)
for native controls. Delegation retains the selected workflow's approval and
verification rules.

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

Use the configured Codex model and reasoning by default. Apply an override only
when the user or selected workflow authorizes it. Tool access and the skill's
prerequisites still determine whether the task can run.

Two Codex-only delivery skills provide their own model routing:

- `orchestration` requires `gpt-5.6-luna` at `max` reasoning for every review,
  review remediation, and verification task. The host must confirm the
  effective setting. Choose the implementation model for the work itself.
- `$sdlc-loop` has a phase-specific cost and independence matrix: Terra/high
  for control and implementation, Luna/medium for routine inventory, Sol/xhigh
  for planning, risk-scaled Luna/Terra/Sol review, and Luna/high for
  deterministic verification. Its [full routing table](https://github.com/wilsonle/agentic-workflows/blob/main/plugins/agentic-workflows/skills/sdlc-loop/SKILL.md#cost-and-topology-matrix)
  states the fallbacks and delivery settings. Treat that table as a preference
  where the skill says so; do not replace it with the generic table above.

## Update an existing installation

The marketplace name is `agentic-workflows` for Codex. Refresh it
and check the installed package:

### Codex

For an update that also approves this suite's current enabled hooks, resolve the
installed `agentic-workflows-config-transfer` skill and run its `codex_config.py update`
command. See [suite updates and hook trust](../../agentic-workflows-config-transfer/references/codex-configuration.md#suite-updates-and-hook-trust)
for the first-update bootstrap, backup/restore and a separate `trust-hooks` refresh.
This leaves unrelated hooks, explicit disables and permission defaults in place.

The native update commands remain available; they require separate hook review
or that trust-refresh command:

```sh
codex plugin marketplace upgrade agentic-workflows
codex plugin list --marketplace agentic-workflows
```

Restart the Codex app or CLI session, then invoke a skill in a new task.

For older focused installations, install or update `agentic-workflows` first and
verify the skills you use in a fresh session. Then remove the focused plugins
through the host's plugin manager, preserving credentials and local workflow data.
A marketplace refresh does not guarantee their removal; leaving them enabled can
expose duplicate skills. Pinned standalone installations can use the
[legacy-components-v1 tag](https://github.com/WilsonLe/agentic-workflows/tree/legacy-components-v1).

If you installed the former AMSoft-named packages, follow the repository's
[migration notes](https://github.com/wilsonle/agentic-workflows/blob/main/README.md#updates-and-migration)
to remove old names and install current package names. Retired WordPress
workflows are covered by the
[operator migration guide](https://github.com/wilsonle/agentic-workflows/blob/main/docs/retired-site-workflows.md).

## Service account setup

Vercel always uses the [Vercel plugin/connected app in Codex](../../vercel-account-operations/SKILL.md).
Recover its connection through Codex and verify the exact team/project/environment
with app tools; exclude Vercel credentials from local setup and worktree copies.


For Supabase, Railway, Cloudflare, DigitalOcean, ERPNext, and Excalidraw, follow
[authenticated CLI and browser assistance](service-browser-operations.md).
Check existing CLI authentication and exact project account/target first. Use
the Codex in-app browser for supported login or secure key/token acquisition only when
needed, or let the user complete that step, then return to CLI verification. Execute supported operations
through authenticated CLI/client; browser service operations are fallback only
for an authenticated client capability gap. Do not expose credentials or extract
browser sessions.

Supabase, Railway, Cloudflare, DigitalOcean, and OpenRouter use project-local, gitignored `.cli/` credential storage.
Follow [the shared credential contract](task-authority-and-secrets.md#project-local-cli-credentials)
and their provider skills to authenticate, persist, and verify that storage.
Carry local env and `.cli/` files into new worktrees of the same project before
dependent work, then verify authentication and target selection again.
