# Task authority and concealed secrets

Read this contract before provider setup, credential handling, or an external mutation.
For Supabase, Railway, Vercel, Cloudflare, DigitalOcean, ERPNext, and Excalidraw, apply
the selected service's authenticated CLI channel contract. Browser-assisted
login/key acquisition uses the concealed transfer controls below, followed by
CLI authentication and target verification. Browser service operations require
a supported authenticated-client capability limitation, not missing credentials.
For browser steps, follow [browser selection](browser-selection.md): prefer the
Codex in-app browser for setup, sign-in/OAuth, credential creation, and dashboard
readback when it supports the required flow. Keep the concealed transfer and
verification requirements below.

## Carry the request through completion

A user's request to achieve an outcome authorizes the necessary steps within that
outcome's account, project, environment, and purpose. Reuse that authority across
turns and dependent steps. Inspect the current target, execute, read back, and
verify the requested flow without asking the user to approve each button or command.

Save, Add, Approve, Authorize, consent, credential creation, secure storage, and
configuration can be necessary steps. A button's label does not create a new human
approval gate. Check its actual effect and requested permissions first. Complete
ordinary in-scope steps yourself when the available tools support them.

Record the originating request and resolved target as nonsecret authority evidence.
Required CLI confirmation flags may express that existing authority; the user
does not need to type a helper's exact phrase. Such flags do not establish authority
by themselves. Credential access also does not authorize unrelated actions.

Ask only when a required account, target, material choice, or authority remains
unresolved, or a higher-priority platform/tool rule requires human input. A new
charge, unrelated permission grant, destructive effect, merge, or deployment needs
authority covering that effect; reuse a request that already covers it. Respect
explicit read-only, plan-only, and stop-before-action instructions. Follow the
delivery workflow's distinct merge and deployment gates; a generic request to
change repository guidance does not authorize releasing it.

Prepare all independent authorized work before asking. Explain the exact missing
decision or restriction and its source. An ordinary provider confirmation dialog
can be completed by the agent within scope; an enforced human-only platform
approval cannot be bypassed. If an automatic approval review rejects an action,
report the action and stated reason. Continue independent work where possible.

## Keep secret values inside the transfer process

Concealed credential handling is permitted within an authorized setup. The agent
can click a provider's Copy control and transfer the clipboard directly to the
user's secret store without seeing the value. A masked field alone does not prove
the transfer path is safe: establish that clipboard APIs, tool responses,
screenshots, child output, and errors will not return plaintext to the agent.

On macOS, prefer a reviewed local helper that reads the clipboard and writes the
exact named Keychain item in one process. Use the Security framework's item APIs
for secret data, rather than passing a password to a shell command. Apple documents
[adding a password](https://developer.apple.com/documentation/security/adding-a-password-to-the-keychain),
[updating items](https://developer.apple.com/documentation/security/updating-and-deleting-keychain-items),
and the [pasteboard API](https://developer.apple.com/documentation/appkit/nspasteboard).
These API references describe a pattern, not a bundled Keychain helper or a claim
that an arbitrary CLI accepts stdin. Inspect and validate the selected mechanism
before using a real credential.

1. Resolve the credential's source, type, least sufficient permissions, and exact
   destination from the request and provider metadata. Do not reveal a masked field.
2. Inspect the transfer helper and downstream CLI for secret-bearing arguments,
   logs, telemetry, errors, and output. Exercise the route with a synthetic value
   before real use when its output behavior has not been established.
3. Click Copy only when the concealed route is ready. Consume the value internally;
   never return clipboard text, a DOM input value, or a secret to chat or tool output.
4. Store it in the named Keychain item, existing approved secret manager, or the
   project-local CLI store required below for the covered providers. Verify
   status and presence without printing the value. Preserve an existing credential
   unless replacement is within the request. Clear the clipboard after successful
   transfer if it still contains the copied value; handle failure and concurrent
   clipboard changes without losing the user's unrelated data.
5. Retrieve the value inside a local launcher and pass it directly to the consumer
   through supported stdin, a narrowly scoped child environment, or a protected
   provider channel. Suppress or sanitize child output and failures before they
   reach a tool response. Keep inherited environments and access narrow.
6. Verify credential health read-only, then confirm the saved configuration and
   requested end-to-end behavior. Report names, targets, and status only.

Do not print `pbpaste`, return a clipboard getter's value, display Keychain secret
output, interpolate a Keychain lookup into a CLI argument, or use
`security add-generic-password -w <value>` for automated transfer. Shell expansion
still places secrets in process arguments even when the command text hides them.
Do not put secret values in tool arguments, history, traces, source files, issues,
PRs, screenshots, recordings, or evidence. A protected environment still requires
output discipline; a child process may echo it.

When an existing provider helper requires a private file, retain its storage and
type checks. An authorized local bridge may create only the required owner-only
input outside tracked Git content without returning its content, then invoke that helper. Minimize
plaintext lifetime and remove or archive input according to the helper's documented
contract. Do not claim existing file-based helpers use Keychain. If no safe transfer
route is available, complete the rest of setup and report that concrete limitation;
ask for private entry only for the unsupported step.

## Project-local CLI credentials

For Supabase, Vercel, Railway, Cloudflare, and DigitalOcean CLI/client work,
authenticate for the intended project and persist
reusable credentials under that checkout's `.cli/` directory. Use the provider
skill's supported storage/consumption mechanism; a global login alone does not
complete project setup. This is local storage scoping, not a restriction on the
credential's remote permissions. Verify the account and exact target separately.

1. Resolve the project root and credential source before setup. Reuse matching,
   healthy project credentials; if only a global login exists, transfer only the
   exact verified provider credential through a concealed route or authenticate
   into the project store. Preserve unrelated global logins and secret stores.
2. Add `/.cli/` to the project's root `.gitignore` before writing credentials.
   Check both `git check-ignore` and `git ls-files`: ignore rules do not untrack
   existing files. Stop secret writes if a destination is tracked, unignored,
   symlinked, outside the project root, or owned by another user. Fix the local
   destination first; exposed tracked credentials need explicit remediation.
3. Use provider subdirectories under `.cli/`. Create directories with mode `0700`
   and secret files with `0600`, retaining stricter helper-required `0400` modes
   for Railway, Cloudflare, and DigitalOcean records (or equivalent
   owner-only ACLs); use a restrictive umask during login/copy, not only afterward.
   Do not print, source as shell code, or pass credential contents in arguments.
   Keep `.cli/` out of deployment uploads, build contexts, archives, and evidence
   as well as Git; check the relevant packaging exclusions before those actions.
4. Use the selected checkout's store explicitly on every authenticated command.
   Check inherited auth environment variables so they cannot silently select a
   different credential; clear conflicting values only in the child process.
   Verify saved-file presence, ignore status, permissions, and a read-only CLI
   account/project check without exposing values. A copied file is not auth proof.
5. When branching a new worktree of the same project, carry over local environment
   files and `.cli/` credential files to matching relative paths before dependent
   work. Use the resolved source checkout, ordinary independent file copies, and
   the same pre-write ignore/path/permission checks at both ends. Never overwrite
   conflicting destination files, follow symlinks, use shared hardlinks, or copy
   home-directory/keychain stores. Before any destination authentication check,
   apply the provider's rotating-session rule: a copied refresh token must not
   invalidate the source session. Rebind commands to the destination `.cli/`,
   establish independent login where required, then verify authentication and target.
6. On missing, expired, or mismatched credentials, resume the provider's supported
   authentication flow into this project store. Preserve existing destination
   credentials until replacement is authorized and verified. Report only paths,
   identity/target metadata, and status; stop dependent remote operations when a
   safe transfer or exact target cannot be established.

The provider skill owns its credential format and CLI consumption mechanism:

| Provider | Project credential location | Consumer |
| --- | --- | --- |
| Supabase | `.cli/supabase/access-token` | Child-only `SUPABASE_ACCESS_TOKEN` |
| Vercel | `.cli/vercel/` | Explicit file backend and project `--global-config`; handle rotating OAuth copies before reuse |
| Railway | `.cli/railway/credentials.json` | Protected launcher `--credentials-file`; account-token-only schema |
| Cloudflare | `.cli/cloudflare/credentials.json` | Protected helper `--credentials-file`; validated record for supported Wrangler child environment |
| DigitalOcean | `.cli/digitalocean/credentials.json` | Protected launcher `--credentials-file` with doctl default context |

The Railway, Cloudflare, and DigitalOcean installers accept `--destination` for
these ignored stores. Their source token input remains a protected private file
outside Git; existing normalized `.cli` records are copied directly between
same-project worktrees and consumed by the launcher, not re-imported as raw tokens.
Legacy global helper defaults remain for compatibility: always supply explicit
project paths in these workflows. Never omit a path and silently fall back globally.

## Check the rule against the task

| Request or observation | Next action |
| --- | --- |
| Set up a named provider integration; Save/Add/Authorize is required for its stated permissions | Inspect the effect, click, and verify using the original request |
| Copy a masked API credential into a named Keychain item | Use the validated concealed bridge; report presence and credential health |
| Configure a CLI from that Keychain item | Retrieve internally and use supported stdin or child environment; keep output secret-free |
| A helper needs a write-confirmation phrase | Supply it only when the original request covers the exact write |
| Inspect the account without changes | Read only; no setup or write as a test |
| A permission grant expands access beyond the integration, or the target is ambiguous | Finish independent work, then ask for the missing decision |
| A tool requires human approval or rejects the action | Obey and name the enforced restriction; do not bypass it |
| The setting saved successfully | Read it back and test the requested flow before claiming completion |
