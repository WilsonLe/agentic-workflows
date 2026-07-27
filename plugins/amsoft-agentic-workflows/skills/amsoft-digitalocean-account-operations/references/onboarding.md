# DigitalOcean Account onboarding

Use this guide for setup, onboarding, and first-run requests.

## Prerequisites

- A current `doctl` installation.
- A user-provided DigitalOcean API access token available as
  `DIGITALOCEAN_ACCESS_TOKEN` in the environment that launches Codex.

Do not ask the user to paste the token into chat. Do not put it in source files, committed `.env`
files, shell history, command arguments, or diagnostic output. If the token is not yet available to
the process, ask the user to configure it through their normal secret manager or secure launcher,
restart Codex, and open a new task.

## First-run workflow

1. Check the CLI:

   ```bash
   doctl version
   ```

2. Check only whether the variable exists; never print its value.
3. Verify read-only account access:

   ```bash
   doctl --context default account get --output json
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
selected. Every mutation still requires explicit approval for the exact target and command.

## Suggested first prompt

> Onboard me to DigitalOcean Account. Verify doctl and the configured token, identify the account,
> and inventory only the resources needed for my task. Do not make any changes.
