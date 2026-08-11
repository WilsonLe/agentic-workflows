# WordPress DevOps target and SSH contract

This contract identifies the infrastructure target without storing provider
tokens, private keys, passwords, database credentials, or secret variables.

## Provider contract

Select exactly one provider for a task:

- **Railway:** use the approved Railway account workflow to resolve the exact
  project, environment, service, deployment, and volume. An account token is
  accepted only through its protected local contract; never use a project
  token as if it were an account credential.
- **DigitalOcean:** use the approved DigitalOcean account workflow to resolve
  the exact account, Droplet, project, network, volume, or load balancer. Keep
  the access-token reference outside the WordPress contract.

The provider credential proves provider identity and target resolution. It is
not a WordPress Application Password and does not by itself authorize an SSH
command.

## SSH contract

Require an existing host alias or fully resolved hostname, account, port if
non-default, environment, and an SSH agent, OS keychain, or approved secret
manager that supplies authentication locally. Record the access source as a
reference only. Never copy private keys, passwords, or agent material into a
repository, contract, command argument, log, or chat.

The SSH path must be tested read-only against the exact target before WP-CLI
discovery. A successful connection to a host does not prove that it contains
the intended WordPress site.

## Reusable/project-specific shape

```json
{
  "schema_version": 1,
  "contract_kind": "wordpress-devops-target",
  "plugin": "wordpress-devops",
  "project_key": "example-project",
  "site_key": "example-site",
  "environment": "staging",
  "provider": "railway",
  "provider_target": {
    "project": "example-project",
    "environment": "staging",
    "service": "wordpress",
    "volume": "wordpress-data"
  },
  "provider_credential_ref": "amsoft/railway/account",
  "ssh": {
    "host_alias": "example-wordpress",
    "user": "deploy",
    "auth_source": "ssh-agent"
  },
  "wordpress_root": "discovered-at-read-only-onboarding",
  "source_of_truth": {
    "repository": "anhminhsoft/example-site-infrastructure",
    "path": "infra/wordpress",
    "branch": "main"
  },
  "last_verified_at": "2026-08-05T00:00:00Z"
}
```

Validate synthetic records with
`<plugin-root>/schemas/devops-target-contract-v1.schema.json`. A project-specific contract
may narrow the provider target, SSH reference, WordPress root, source path,
allowed operations, and rollback identity. It may not copy secret values.

## Invalid or stale state

Mark the contract `Needs input` if provider, environment, target, SSH alias,
source of truth, or rollback path is missing. Mark it `Blocked` if provider or
SSH identity is wrong, the site cannot be fingerprinted, the runtime is not
the selected environment, the mount is unexpected, or source/deployed drift
cannot be reconciled. Do not guess a hostname, volume, container, path, or
provider resource.
