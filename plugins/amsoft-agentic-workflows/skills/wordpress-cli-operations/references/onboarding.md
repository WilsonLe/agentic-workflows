# WordPress CLI Operations onboarding

Use this guide for setup and first-run requests.

## Access contract

Require:

- the intended environment and site;
- an authorized SSH host alias or hostname and account;
- authentication already available through an SSH agent, keychain, or secret manager;
- the WordPress root, Compose directory, or enough read-only access to discover it;
- WP-CLI available in the runtime that currently serves WordPress.

Do not ask for private keys, SSH passwords, database passwords, salts, or hosting tokens in chat.
Do not copy credentials into plugin files, shell history, command arguments, logs, or reports.

## Read-only first run

1. Confirm the target is production, staging, or local.
2. Test the existing SSH connection without changing the server.
3. Discover whether WordPress is bare metal or containerized.
4. Identify the WordPress root or Compose project and the serving WordPress/PHP service.
5. Run `wp --info` through the selected runtime.
6. Read only the minimum site context needed for the planned task: core version, `home`, `siteurl`,
   multisite state, active theme, and relevant plugin status.
7. Report the connection, runtime adapter, WordPress context, permissions observed, missing
   prerequisites, and next safe action.

Do not update, activate, deactivate, install, delete, back up, purge caches, or enable maintenance
mode as an onboarding test.

## Ready state

Mark the skill `Ready` only when SSH succeeds, the correct WordPress runtime answers `wp --info`,
and a read-only WP-CLI request identifies the intended site. If Docker or WP-CLI exists but the
serving service, path, or site is unresolved, mark it `Needs input` or `Needs configuration`.

## Suggested first prompt

> Use WordPress CLI Operations to connect to my authorized server, discover whether WordPress is
> bare metal or Docker Compose, identify the correct WP-CLI runtime and site, and return a
> read-only inventory. Do not make changes.
