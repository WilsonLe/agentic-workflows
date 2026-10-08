# Cloudflare authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

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
