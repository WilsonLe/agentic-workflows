# Railway variables and secrets

Railway variables can contain credentials and private configuration. Treat all
variable values as secrets unless proven otherwise.

## Inspect

Do not run or report `railway variable list` directly: ordinary values may be
returned in plaintext. Use the launcher names-only operation:

```text
python3 <plugin-root>/scripts/railway_cli.py -- variable-names \
  --service <service> --environment <environment>
```

This captures JSON internally and emits sorted keys only. It fails closed when
the installed CLI returns an unknown shape. Do not use `--kv`, shell tracing,
environment dumps, `railway run`, or `railway shell` for inventory.

Railway sealed variables are intentionally unretrievable, but that does not
make ordinary variables safe to display. Report names and metadata only.

## Change

1. Resolve the exact service and environment.
2. Confirm whether the variable already exists by name.
3. Obtain the new value through the user's approved secret manager or concealed
   input path, never chat or a literal command argument.
4. Inspect `railway variable set --help` for stdin support in the installed
   version.
5. State whether the change stages or triggers a deployment and whether
   `--skip-deploys` is intended.
6. Reuse authority covering the write and production target as applicable; apply
   [task authority and concealed secrets](task-authority-and-secrets.md).
7. Set from stdin or another non-argv secret channel.
8. Verify only presence and resulting deployment/health; never read back or
   print the value.

The launcher refuses `KEY=VALUE`, template-variable flags, and `--2fa-code`
arguments because they would place secret material in the process argument
list.

Deletion is destructive. Require the exact key, service, environment, impact,
rollback source, and authority covering both the write and destructive effect.
Reuse an existing request that already covers them.
