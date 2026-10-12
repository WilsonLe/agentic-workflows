# ERPNext authenticated CLI onboarding

Apply [CLI and browser assistance](browser-selection.md).

1. Identify the intended account/project from task evidence and check the installed
   protected erpnext_api.py command-line client using current help. Install missing tools from official instructions
   when authorized; do not treat a missing binary as an authenticated capability gap.
2. Check existing authentication read-only with whoami, bounded user-summary, and site/company/project/record context reads. Reuse it only when the
   authenticated identity and target match. No browser visit or new token is needed
   when existing CLI authentication is valid.
3. If unauthenticated, expired, or mismatched, open the exact ERPNext site origin from the task/project documentation or the official CLI login
   URL in the built-in Codex browser. Verify the signed-in account and select the
   account/team/workspace for the current project. Resolve ambiguous identities.
4. Obtain the intended ERPNext user API key/secret through official User/API Access controls. Reuse existing task authority for needed setup, but do not
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

The existing installer accepts a private JSON key file or one-row Frappe CSV plus
confirmed site origin. A validated concealed browser-to-file bridge may create
that owner-only input outside Git; use `erpnext_configure_credentials.py`, protected modes,
read-only verification, and explicitly scoped replacement/archival. A source path
is the fallback private input mechanism when automated concealed transfer is
unavailable, not the default first question. Never expose a full User record.
