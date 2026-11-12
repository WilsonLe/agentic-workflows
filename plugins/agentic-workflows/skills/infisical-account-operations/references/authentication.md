# Authenticate to Infisical

Use the official [installation guide](https://infisical.com/docs/cli/install)
and [CLI reference](https://infisical.com/docs/cli/reference-agents#login), then
inspect the installed CLI's help. On macOS, the documented installation is
`brew install infisical/get-cli/infisical`; tap `infisical/get-cli` first if Homebrew
requires it. Install only from the official package source within setup authority.

## Human present

1. Resolve US Cloud (`https://app.infisical.com`), EU Cloud
   (`https://eu.infisical.com`) or the exact self-hosted URL. Do not send credentials
   to an inferred instance. Start the login without `--plain`:

   ```sh
   infisical login --domain https://app.infisical.com --save-as agentic-workflows
   ```

2. Open the CLI's actual browser callback URL using the supported browser. Let the
   user complete private sign-in/MFA and enforced consent; keep the CLI alive.
   Do not copy a printed token into chat. A user login is saved as a profile in the
   system keyring. Verify the selected vault; do not silently switch to plaintext
   file storage if the keyring is unavailable.
3. Check `infisical login status --profile agentic-workflows`. Resolve the
   organization and project with metadata-only CLI commands such as
   `infisical secrets-manager projects get --profile agentic-workflows`.
   If there are several plausible projects, ask before selecting or creating one.
4. Optionally use `infisical init --project-id <project-id>` to link the directory.
   Inspect the generated nonsecret project configuration before committing it;
   keep credential state in the keyring, never in the checkout. For automated
   commands pass explicit domain/profile/project/environment/path instead of
   depending on a directory's mutable defaults.
5. Verify a named secret's presence through the concealed read path. Report login
   and project access separately from token availability and actual provider access.

Reuse a healthy user profile across worktrees. Reauthenticate an expired profile
using `infisical login --profile agentic-workflows --domain <verified-url>`;
do not create duplicate accounts or overwrite another profile incidentally.

## Unattended workloads

Use a [machine identity](https://infisical.com/docs/documentation/platform/identities/machine-identities)
with access only to the required projects/environments/folders. A human user
session is not a portable server credential. Prefer a workload identity/OIDC
auth method when its trust configuration is available; otherwise
[Universal Auth](https://infisical.com/docs/documentation/platform/identities/universal-auth)
uses a Client ID and Client Secret to obtain a time-limited access token.

The bootstrap secret cannot be retrieved solely from the vault it unlocks. Keep
it in the host's approved secret mechanism, such as macOS Keychain or a CI secret,
outside Git and configuration-transfer archives. Read it internally into the
login subprocess's `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` environment; pass the
nonsecret ID through `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID`. Use
`infisical login --method=universal-auth --silent --plain` only with both output
streams captured inside that process, then supply the returned token as
`INFISICAL_TOKEN` to Infisical commands. Never use secret flags or print the login
result. Remove the Client Secret from descendant environments after exchange.

Honor token expiry and renewal limits. On auth failure, stop dependent provider
work and report reauthentication/permission requirements without printing the
server response or expanding scopes. Never treat a cached provider CLI login as
recovery. Establish fresh read-only identity and exact-target evidence on resume.
