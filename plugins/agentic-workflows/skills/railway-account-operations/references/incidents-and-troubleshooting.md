# Railway incidents and troubleshooting

## Safe diagnosis

1. Confirm account, workspace, project, environment, service, and incident
   window.
2. Separate read-only investigation from mitigation authority.
3. Run `railway --version`, then the exact command help when safe.
4. Reduce failures to bounded structured reads.
5. Inspect deployment status and bounded logs only after passing
   `--confirm-sensitive-output I_APPROVE_RAILWAY_SENSITIVE_READ`; sanitize
   application secrets and personal data before reporting.
6. Check Railway's current status and official documentation when service or
   CLI behavior may have changed.

Do not use shell tracing, environment dumps, raw authorization headers, or
unbounded log streams. The launcher redacts the account token but cannot know
every application secret that may appear in logs.

## Known CLI behavior boundary

On Railway CLI `4.29.0`, `railway scale --help` was observed contacting Railway
and panicking on a GraphQL field error. Therefore:

- do not assume help is purely local;
- capture sanitized errors;
- do not retry a mutation because help or discovery failed;
- compare installed behavior with current official documentation.

## Common failures

- Authentication failure: confirm protected credential owner/mode, account-token
  creation with **No workspace**, absence of `RAILWAY_TOKEN`, then retry
  `whoami --json` once.
- Authorization failure: stop and report the denied action; do not switch to a
  different credential class.
- Wrong or missing link: inspect current directory status and follow
  `target-resolution.md`.
- Unknown command or flag: use exact installed help and official docs; do not
  borrow flags from another command.
- Rate limit or transient 5xx: respect server guidance; retry reads with bounded
  backoff, never blindly retry writes.
- Unknown write outcome: read current state before any retry.

## Incident mitigation

Present evidence, hypothesis, blast radius, smallest reversible mitigation,
validation, and rollback. Require explicit approval unless the user already
authorized that exact emergency action. Apply one change at a time and stop
when stable or when the next action broadens authority.
