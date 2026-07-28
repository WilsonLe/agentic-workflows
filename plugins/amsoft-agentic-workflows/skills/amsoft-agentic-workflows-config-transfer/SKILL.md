---
name: amsoft-agentic-workflows-config-transfer
description: Export and import AMSoft Agentic Workflows preferences and supported Railway, Cloudflare, and DigitalOcean credentials through one authenticated-encrypted .amsoftx file. Use when the user asks to export, back up, transfer, migrate, restore, or import agentic workflow configuration, including drag-and-drop import across Codex sessions, macOS, and Windows.
---

# AMSoft Agentic Workflows Config Transfer

Use the bundled transfer helper to export or import one authenticated-encrypted `.amsoftx` file.
Read [references/transfer-contract.md](references/transfer-contract.md) before every operation. For
first use, prompt behavior, or runtime setup, also read
[references/onboarding.md](references/onboarding.md).

## Export

When the user asks simply to export configuration, use `local-session` mode. It includes
allowlisted workflow preferences and every configured supported provider credential. It is intended
for another central-plugin session running as the same OS user on the same machine.

Run from this skill's plugin root:

```bash
uv run scripts/agentic_workflow_config_transfer.py export \
  --mode local-session \
  --output /user/selected/path/amsoft-agentic-workflows-transfer-YYYYMMDD-HHMMSS.amsoftx
```

When the user says the file is for another machine or operating system, use
`portable-passphrase`. The helper opens a masked local prompt twice. Never ask for or accept the
passphrase in chat.

```bash
uv run scripts/agentic_workflow_config_transfer.py export \
  --mode portable-passphrase \
  --output /user/selected/path/amsoft-agentic-workflows-transfer-YYYYMMDD-HHMMSS.amsoftx
```

Return the generated file and list only the included provider names. Warn that the encrypted file
is a sensitive credential backup. Never inspect or expose its decrypted payload.

## Import

When the user attaches exactly one `.amsoftx` file and directly asks to import config:

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
uv run scripts/agentic_workflow_config_transfer.py import \
  /resolved/attachment/amsoft-agentic-workflows-transfer.amsoftx
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
