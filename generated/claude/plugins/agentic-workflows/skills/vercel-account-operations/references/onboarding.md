# Vercel authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

## Project credential location

Apply [project-local credential controls](task-authority-and-secrets.md#project-local-supabase-and-vercel-credentials)
first. Resolve the current checkout's absolute root, ignore `/.cli/`, and prepare
`.cli/vercel/` with owner-only permissions. Use the documented
[`--global-config`](https://vercel.com/docs/cli/global-options#global-config)
option on **every** invocation, including login, whoami, inventory, and writes:

```sh
vercel --global-config <absolute-project-root>/.cli/vercel login
vercel --global-config <absolute-project-root>/.cli/vercel whoami
vercel --global-config <absolute-project-root>/.cli/vercel teams list
```

These are command shapes; substitute and quote the resolved path before execution.
Vercel maintains `auth.json` and `config.json` in the selected directory. Let the
CLI manage their format; do not hand-edit tokens or assume `.vercel/project.json`
contains authentication. Keep project-link metadata separate from `.cli/vercel/`.
Use a restrictive umask during login and verify secret-file permissions afterward.
Clear conflicting inherited token variables in the command's child environment.
An existing global login may be reused only by a concealed transfer of the exact
matching provider files into the protected project directory, followed by scoped
read-only verification. Do not copy unrelated global configuration or revoke it.

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
