# DigitalOcean authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

## Project store

Apply [project-local controls](../../agentic-workflows/references/task-authority-and-secrets.md#project-local-cli-credentials).
Install the supported access token from a protected private file outside Git
into ignored `.cli/digitalocean/credentials.json`, retaining the helper's `0400`
file mode and `0700` directories. Command shapes (resolve and quote paths):

```sh
python3 <plugin-root>/scripts/digitalocean_configure_credentials.py <private-source> --destination <project-root>/.cli/digitalocean/credentials.json --verify
python3 <plugin-root>/scripts/digitalocean_cli.py --credentials-file <project-root>/.cli/digitalocean/credentials.json -- --context default account get --output json
```

Supply the explicit project `--credentials-file` on every launcher call and use
doctl's `--context default` so a named global context cannot override the protected
token. The launcher injects `DIGITALOCEAN_ACCESS_TOKEN` into the child and clears
conflicting inherited token variables. See [doctl authentication precedence](https://github.com/digitalocean/doctl/blob/main/README.md).
Do not pass tokens via `--access-token`, invoke `doctl auth token`, or copy the
whole global doctl configuration. `doctl auth init` does not populate this store.

The existing global helper default remains compatible; do not use it implicitly
for project work. Preserve the selected source token, and copy the normalized
project record with local env files into new same-project worktrees. Verify the
account and exact project/resource through the destination record before use.

## Authenticate and verify

1. Identify the intended account/project from task evidence and check the installed
   digitalocean_cli.py protected doctl launcher using current help. Install missing tools from official instructions
   when authorized; do not treat a missing binary as an authenticated capability gap.
2. Check existing authentication read-only with doctl --context default account get --output json through the launcher, followed by resource/project matching. Reuse it only when the
   authenticated identity and target match. No browser visit or new token is needed
   when existing CLI authentication is valid.
3. If unauthenticated, expired, or mismatched, open https://cloud.digitalocean.com or the official CLI login
   URL in the built-in Codex browser. Verify the signed-in account and select the
   account/team/workspace for the current project. Resolve ambiguous identities.
4. Obtain a supported scoped DigitalOcean access token. Reuse existing task authority for needed setup, but do not
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

Use `digitalocean_configure_credentials.py` and preserve its private-file, token,
read-only verification, and archival checks. The launcher uses default context
so an unrelated stored doctl context cannot override the protected token.
