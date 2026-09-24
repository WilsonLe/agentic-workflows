# Agentic Workflows configuration transfer onboarding

## Prerequisites

- A compatible `agentic-workflows` plugin installed in both sessions.
- `uv` available to run the helper and its pinned `cryptography` dependency.
- A supported local prompt:
  - macOS native masked dialog or interactive terminal;
  - Windows native masked PowerShell/.NET dialog or interactive terminal.
- Protected provider credentials already onboarded for anything that should be exported.

Never paste a passphrase or token into chat.

## First export

Ask:

> Export my Agentic Workflows config and credentials for another session on this Mac.

For another machine or Windows computer, ask:

> Export a portable Agentic Workflows config and credential file for another computer.

Portable export opens a local masked passphrase prompt twice. Store the passphrase separately from
the `.agenticx` file using the user's password manager.

## First import

Attach exactly one `.agenticx` file and ask:

> Import this Agentic Workflows config.

Portable import opens a local masked prompt. Local-session import uses the current user's OS
credential store. The helper shows only a sanitized preview, verifies all provider credentials
read-only, and either applies everything or restores the prior local configuration.

## Ready state

The workflow is ready when the helper runtime resolves, the selected local prompt works, a
synthetic export round trip authenticates, and provider wrappers are ready for any credentials the
user will import. A plugin being installed does not prove that a portable passphrase or local key
is available.
