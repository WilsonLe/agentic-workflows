---
name: agentic-workflows-config-transfer
description: Use when the user asks to start a Codex session using saved TOML defaults, preserve session configuration, export, back up, transfer, migrate, restore, or import Agentic Workflows configuration, or enable portable full-access Codex defaults. Launch user sessions without permission overrides; transfer allowlisted preferences and supported credentials through an encrypted .agenticx file; explicitly activate the bundled Codex config.toml with backup and restore.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer before running the bundled helper scripts.
- **Required: Codex local configuration** — Use a supported Codex installation with local preference files and access to the protected credential store.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Agentic Workflows Config Transfer

For new Codex work sessions, follow [inherit-config launches](references/codex-configuration.md#start-sessions-with-the-saved-configuration).
Use the intended host's existing configuration without injecting permission selectors
or ignoring user config. Prefer native Codex CLI when a desktop task tool forces a
different profile, and read back the new session's effective permissions. Do not
activate the bundled preset merely to start a session or resolve a mismatch.

For full-access Codex configuration, read [Codex activation](references/codex-configuration.md).
The installed asset is [templates/codex/config.toml](templates/codex/config.toml),
relative to this skill. Installation only distributes it; activation is opt-in.
Never apply it merely because a task encounters a permission denial. A direct request
to activate these defaults authorizes the reversible local update, subject to effective
runtime permissions. Configuration does not grant task authority or bypass managed
policy, tool restrictions, OS consent, or communications/merge/deployment approvals.

Use the bundled transfer helper to export or import one authenticated-encrypted `.agenticx` file.
Read [references/transfer-contract.md](references/transfer-contract.md) before every operation. For
first use, prompt behavior, or runtime setup, also read
[references/onboarding.md](references/onboarding.md).

## Export

When the user asks simply to export configuration, use `local-session` mode. It includes
allowlisted workflow preferences and every configured supported provider credential. It is intended
for another central-plugin session running as the same OS user on the same machine.

Run from this skill's plugin root:

```bash
uv run <plugin-root>/scripts/agentic_workflow_config_transfer.py export \
  --mode local-session \
  --output /user/selected/path/agentic-workflows-transfer-YYYYMMDD-HHMMSS.agenticx
```

When the user says the file is for another machine or operating system, use
`portable-passphrase`. The helper opens a masked local prompt twice. Never ask for or accept the
passphrase in chat.

```bash
uv run <plugin-root>/scripts/agentic_workflow_config_transfer.py export \
  --mode portable-passphrase \
  --output /user/selected/path/agentic-workflows-transfer-YYYYMMDD-HHMMSS.agenticx
```

Return the generated file and list only the included provider names. Warn that the encrypted file
is a sensitive credential backup. Never inspect or expose its decrypted payload.

## Import

When the user attaches exactly one `.agenticx` file and directly asks to import config:

1. Resolve the attachment to a local path without copying it into Git.
2. Run the helper. Portable files open a masked local prompt; local-session files retrieve the
   current OS user's local key.
3. Review only the sanitized preview containing preference field names, provider names, token
   types, and replacement decisions.
4. The direct import request authorizes this reversible local configuration update. It does not
   authorize provider resource writes.
5. Let the helper stage all preferences and credentials, verify every credential read-only, and
   commit only if all providers succeed.
6. Report the sanitized result or rollback. Preserve the attached transfer file.

```bash
uv run <plugin-root>/scripts/agentic_workflow_config_transfer.py import \
  /resolved/attachment/agentic-workflows-transfer.agenticx
```

## Non-negotiable boundaries

- Never request, display, log, hash, prefix, measure, or copy a credential into chat.
- Never decrypt an export for inspection or use a general JSON tool on its secret payload.
- Never use `--passphrase-stdin` in an agent-driven command. It exists only for isolated automated
  testing and a user-controlled local terminal.
- Never use a local-session file on another machine by embedding, exporting, or copying the local
  key. Re-export in portable mode.
- Never add unsupported providers or fields without a schema/version change and review.
- Never treat import as approval to deploy, mutate DNS/resources, rotate tokens, or weaken another
  skill's approval gates.
- Never delete or relocate an attachment after import unless the user explicitly asks.

Credentials imported by this skill grant the same provider access as their originals. Apply each
provider skill's operational approvals after import.
