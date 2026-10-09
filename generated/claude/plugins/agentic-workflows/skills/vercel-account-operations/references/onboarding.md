# Vercel authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

## Project credential location

Apply [project-local credential controls](task-authority-and-secrets.md#project-local-cli-credentials)
first. Resolve the current checkout's absolute root, ignore `/.cli/`, and prepare
`.cli/vercel/` with owner-only permissions. Use the documented
[`--global-config`](https://vercel.com/docs/cli/global-options#global-config)
option on **every** invocation, including login, whoami, inventory, and writes:

```sh
VERCEL_TOKEN_STORAGE=file vercel --global-config <absolute-project-root>/.cli/vercel login
VERCEL_TOKEN_STORAGE=file vercel --global-config <absolute-project-root>/.cli/vercel whoami
VERCEL_TOKEN_STORAGE=file vercel --global-config <absolute-project-root>/.cli/vercel teams list
```

These are command shapes; substitute and quote the resolved path before execution.
Select the **file** credential backend explicitly: set the non-secret
`credStorage` field to `"file"` in the destination `.cli/vercel/config.json`,
preserving its other fields, and set `VERCEL_TOKEN_STORAGE=file` only for each
CLI child process. Check both settings, including copied config: a config-directory
flag alone does not override `keyring` or `auto` storage. See the official
[credential storage implementation](https://github.com/vercel/vercel/blob/main/packages/cli-auth/src/credentials-store.ts)
and recheck installed-version support before setup.

With file storage selected, Vercel maintains `auth.json` in that directory. Let
the CLI manage auth contents; do not hand-edit tokens or assume `.vercel/project.json`
contains authentication. Keep project-link metadata separate from `.cli/vercel/`.
Use a restrictive umask during login and verify secret-file permissions afterward.
Clear conflicting inherited token variables in the command's child environment.
Before consuming credentials copied from another checkout or a global login,
apply the session rule below. Do not copy unrelated global configuration or revoke it.

## Carry credentials without invalidating the source session

Vercel OAuth [refresh tokens rotate on use](https://vercel.com/docs/sign-in-with-vercel/tokens#refresh-token).
Independent copies of one OAuth session cannot safely keep refreshing: the first
refresh invalidates the shared token and leaves the other checkout's copy stale.

1. Before using copied credentials, inspect their type inside a concealed local
   process; report only whether refresh-token data is present, never its value.
   Unknown formats require supported authentication recovery, not guessed reuse.
2. Carry over the requested env and `.cli/` files using the shared copy controls.
   If `auth.json` contains a refresh token, move only the newly copied destination
   file to an ignored, owner-only holding path such as `.cli/vercel-source-copy/auth.json`
   **before any destination CLI authentication or read-only check**. Preserve
   existing destination credentials under the conflict rule; never move the source file.
3. With copied rotating auth absent from the active `.cli/vercel/auth.json`, run
   an independent destination login using the file-backend settings above. Verify
   the new saved credentials and exact target, then remove only the task-created
   holding copy. On login failure, keep dependent operations blocked; do not restore
   and refresh the copied source session. Do not log out or revoke the source login.
4. A verified reusable credential without rotating refresh state can use the normal
   concealed copy and read-only verification path. Do not strip refresh fields or
   convert an OAuth token into a supposed reusable token. A global keyring-only
   OAuth login needs independent project login rather than a keyring export.

## Authenticate and verify

1. Identify the intended account/project from task evidence and check the installed
   official vercel CLI using current help. Install missing tools from official instructions
   when authorized; do not treat a missing binary as an authenticated capability gap.
2. Check existing project authentication read-only with the scoped commands above
   and read-only team/project inventory. Reuse it only when the
   authenticated identity and target match. No browser visit or new token is needed
   when existing CLI authentication is valid.
3. If unauthenticated, expired, or mismatched, open https://vercel.com/dashboard or the official CLI login
   URL in the built-in Codex browser. Verify the signed-in account and select the
   account/team/workspace for the current project. Resolve ambiguous identities.
4. Obtain the supported CLI login/OAuth flow; use a token only when needed by the selected supported flow. Reuse existing task authority for needed setup, but do not
   rotate/revoke existing credentials, broaden access, or switch accounts silently.
5. Before key generation/reveal/Copy, validate a concealed transfer into the project's
   `.cli/vercel/` store or the CLI login flow configured to write there. Never return secrets in tool arguments,
   output, DOM reads, screenshots, logs, process arguments, or Git. If private
   password/MFA/CAPTCHA entry or concealed transfer needs the user, identify that
   exact step and resume afterward. Never harvest browser cookies/storage/session.
6. Confirm credentials were saved under `.cli/vercel/`, remain ignored and owner-only,
   then verify authentication read-only through that store and resolve exact targets.
   A browser login or created key alone is not usable CLI authentication proof.
7. Report verified client/identity/scope and readiness without secrets. Perform
   requested work through supported authenticated commands. Onboarding does not
   create resources, change business/configuration settings, or deploy as a test.

Browser service operations are fallback only for a documented capability missing
from the authenticated client. Authentication failures must be repaired first;
permission denials cannot be bypassed through another account/channel. If secure
setup is unavailable, finish independent work and report the concrete blocker.
