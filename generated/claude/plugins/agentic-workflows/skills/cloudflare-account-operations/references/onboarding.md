# Cloudflare authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

## Project store

Apply [project-local controls](../../agentic-workflows/references/task-authority-and-secrets.md#project-local-cli-credentials).
Install a supported scoped API token from a protected private file outside Git
into ignored `.cli/cloudflare/credentials.json`. Retain the normalized provider
record at `0400`, directories at `0700`, and the installer's token classification.
Command shapes (resolve/quote paths and select the verified token type):

```sh
python3 <plugin-root>/scripts/cloudflare_configure_credentials.py <private-source> --destination <project-root>/.cli/cloudflare/credentials.json --token-type <verified-token-type> --verify
python3 <plugin-root>/scripts/cloudflare_api.py --credentials-file <project-root>/.cli/cloudflare/credentials.json verify
```

For an account API token, include the observed `--account-id` when needed for
verification. Supply `--credentials-file` on every helper call; the legacy global
default is not this project's store. Reuse only matching healthy records, copy
them into new same-project worktrees with their exact modes, then verify again.

For supported Wrangler workflows, read this same record through the shared
`load_credential` validator in a reviewed concealed launcher, and inject only its
token into the Wrangler child's `CLOUDFLARE_API_TOKEN`; set the observed
`CLOUDFLARE_ACCOUNT_ID`. Clear conflicting inherited Cloudflare token/key/email
variables, including legacy `CF_*` aliases, in that child. Never source the JSON,
expand a token into arguments, or export it across the session. Sanitize captured
output and errors before returning them. The bundled `cloudflare_api.py` only
supports verification/account reads; it is not a general Wrangler launcher.
Use an existing validated secret-safe route or report the capability gap.

Prefer this portable API-token path over copying Wrangler OAuth caches, which
may contain rotating sessions. `wrangler login`, a config file, or a changed
working directory alone does not put credentials in `.cli/`. Verify with a
read-only supported command such as `wrangler whoami`, followed by exact account
and resource matching. See [Wrangler environment variables](https://developers.cloudflare.com/workers/wrangler/system-environment-variables/).

## Authenticate and verify

1. Identify the intended account/project from task evidence and check the installed
   protected cloudflare_api.py helper and supported Wrangler commands using current help. Install missing tools from official instructions
   when authorized; do not treat a missing binary as an authenticated capability gap.
2. Check existing authentication read-only with protected token verification plus account/zone/resource matching. Reuse it only when the
   authenticated identity and target match. No browser visit or new token is needed
   when existing CLI authentication is valid.
3. If unauthenticated, expired, or mismatched, open https://dash.cloudflare.com or the official CLI login
   URL in the built-in Codex browser. Verify the signed-in account and select the
   account/team/workspace for the current project. Resolve ambiguous identities.
4. Obtain a supported scoped Cloudflare API token; never a Global API Key. Reuse existing task authority for needed setup, but do not
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

Use `cloudflare_configure_credentials.py` for protected token installation and
retain type classification, owner-only storage, read-only verification, and scoped
archival. Do not manually expand credentials into curl header arguments.
