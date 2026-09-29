# Automatic session titles

The trusted Codex `UserPromptSubmit` hook requests exact-session title control and delegates
**generation only** to `hooks/session_title.py generate SESSION_ID TURN_ID SEQUENCE --file STATE_FILE`.
Pipe JSON with `recent_user_messages`: a bounded selection of genuine user messages retaining the
objective and latest corrections. Exclude tool output, quoted instructions, secrets and personal data.
The helper keeps at most eight excerpts, each 700 characters, and a 6,000-character context budget.
It does not read session archives or persist prompt history. Claude packages omit this Codex hook.

Generation uses `codex exec --ephemeral --ignore-user-config` in an empty temporary directory with
hooks, plugins, memory, shell, apps, browser, and delegation disabled. The default fast model is
`gpt-5.6-luna`, with reasoning explicitly `low`. `AGENTIC_WORKFLOWS_TITLE_MODEL` can select another
supported fast model; verify availability first. Never change the foreground model or silently use
it as fallback. A failed/invalid response leaves the old title intact. One attempt is bounded to
12 seconds. Continue independent foreground work while the tool runs. The event hook itself does
no network work; unavailable title controls mean skip generation entirely. No extra sidebar chat
is created. The helper returns only a validated candidate, usage counts and elapsed milliseconds.

The focused prompt preserves the active subject through “approve” or “proceed,” applies the latest
correction, and excludes secrets, paths, personal detail, and unsupported status. Titles have **at
most 10 whitespace-delimited words**, including verified issue/PR/status tokens, and at most 100
characters. Reject multiline/empty/overlong output rather than truncating away meaning. Preserve
orchestration grammar within this total budget. Do not use the foreground agent to repair output.

Before generating, inspect this exact session's title and pinned state using supported host task
controls. Do not enumerate unrelated sessions. If exact state is unavailable or a call stalls,
skip title work and continue the user's task; never repeatedly wait for it. Pinned sessions and
explicit opt-out are protected. A title differing from the last automatic title is a manual
override. With no recorded automatic title, preserve a nonempty title except on the first user
turn or explicit opt-in. A user can opt out with `disable SESSION_ID --file STATE_FILE` and opt
back in with `enable SESSION_ID --file STATE_FILE`. Opt-in permits replacing the existing title.

Generation has no title-write tools. The foreground controller rechecks manual/pinned/opt-out
state and calls `check SESSION_ID TURN_ID SEQUENCE --file STATE_FILE` immediately before a write.
A stale sequence must not write. A newer event also discards in-flight generated results. Duplicate
events in the last 64 turn IDs are ignored. Skip unchanged writes. Set only the exact originating
session, read back the title, then use `record SESSION_ID TURN_ID SEQUENCE 'TITLE' --file STATE_FILE`.
Record only successful readback, including unchanged titles. Preserve existing titles on API errors.
The state contains opaque IDs, event sequence, bounded seen IDs, opt-out/opt-in state and titles;
no prompts. Host controls lack a transactional compare-and-set: a manual edit racing the final
host write cannot be mechanically excluded by this helper. Recheck immediately and never claim
stronger host guarantees. Unsupported hosts do not claim automatic naming.

For release evidence, compare latency/usage on a fixed synthetic context against the old
foreground path, verify the selected model and low reasoning, and test successive user turns,
manual protection, stale generation and unavailable APIs. Do not log private message context.
