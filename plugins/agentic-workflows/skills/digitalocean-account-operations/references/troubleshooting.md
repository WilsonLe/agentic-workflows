# doctl troubleshooting runbook

Use this sequence when a command, flag, request, or response is unclear.

## Discover the command

```bash
doctl help
doctl <resource> --help
doctl <resource> <action> --help
doctl version
```

Use the help for the exact installed version. Do not invent a flag from memory or reuse a flag from
another resource group.

## Reproduce safely

1. Reduce the request to the smallest read-only command.
2. Prefer `--output json` to distinguish empty results from formatting problems.
3. Add `--verbose` for more context.
4. Use `--trace` only when necessary:

   ```bash
   doctl <read-only-command> --trace
   ```

Trace output can contain request metadata and sensitive identifiers. Capture it only in a temporary,
restricted location when needed; redact authorization material and secrets before showing or saving
it. Never run shell environment dumps as a credential check.

## Common failures

- **Command or flag not found:** read the exact action help and compare the installed version with
  current official documentation.
- **401:** confirm the variable exists, ensure the command uses the default context, check token
  status, then retry `doctl --context default account get --output json`.
- **403:** identify the missing scope or permission; do not broaden it without the user.
- **404:** re-list the resource and confirm account, region, and identifier.
- **409:** inspect resource state and recent actions before retrying.
- **429 or 5xx:** respect server guidance and documented retry flags for read-only calls. Do not
  blindly retry mutations.
- **Empty list:** verify filters, pagination, region, project, and formatting.

Report the command shape, CLI version, exit status, sanitized error, likely cause, and safest next
diagnostic. Do not report raw trace output unless it has been checked for secrets.
