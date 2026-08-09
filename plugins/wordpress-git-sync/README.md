# WordPress Git Sync

WordPress Git Sync is the executable adapter behind AMSoft's content-as-code
contract. It does not mirror a WordPress database. It synchronizes only
explicitly enrolled objects and fields through stable logical identities,
deterministic canonical JSON, environment-specific locks, and an atomic
compare-and-swap runtime.

The package contains:

- `scripts/wp_content_sync.py`: pull, status, diff, plan, guarded apply,
  inventory, baseline, migration waves/checkpoints, code-export validation,
  and GitHub automation planning;
- `runtime/amsoft-wordpress-git-sync`: the WordPress registry, REST readback,
  row-lock CAS apply, idempotency journal, and save-event queue;
- schemas and synthetic fixtures for objects, projects, locks, media,
  migration state, and automation events; and
- `$wordpress-git-sync-management`: ownership, migration, rollback, automation,
  and operator runbooks.

Git owns executable themes/plugins/registered blocks. WordPress is an editable
peer only for enrolled database entities. Git versions media manifests rather
than unbounded binaries. Private/draft payloads, credentials, cookies, nonces,
signed URLs, and protected metadata are excluded from Git artifacts.

## Safe first use

Start with `validate`, `inventory`, `status`, `diff`, and `plan`. `apply` is a
dry run unless `--execute` is present, and execution additionally requires the
reviewed lock values, `--require-atomic-check`, an idempotency key, and a
bounded approval identifier. A real site requires the runtime plugin and a
secret-free WordPress Application Password reference; fixture projects use no
credential.

No command commits, pushes, opens a pull request, deploys, publishes, purges,
or changes a provider by itself.
