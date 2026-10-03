# Railway target resolution

Resolve targets before proposing commands.

## Directory context

1. Resolve the exact local project directory.
2. Inspect `.railway/` or other CLI link state without displaying credentials.
3. Run `status --json` through the launcher from that directory.
4. Record workspace, project, environment, and service names and IDs returned
   by Railway.
5. Compare them with the user's intended target.

`railway link` and `unlink` modify local context and can redirect later
commands. Present the directory, current link, proposed link, and validation,
then match the change to existing task authority. A required in-scope link does
not need another confirmation; apply `task-authority-and-secrets.md`.

## Explicit targets

Prefer supported explicit `--project`, `--environment`, and `--service` flags
for consequential commands. Verify exact flags with the installed command help;
they are not uniform across commands.

Names are human-readable but can collide or change. Preserve IDs from
structured output and read back both name and ID before a write.

## Production classification

Do not classify production only by a name. Use all available evidence:

- environment name and ID;
- active domains and traffic;
- service role and current deployment;
- repository/deployment documentation;
- the user's explicit confirmation.

If production status is unclear, classify the target as production. Pass
`--target-class production` to the launcher only after separate production
authority covering that environment and effect. Reuse an explicit deployment or
change request that already provides it.

## Stale state

Immediately before a write, read the target again. Stop if the link, workspace,
project, environment, service, current deployment, or relevant configuration
changed unexpectedly. Do not overwrite another operator's work from stale
state.
