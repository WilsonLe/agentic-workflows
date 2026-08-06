# WordPress DevOps onboarding

Use this guide for setup and first-run requests. Read
[target-and-ssh-contract.md](target-and-ssh-contract.md) first.

## Readiness inputs

Require the intended project/site, environment, exactly one provider
(`railway` or `digitalocean`), provider access through its approved account
workflow, an authorized SSH host alias/account or equivalent access path, and
the WordPress root or enough read-only access to discover it.

Do not ask for provider tokens, private keys, SSH passwords, database
credentials, salts, or secret variables in chat.

## Read-only first run

1. Verify the selected provider identity and resolve the exact resource.
2. Test SSH without changing the target.
3. Discover bare-metal or Docker Compose topology and the serving WordPress/
   PHP runtime.
4. Run `wp --info` through the selected runtime and read the minimum site
   context needed for the intended task.
5. Inspect source-of-truth repository, branch, revision, deployment adapter,
   filesystem ownership, mounts, and relevant plugin/theme state.
6. Report readiness, missing configuration, target fingerprint, and next safe
   action.

Do not update, install, activate, delete, backup, purge, chown, deploy, or
enable maintenance mode as an onboarding test.

## Ready state

`Ready` requires the intended provider target, successful read-only provider
identity, successful SSH, a responding target WP-CLI runtime, and a resolved
source-of-truth/rollback path for the planned mutation. Provider access alone
does not prove SSH or WordPress access.
