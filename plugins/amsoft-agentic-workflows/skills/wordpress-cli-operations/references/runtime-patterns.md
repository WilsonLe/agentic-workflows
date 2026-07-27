# WordPress WP-CLI runtime patterns

Choose a pattern only after discovering the target.

## Bare metal

Run WP-CLI as the operating-system user that owns or normally administers the WordPress files.
Change to the WordPress root or pass `--path`. Confirm that the PHP binary used by WP-CLI is
compatible with the serving runtime.

Conceptual adapter:

```text
ssh <target> -- 'cd <wordpress-root> && wp <command> --format=json'
```

## Docker Compose

Work from the discovered Compose project. Confirm the running service with `docker compose ps` and
inspect its command or image before assuming where WordPress is mounted. Use `-T` for
non-interactive execution.

Conceptual adapters:

```text
ssh <target> -- 'cd <compose-dir> && docker compose exec -T <service> wp <command>'
ssh <target> -- 'cd <compose-dir> && docker compose run --rm <wp-cli-service> wp <command>'
```

Use the existing service pattern. Do not introduce a new one during diagnosis.

## Direct container execution

Use `docker exec` only when the exact serving or CLI container has been identified and Compose is
not the management surface. Container names and IDs are runtime state; rediscover them rather than
storing them in the skill.

## Multisite

Read `wp core is-installed --network` and the site list before site-scoped work. Require the exact
site URL and add `--url=<site-url>`. Network activation and individual-site activation are
different operations; preserve the observed scope.

## Managed hosting

Prefer the host's supported SSH/WP-CLI entrypoint and snapshot mechanism. Do not bypass a hosting
wrapper, immutable release path, or deployment workflow merely because a lower-level shell is
available.
