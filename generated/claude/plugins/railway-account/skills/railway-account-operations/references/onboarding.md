# Railway authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

## Project store

Apply [project-local controls](task-authority-and-secrets.md#project-local-cli-credentials)
before setup. Use a private input file outside Git and the existing installer;
do not substitute interactive login state for the required account token.
Command shapes (resolve and quote paths before execution):

```sh
python3 <plugin-root>/scripts/railway_configure_credentials.py <private-source> --destination <project-root>/.cli/railway/credentials.json --confirm-account-token I_CONFIRM_RAILWAY_ACCOUNT_TOKEN --verify
python3 <plugin-root>/scripts/railway_cli.py --credentials-file <project-root>/.cli/railway/credentials.json -- whoami --json
```

Use that `--credentials-file` on every command. The helper supplies
`RAILWAY_API_TOKEN` inside the child and clears conflicting Railway token variables.
The [official authentication reference](https://docs.railway.com/cli/login)
describes the CLI environment mechanism; retain the wrapper's narrower account-token
contract. Directory selection and local linking do not select this protected store.
Copy normalized records at `0400` into new worktrees, preserve source files, and
verify identity and workspace/project/environment/service there. Do not archive
or revoke the source worktree's token as part of copying.

## Authenticate and verify

1. Identify the intended account/project from task evidence and check the installed
   railway_cli.py wrapper using current help. Install missing tools from official instructions
   when authorized; do not treat a missing binary as an authenticated capability gap.
2. Check existing authentication read-only with wrapper whoami --json and exact workspace/project/environment/service reads. Reuse it only when the
   authenticated identity and target match. No browser visit or new token is needed
   when existing CLI authentication is valid.
3. If unauthenticated, expired, or mismatched, open https://railway.com/dashboard or the official CLI login
   URL in the built-in Codex browser. Verify the signed-in account and select the
   account/team/workspace for the current project. Resolve ambiguous identities.
4. Obtain an account token created with No workspace in Account Settings. Reuse existing task authority for needed setup, but do not
   rotate/revoke existing credentials, broaden access, or switch accounts silently.
5. Before key generation/reveal/Copy, validate a concealed transfer into the client's
   supported protected store/login mechanism. Never return secrets in tool arguments,
   output, DOM reads, screenshots, logs, process arguments, or Git. If private
   password/MFA/CAPTCHA entry or concealed transfer needs the user, identify that
   exact step and resume afterward. Never harvest browser cookies/storage/session.
6. Return to the CLI, verify authentication read-only, and resolve exact targets.
   A browser login or created key alone is not usable CLI authentication proof.
7. Report verified client/identity/scope and readiness without secrets. Perform
   requested work through supported authenticated commands. Onboarding does not
   create resources, change business/configuration settings, or deploy as a test.

Browser service operations are fallback only for a documented capability missing
from the authenticated client. Authentication failures must be repaired first;
permission denials cannot be bypassed through another account/channel. If secure
setup is unavailable, finish independent work and report the concrete blocker.

Read [credential contract](credential-contract.md) for exact type/storage/verification controls.
