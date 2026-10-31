# Portable Codex full-access configuration

This is an opt-in **local** Codex preset, distributed with the plugin. It is not an
automatically loaded plugin configuration, hook, policy override, or credential bundle.
The `.agenticx` export/import allowlist does not carry Codex configuration or backups.
On each machine, install the plugin, then activate its local packaged asset explicitly.

Resolve `<skill-root>` from this loaded skill's directory. The asset is
`<skill-root>/templates/codex/config.toml` and the helper is
`<skill-root>/scripts/codex_config.py`. Do not guess a cache version or copy this
repository's path. The plugin root is two directories above `<skill-root>`.

## Start sessions with the saved configuration

For user-requested Codex work sessions, inherit the intended execution host's
`$CODEX_HOME/config.toml` (or `~/.codex/config.toml`). Confirm the target project
and existing Codex home without printing config contents or secrets. Retain the
existing environment; do not point `CODEX_HOME` at another installation to obtain
different permissions. Starting a session does not activate this preset.

Prefer a host task-creation capability only when it can inherit user configuration
without supplying permission overrides. If it forces a profile, approval policy,
or sandbox mode, use the installed native CLI for an ordinary work session:

```sh
codex exec --json --cd /resolved/project/root 'Read-only preflight: report your effective approval policy, sandbox and network restrictions. Do not perform dependent work.'
```

Keep the CLI in the foreground of a resumable execution tool, retain its emitted
`thread.started` ID, and monitor completion. Use native argument arrays or proper
shell quoting for real prompts. Do not add `--ignore-user-config`, `--sandbox`,
`--approve-for-me`, bypass flags, a profile, or `--config` permission overrides.
Do not silently select another model, enable hooks, or edit TOML to make a launch
pass. If the CLI or required host controls are unavailable, report that limitation.

Before assigning dependent work or claiming inherited permissions, read back the
exact new thread's effective approval policy, sandbox and network restrictions.
Use supported task readback or the exact session's recorded `turn_context` when
available; inspect only relevant permission fields. A host request or prompt
claiming full access is insufficient. If permissions differ from the intended
configuration, retain the session identity, report `permission_mismatch`, and do
not send dependent work or retry with forced permissions. Check applicable trusted
project/profile settings and managed requirements without rewriting them. Resume
and fork can retain a prior session's overrides; verify them by the same contract
instead of treating them as fresh inherit-config launches.

Use a read-only preflight as the initial prompt. Only after successful readback,
continue the verified thread with the authorized task through native CLI resume
or a host continuation capability proven to preserve those permissions. Missing
authoritative readback records `readback_unavailable` and blocks dependent work.

CLI sessions are not a promise of a desktop tab or of Goal mode. Orchestration
delegation still requires its authoritative Goal-mode and other workflow readbacks;
missing support blocks that lane. If a workflow requires full access but the saved configuration
is restrictive, record the incompatibility instead of overriding the user's choice.
Enforced managed, runtime, tool and OS policies still apply. This launch contract
does not authorize evading a denial, sending communications, merge or deployment.

This contract covers user work sessions. The separate ephemeral session-title
utility deliberately uses isolated configuration; it must not be reused as a
work-session launcher. Instruction/package checks establish the guidance contract,
not universal agent adherence. Report observed live session permissions separately
from untested write/network behavior or unchanged desktop-tool behavior.

## Activate and restore

Run with `uv` (which supplies Python 3.10+ and pinned `tomlkit`) or an equivalent
Python environment with `tomlkit==0.13.3`. The TOML editor preserves comments and
unrelated settings; regular-expression merging or replacing the whole config can
damage existing authentication, provider settings, or table scope.

Close competing configuration editors before applying. Start with the sanitized preview:

```sh
uv run <skill-root>/scripts/codex_config.py preview --all-configured-servers
uv run <skill-root>/scripts/codex_config.py apply --all-configured-servers
```

These commands match the practical full-access setup including every locally
configured MCP and plugin-server default. The explicit `--all-configured-servers`
option touches only definitions in this user config; it does not discover new
servers or change per-tool overrides. Omit it to retain existing server defaults.

Defaults target `$CODEX_HOME/config.toml`, or `~/.codex/config.toml` when unset.
Pass `--codex-home /chosen/local/codex-home` **before** the subcommand for a custom
installation. In PowerShell, quote resolved paths and use `$env:CODEX_HOME` to inspect
that environment variable; the helper uses Python's home resolution on Windows too.
Use the Codex home of the client/execution host you intend to configure, not another
machine or a project `.codex` directory. The helper refuses Git-contained or symlinked
destinations and never reads authentication stores. Do not print existing config or backups.

The result reports `applied` and an exact backup directory, or `unchanged` on repeat.
Backups can contain secrets from an existing config: keep them local and private.
The helper creates a private backup directory with the exact prior bytes and a
version-1 receipt (before/after SHA-256 and original file mode), then atomically
replaces config. A helper lock serializes helper operations; it cannot lock the
desktop settings editor. Re-preview after any external edit. A failed/interrupted
operation can leave its backup or `.agentic-workflows-config.lock`; inspect local
state and confirm no helper is running before removing only that stale lock.

```sh
uv run <skill-root>/scripts/codex_config.py restore /exact/returned/backup-directory
```

Restore checks that the current config still matches the applied bytes, restores
the original file and mode (or removes only the file it created), and retains the
backup. If config changed later, restore refuses to overwrite it. Reconcile those
changes locally; never force-copy a backup over newer settings. Backups do not
travel through plugin updates or `.agenticx` files. POSIX backups use mode 0700/0600;
on Windows, use an OS-user-private home with suitable ACLs: POSIX mode bits do not
establish Windows ACL isolation.

## Exact settings and scope

| Setting | Effect and limit |
| --- | --- |
| `approval_policy = "never"` | Suppresses command approval prompts; denied operations fail rather than gain authority. |
| `sandbox_mode = "danger-full-access"` | Removes Codex's local shell filesystem/network sandbox where permitted. OS/account/container/network and managed limits still apply. |
| `web_search = "live"` | Requests live native web search where the client provides it; does not provision tools or authenticate providers. |
| `apps._default.enabled`, `destructive_enabled`, `open_world_enabled` = `true` | Enables defaults for app tools and advertised destructive/open-world capabilities, subject to specific overrides and enforced policy. |
| `apps._default.default_tools_approval_mode = "approve"` | Automatically approves app tool prompts where supported; does not authorize the underlying task or establish an account connection. |
| `computer_use.default_app_access = "allow"` | Lets normal native-app approvals and policy checks continue. This is also the product default; it does **not** silently approve every app. |

Activation removes the root `default_permissions` selector so it cannot conflict
with `sandbox_mode`. It retains custom `[permissions.*]` definitions and all
unrelated settings. It preserves specific app/tool/server policy, enabled states,
allow/deny lists, and platform app rules; these can keep particular tools restricted.
The asset deliberately supplies neither machine-specific paths nor identities,
credentials, connection definitions, global MCP wildcards, or hook trust.

For existing, explicitly selected MCP server definitions, append these flags to
**both** preview and apply as needed:

```sh
uv run <skill-root>/scripts/codex_config.py preview --mcp-server SERVER_ID --plugin-server PLUGIN_KEY SERVER_ID
uv run <skill-root>/scripts/codex_config.py apply --mcp-server SERVER_ID --plugin-server PLUGIN_KEY SERVER_ID
```

Use actual configured table keys, including the marketplace suffix when present.
The helper sets only that server's `default_tools_approval_mode = "approve"` at
`mcp_servers.<id>` or `plugins.<plugin>.mcp_servers.<server>`. Missing definitions
fail before writing; per-tool overrides remain. For plugin servers configured only
through their manifest, add/review the documented plugin-scoped policy table in
user settings first; the helper does not invent a connection or enumerate private
config. `approve` does not approve MCP elicitation/authentication or expose disabled tools.

These defaults govern tool prompts. They never authorize sending communications,
merging, deployment, paid actions, or unrelated destructive operations. Follow the
task's actual authorization and all effective runtime, tool-specific, managed, and
OS restrictions. Do not try alternate tools or change permissions to evade a denial.

## Client, platform, and verification

Verified against installed **Codex CLI 0.162.0** and official documentation on
2026-10-31. The supported legacy `sandbox_mode` path avoids assuming beta permission
profiles on older clients. Older releases may reject newer app/native/MCP options;
verify/update the intended client rather than silently dropping unsupported settings.

After activation, start a new task and restart the relevant client/server if it
caches defaults. A running task, resume, pending approval, explicit task override,
selected profile file, or trusted project's config can retain different effective
permissions. Inspect effective task permissions in the client; where available,
use app-server `config/read` with origins and `configRequirements/read` to distinguish
stored defaults from applied policy. Do not expose the full config response because
it can contain connection details. A parsed file is not proof of a tool's execution.

| Execution host | Practical limits |
| --- | --- |
| macOS local | Shell remains under the OS user. Native apps need supported Computer Use tools plus OS Screen Recording/Accessibility consent and normal app approvals. |
| Linux local | Shell preset applies where the client supports it. This file does not install a desktop, browser, or native-app control capability. |
| Windows local | Shell runs under the Windows user; filesystem ACLs/UAC and network policy remain. Native app policy uses signed packaged AUMIDs or signed executable identity, not portable file paths. WSL uses its own Linux Codex home/runtime. |
| Remote host / hosted task / Work Cloud | Activate on the actual local execution host where supported. A local file cannot relax hosted/container/coordinator limits, managed requirements, client-owned tool policy, or account availability. |

Official sources: [configuration basics and precedence](https://learn.chatgpt.com/docs/config-file/config-basic),
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
[sandbox and approvals](https://learn.chatgpt.com/docs/agent-approvals-security),
[permissions](https://learn.chatgpt.com/docs/permissions), and
[plugin packaging and installed MCP policy](https://developers.openai.com/plugins/build/plugins).
