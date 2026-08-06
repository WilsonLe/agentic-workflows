# WordPress filesystem and plugin management

Use this runbook for wp-admin FTP prompts, `Could not access filesystem`,
plugin/theme lifecycle, update failures, or writable-volume diagnosis.

## Read-only probe

Resolve the exact site, WordPress root, serving service, PHP-FPM/Apache
runtime user, and mounted paths first. Run the probe as the same numeric UID/GID
used by PHP; a root-only probe is not sufficient. Capture only IDs, owners,
modes, mount type, writable state, and filesystem method.

For every update context in scope, check the WordPress content/plugin/theme
path, core path, temporary path, and `get_filesystem_method()` as the serving
user. `direct` is required when the approved deployment contract expects PHP
to update files directly. Setting `FS_METHOD=direct` does not repair a failed
write probe.

## Plugin/theme lifecycle

Before install, update, activate, deactivate, or delete:

1. identify the exact package/source, version, dependencies, target site, and
   environment;
2. check the versioned deployment/source-of-truth representation and planned
   rollback;
3. create the required database/file or hosting snapshot;
4. obtain the mutation approval for the exact target;
5. perform the supported release operation; and
6. read back plugin/theme status, PHP/bootstrap health, logs, and the affected
   public/admin behavior.

Never use the built-in Plugin/Theme File Editor, an unbounded wildcard, a
guessed ZIP, or `0777`. Do not collect FTP credentials to conceal ownership
or mount problems.

## Ownership remediation

The durable fix is usually to align the PHP runtime UID/GID with the exact
writable volume path through the reviewed image, entrypoint, Compose, or
provider deployment source. A Docker Compose repair must use the discovered
service, numeric IDs, and exact path; a Railway repair must preserve the
volume and use the reviewed startup/deployment contract. Never chown a broad
host directory, detach/delete a volume, or change a read-only source mount.

Filesystem ownership/mode changes are production mutations. Require a current
database backup, exact ownership/mode manifest, deployment/volume identity,
approval, source reconciliation, commit, and rollback path before changing
them.

## IaC drift rule

A remote WP-CLI or provider action is a diagnostic or release step, not the
source of truth. If an emergency action is explicitly authorized, record its
exact target and result as drift, then encode the durable fix in the versioned
infrastructure source and commit it before completion. Content changes remain
outside this DevOps contract.
