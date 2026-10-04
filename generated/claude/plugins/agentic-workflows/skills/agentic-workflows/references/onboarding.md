# Agentic Workflows onboarding

This public suite packages reusable skills for Codex and Claude Code. Start with
`agentic-workflows` to find the right skill; use a focused package when you want
its smaller set of skills. A skill explains **how** to work on a task. The host
controls **who** does the work and which model runs it.

## First use

1. Choose your harness and a package from the public
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

For another package, replace `<package>` with its name, then use
`codex plugin add <package>@agentic-workflows` or
`claude plugin install <package>@agentic-workflows`. Check the
[package support list](https://github.com/wilsonle/agentic-workflows/blob/main/README.md#packages)
first: some packages and skills are Codex only. A successful install shows that
the package is available; run a small task using the chosen skill to confirm
that its tools and connections work.

## Find the right workflow

| You want to... | Start with... |
| --- | --- |
| Plan, implement, and verify software work | `standard-development-workflow` in Codex; `payloadcms` for Payload projects |
| Coordinate a full Codex delivery run | `agent-orchestration` (`orchestration` or `$sdlc-loop`), only when explicitly invoked |
| Research or write with source checks | `literature-review`, `systematic-literature-review`, or `guided-writing` |
| Work with business systems or providers | `erpnext-operations`, `railway-account`, or the central Cloudflare and DigitalOcean skills |
| Develop product ideas and visual material | `trend-to-product`, `excalidraw`, `qr-code-generator`, or Codex-only `image-editing` |
| Work with media, marketing, or personal tasks | `youtube`, `restaurant-marketing`, `david-jones-customer-service`, or Codex-only `reddit` and `calorie-tracker` |

The router can select a more specific skill once you describe your task.
In Codex, a trusted central-package prompt hook reminds the agent to use the
ordinary `standard-development-workflow` for Git repository changes, including
plain-language edits and terse follow-ups. The hook does not create a PR or
activate `$sdlc-loop` autopilot. The workflow's PR handoff remains an agent
responsibility, with explicit local-only and concrete-blocker exceptions.
After installing or updating the package, review and trust its hook definition
in Codex and verify the route in a fresh task. Without hook trust, skill metadata
alone cannot guarantee that Codex selects the workflow.
Claude Code receives the clarified router guidance, but the Standard Development
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
  use a separate session or worktree when your Claude version supports it.
  Keep the request outcome focused and open ended, for example: “Find the best
  way to simplify onboarding and report what you recommend.”

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
See the [OpenAI model guide](https://developers.openai.com/api/docs/models) and
[Claude Code model guide](https://code.claude.com/docs/en/model-config) when
model availability changes.

## Update an existing installation

The marketplace name is `agentic-workflows` on both hosts. Refresh it and
check the installed package:

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

Restart Claude Code, then invoke a skill in a new session.

In Claude Code, repeat `claude plugin update <package>@agentic-workflows` for
each additional installed package. In Codex, the marketplace upgrade refreshes
the configured Git snapshot and its installed plugin files; verify the package
and skill in a new task. If either host still shows an old version, use that
host's plugin manager to inspect the installed source before reinstalling.

If you installed the former AMSoft-named packages, follow the repository's
[migration notes](https://github.com/wilsonle/agentic-workflows/blob/main/README.md#updates-and-migration)
to remove old names and install current package names. Retired WordPress
workflows are covered by the
[operator migration guide](https://github.com/wilsonle/agentic-workflows/blob/main/docs/retired-site-workflows.md).
