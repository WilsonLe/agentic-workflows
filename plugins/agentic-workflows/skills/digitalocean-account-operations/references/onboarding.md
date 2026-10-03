# DigitalOcean Account onboarding

Use this guide for setup, onboarding, and first-run requests.

## Prerequisites

- A current `doctl` installation.
- An authorized DigitalOcean API access token in a private local file.

For authorized setup, the agent can create and securely transfer the token using
[task authority and concealed secrets](../../agentic-workflows/references/task-authority-and-secrets.md).
Keep the existing installer's protected file contract; do not claim it uses Keychain.

Do not ask the user to paste the token into chat. Do not put it in committed files, shell history,
command arguments, or diagnostic output.

## First-run workflow

1. Check the CLI:

   ```bash
   doctl version
   ```

2. Install from the selected private file with `digitalocean_configure_credentials.py`. If a doctl
   YAML source is also supplied, the helper checks only that its `access-token` matches and never
   imports command defaults.
3. Add `--verify --archive-source` to verify read-only account access and archive the exact
   successful source or matching pair:

   ```bash
   python3 <plugin-root>/scripts/digitalocean_cli.py -- \
     --context default account get --output json
   ```

4. If needed, discover available top-level commands:

   ```bash
   doctl help
   ```

5. Run only the smallest read-only inventory needed for the user's planned task.
6. Report CLI availability, credential health, visible account context, required permissions, and
   any restart or configuration requirement.

Do not create, update, delete, reboot, resize, deploy, or assign anything as an onboarding test.

## Ready state

The plugin is ready when `doctl --context default account get --output json` succeeds with the
intended account and the token can read the resources required for the planned task. The default
context is intentional: the environment token is ignored when a non-default stored context is
selected. Every mutation needs authority covering its target and effect; reuse the setup or change request rather than asking for each command.

## Suggested first prompt

> Onboard me to DigitalOcean Account. Verify doctl and the configured token, identify the account,
> and inventory only the resources needed for my task. Do not make any changes.
