# Railway Account onboarding

## Prerequisites

- Railway CLI installed.
- A downloaded account token created with **No workspace**.
- The local path to that file.

Do not accept a token value in chat. Do not use a Railway mutation as an
authentication test.

## First run

1. Read `credential-contract.md`.
2. Run `railway --version`.
3. Confirm the user states that the token was created with **No workspace**.
4. Install it without displaying content:

   ```text
   python3 <plugin-root>/scripts/railway_configure_credentials.py <selected-path> \
     --confirm-account-token I_CONFIRM_RAILWAY_ACCOUNT_TOKEN \
     --verify --archive-source
   ```

   If a protected credential already exists, inspect only its owner and mode.
   Use `--replace` only after confirming the exact destination and source.

5. If onboarding did not use `--verify`, verify identity read-only:

   ```text
   python3 <plugin-root>/scripts/railway_cli.py -- whoami --json
   ```

6. List projects only when needed for the user's intended task:

   ```text
   python3 <plugin-root>/scripts/railway_cli.py -- list --json
   ```

7. Report the CLI version, credential type, authenticated identity, visible
   account context, required permissions, and next safe action. Minimize
   personal data in the report.

Do not link a directory, create a project, deploy, set a variable, generate a
domain, restart a service, or make any other change during onboarding.

## Readiness

- `Ready`: protected credential checks pass, the user confirmed **No
  workspace**, `whoami --json` returns the intended account, and the minimum
  targets needed for the planned task are readable.
- `Needs input`: token path, creation confirmation, or intended target is
  missing.
- `Needs configuration`: CLI missing, credential permissions invalid, or the
  protected credential is absent.
- `Blocked`: authentication fails, the account is wrong, or required access is
  denied.

## Suggested prompt

> Use Railway Account Operations to onboard my downloaded account token
> read-only. Ask only for its local path, verify the account, and do not change
> Railway.
