# WordPress filesystem ownership and update prompts

Use this runbook when wp-admin asks for FTP/SSH credentials, reports
`Could not access filesystem`, or WordPress chooses `ftpext`, `ftpsockets`, or
`ssh2` instead of `direct` for updates.

The warning is normally a runtime ownership problem, not a missing FTP
credential. WordPress tests a context directory by creating and removing a
temporary file and, by default, also checks whether the new file has the same
owner as the WordPress files. The filesystem method is therefore determined by
the PHP process and the actual mounted files, not by the administrator role.
Do not collect or invent FTP credentials to work around a host that should use
direct writes.

## Required read-only probe

Resolve the exact production target, WordPress root, serving service, PHP user,
and writable mounts first. Run the probe as the same numeric UID/GID used by
PHP-FPM or Apache; a probe executed as container root is not sufficient.

Capture only ownership, modes, numeric IDs, mount paths, and the filesystem
method. Never print `wp-config.php`, environment variables, database settings,
tokens, or command output containing credentials.

For a bare-metal installation, use the discovered PHP runtime and WordPress
root. For Docker Compose, use the exact discovered service and a non-interactive
exec. A conceptual PHP probe is:

```text
require <wordpress-root>/wp-load.php;
require ABSPATH . 'wp-admin/includes/file.php';
echo get_filesystem_method([], <context>, false);
```

Probe at least the following contexts when core updates are in scope:

- `WP_CONTENT_DIR` or the exact plugin/theme update directory;
- `ABSPATH` or the exact core directory; and
- the temporary directory used by the discovered update path.

Record the observed PHP UID/GID, owner UID/GID for the context and a newly
created probe file, mode bits, `is_writable()` results, filesystem method, and
whether the path is a named volume, bind mount, read-only mount, or immutable
release path. The result must be attributable to one exact site and
environment.

`get_filesystem_method()` can return `direct`, `ssh2`, `ftpext`, or
`ftpsockets`. A non-`direct` result is an acceptance failure for a site whose
approved deployment contract expects PHP to update files directly. Defining
`FS_METHOD` as `direct` does not repair a non-writable or mismatched mount; do
not add that constant until the same-user probe succeeds.

## Remediation decision

Choose the smallest fix owned by the deployment layer:

| Observed cause | Correct boundary | Do not do |
| --- | --- | --- |
| Persistent Docker volume contains root- or migration-user-owned WordPress files while PHP runs as `www-data` | Take the required backup, then repair ownership on the exact writable volume path from the serving container or the reviewed deployment playbook | Do not chmod the site to `0777`, edit core files, or chown a broad host directory |
| A bind-mounted theme, mu-plugin, or release directory is read-only by design | Keep that mount read-only and update it through its versioned source/deployment workflow; repair only the writable core/plugin/upload paths | Do not make a source-controlled or security-sensitive bind mount writable from wp-admin |
| Railway volume is mounted at the WordPress root | Preserve the volume and use a reviewed image/entrypoint or one-time, narrowly bounded provider command that runs as root and chowns only the exact mounted WordPress path to the PHP UID/GID | Do not detach, delete, recreate, or resize the volume as a filesystem fix; do not use an unbounded interactive shell through the provider credential wrapper |
| Managed hosting uses an immutable release or host wrapper | Use the host's supported deployment or ownership repair mechanism | Do not bypass the release workflow with a guessed SSH path |
| PHP and WordPress files already share the owner but the method is non-direct | Inspect `FS_METHOD`, filters, PHP restrictions, and the tested context before changing configuration | Do not force `FS_METHOD` to hide an unresolved runtime failure |

For a Docker Compose VPS, the shape of an approved repair is:

```text
docker compose exec -T -u root <wordpress-service> chown -R <php-uid>:<php-gid> <exact-writable-wordpress-path>
```

Use the exact service, UID/GID, and path discovered immediately before the
write. If the service has read-only bind mounts under that path, split the
repair into explicit writable directories and files rather than traversing the
mount blindly. On the common WordPress images, `www-data` is often `33:33`,
but never assume that value without reading the running container.

For Railway, the normal durable fix is to make the container startup contract
establish ownership on the mounted volume before Apache/PHP serves requests,
or to deploy an image whose writable path is already owned by the runtime user.
If a one-time provider command is required, it must be an exact, non-secret
filesystem probe or ownership repair against the resolved service, environment,
volume mount, and deployment. The Railway account skill's general `shell` and
`ssh` surfaces remain blocked by default; a future provider-specific adapter
must keep the command narrow and preserve the account-token, target, and
production approval gates.

## Backup and change boundary

Before ownership or permission changes on production, capture:

1. a current database backup;
2. the exact changed file tree or hosting snapshot when the deployment supports
   one;
3. a secret-free ownership/mode manifest for the exact target paths; and
4. the current deployment revision, Compose project/service, volume identity,
   and PHP UID/GID.

Ownership repair is a production filesystem mutation and requires explicit
approval immediately before execution. It is not a plugin update, core update,
database migration, cache purge, or permission to edit content. Do not combine
it with unrelated updates.

Rollback restores the captured owner/group and mode for the exact paths, or
reverts the reviewed image/entrypoint/deployment revision. Do not restore a
whole WordPress volume merely because an ownership repair failed.

## Verification after remediation

Run the same probe as the PHP UID/GID and require:

- the expected owner UID/GID on the writable WordPress paths;
- a successful temporary write/remove test by that same runtime user;
- `get_filesystem_method()` returning `direct` for every required context;
- normal WordPress bootstrap, active plugin/theme inventory, and health checks;
- the intended admin update surface no longer requesting FTP credentials; and
- logged-out public health and critical journeys still working.

Read back the exact service, container/deployment, mount, and ownership state.
An HTTP 200, a successful root-only probe, a WP-CLI exit code, or a visible
admin page alone does not prove that PHP can perform updates directly.

## Security and failure handling

- Never request, store, or paste FTP passwords, SSH passwords, private keys,
  application passwords, or provider tokens.
- Never use `0777`, disable TLS, edit the built-in Theme/Plugin File Editor, or
  modify WordPress core source as a repair.
- Stop on a read-only mount, unexpected UID/GID, changed deployment, changed
  volume identity, missing backup, or any path that is broader than the
  approved envelope.
- If the method remains non-direct after ownership is correct, classify the
  failure as configuration, PHP restriction, deployment topology, or plugin
  filter and re-plan that narrower cause; do not blindly add credentials.
