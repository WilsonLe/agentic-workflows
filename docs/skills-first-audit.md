# Skills-first distribution audit

Current scope: the maintained Codex suite after the 2026-11-11 scope reduction.
The [catalog](../catalog/plugins-v2.yaml) owns skill membership, prerequisites and
executable registration. The generated [capability map](../plugins/agentic-workflows/CAPABILITIES.md)
is the complete installed workflow inventory. Use those owners rather than
maintaining a second list of skills or helper paths here.

## Responsibilities and activation

- Ordinary features load as skills through native Codex discovery. The router
  selects the workflow and its prerequisites; it adds no prompt-routing hook.
- Task helpers validate or transform explicit task inputs, protect credentials,
  render media, or maintain workflow evidence. They run under the selected skill's
  authority and contracts, not simply because the plugin is installed.
- The automatic-title hook remains the sole automatic behavior exception. Its
  native registration and background worker retain title protection and privacy
  rules. See the [title policy](../plugins/agentic-workflows/skills/agentic-workflows/references/session-title-policy.md).
- Delegation owns native task/session lifecycle. Configuration transfer owns
  encrypted export/import and opt-in local activation, backup and restore. An
  independent Git session uses an isolated worktree by default; verify actual
  directory, configuration and required tools before dependent work.
- Installation distributes configuration assets without activating them. Provider
  access, external writes and paid actions retain task-specific authority.

## Distribution and verification

The existing generator materializes the complete Codex suite and marketplace.
It preserves executable modes and excludes transient runtime caches. Catalog and
package validation reconcile skill directories, executable registration, metadata,
links, prerequisites, capabilities and the staged file tree. Retired workflows
have no maintained skill trees, helper registrations or companion handoffs.

Templates and schemas remain task inputs. Media artwork, record fixtures,
research examples and upstream notices do not register background integrations.
Repository generators, validators and tests stay outside the installed package.
See [Codex development and release checks](harnesses.md#development-checks) and
[ADR-0015](adr/0015-support-codex-only-and-use-the-connected-vercel-app.md).

Static checks establish package integrity. Fresh Codex sessions, real tool
operations and target readbacks supply separate behavior evidence. Keep those
limits explicit and preserve private ledgers, credentials, user configuration
and unrelated plugin state during updates.
