# Railway account-token contract

## Accepted credential

Accept only a Railway **account token** created from Account Settings with
**No workspace** selected. Railway documents this as its broadest token class:
it can perform actions across every resource and workspace the account is
authorized to access.

Use it only as `RAILWAY_API_TOKEN`. Reject:

- project tokens and `RAILWAY_TOKEN`;
- workspace tokens, even though the CLI also maps them to
  `RAILWAY_API_TOKEN`;
- OAuth tokens;
- interactive `railway login` state;
- an unknown token whose class the user cannot confirm.

Token strings do not identify their class reliably. Require the user to confirm
how the token was created; never infer it from its characters.

## Input and storage

Ask only for a local file path. Never ask the user to paste or dictate a token.
The installer accepts:

- one non-empty, single-line plaintext token; or
- JSON containing exactly `{"token_type": "account", "token": "..."}`.

Require the non-secret confirmation phrase
`I_CONFIRM_RAILWAY_ACCOUNT_TOKEN`. Install a normalized JSON record at
`~/.config/amsoft/railway/credentials.json`, with directory mode `0700` and
file mode `0400`. Verification failure preserves the source. When the user has
explicitly authorized relocation, `--verify --archive-source` moves the exact
successfully verified source into
`~/.config/amsoft/railway/imported-sources/` with protected modes. Name
collisions fail closed.

Never store a token in this plugin, Git, a committed `.env`, shell history,
command arguments, logs, screenshots, issue text, PR text, or evidence.

## Execution

Use the bundled launcher. It:

- validates current-user ownership and exact protected modes;
- accepts only `token_type: account`;
- removes inherited `RAILWAY_TOKEN` and `RAILWAY_API_TOKEN`;
- sets only `RAILWAY_API_TOKEN` in the Railway subprocess;
- executes without a shell;
- redacts the exact token from captured stdout and stderr.

The launcher cannot prove the dashboard token type from the token string. The
read-only `railway whoami --json` check proves account identity, not how the
token was created. Keep the user's creation confirmation as part of readiness.

## Rotation and removal

Token rotation and revocation are consequential account-security actions.
Require explicit approval, install the replacement atomically, verify it
read-only, and revoke the old token through the user's authorized Railway
surface only after the replacement succeeds. Remove the protected local copy
only on an explicit request targeting that exact path.

The central encrypted config-transfer skill may export and import this account
token inside an authenticated-encrypted `.amsoftx` payload. It never changes
the account-token-only rule. Imported credentials must pass `whoami --json`
read-only before the local transaction commits.
