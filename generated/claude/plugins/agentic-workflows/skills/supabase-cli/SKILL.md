---
name: supabase-cli
description: Use when working with Supabase CLI for a project, including authentication, project inspection, linking, migrations, and functions. Authenticate with the intended account, keep reusable credentials in the project's gitignored .cli directory, and carry them with local env files into new worktrees.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated service CLI** — Use Official Supabase CLI; verify authentication and exact project account/target before remote operations. Local-only commands need no remote login.
- **Optional: Browser authentication assistance** — If CLI authentication is missing, use the built-in Codex browser for supported login or secure key/token acquisition, then return to CLI verification. Browser operations are fallback only for an authenticated CLI capability gap.

<!-- catalog-prerequisites:end -->

# Supabase CLI

Read [CLI and browser assistance](references/browser-selection.md) and
[project-local credential controls](../agentic-workflows/references/task-authority-and-secrets.md#project-local-supabase-and-vercel-credentials)
before setup. Default to a supported authenticated CLI for remote operations.
This skill owns Supabase authentication and target selection; use repository
runbooks and installed help for the requested operation's implementation.

## Authenticate and retain project credentials

1. Resolve the current checkout root, intended account/organization, project ref,
   and environment from task and repository evidence. Check `supabase --version`
   and installed help. Local-only CLI work needs no remote login; authenticate
   before any command that accesses the hosted account.
2. Prepare ignored, owner-only `.cli/supabase/` using the shared credential controls.
   Retain the personal access token as data in `.cli/supabase/access-token`.
   This path is our project convention, not a Supabase auto-discovery location.
3. Reuse that file only after a read-only authentication/target check. For missing
   or expired authentication, use the supported Supabase login or personal-access-token
   flow with browser assistance. Conceal transfer of the exact credential into
   the project file; never use `--token <secret>` or print native-store contents.
   If login saved into native credential storage, use a validated concealed bridge
   for that exact provider item, or the official token flow directly into the
   project file. Do not copy a keychain or harvest a browser session. Stop dependent
   work if no supported concealed transfer exists; resume after private entry.
4. Consume the file inside a local launcher as plain data, injecting its value as
   `SUPABASE_ACCESS_TOKEN` only into the Supabase child process. Replace any
   conflicting inherited token in that child. Do not source the file as shell
   code, export it across the session, or interpolate it into arguments. Inspect
   the launcher and sanitize output/failures under the shared concealed-transfer
   contract before real use; no launcher is bundled by this skill.
5. Through that environment, run `supabase projects list` and, where needed,
   `supabase orgs list`. Match organization ID and project ref against the intended
   target and account evidence; names or the first result are insufficient. A
   credential file or successful login alone does not establish readiness.
6. Verify file presence, ignore status, owner-only permissions, and successful
   read-only access through the saved project credential. Report only client/version,
   target metadata, credential path, and status. Carry this file and local env files
   into same-project worktrees under the shared copy controls, then reverify there.

The [Supabase login reference](https://supabase.com/docs/reference/cli/supabase-login)
documents native credential storage with a home-directory fallback and supports
`SUPABASE_ACCESS_TOKEN` for authenticated commands without a persisted global login.
`--workdir` selects project files; it does not relocate the credential store.
Do not reassign `HOME` or assume changing directories moves authentication.
Application publishable/anon/service-role keys are not CLI personal access tokens.

## Operate on the verified target

Check current command help and repository runbooks; use explicit project/workdir
flags when supported. Inspect existing link metadata and bind the exact project
before `supabase link`; a Git worktree is not a separate Supabase remote project.
Login/copy authority does not authorize migrations, resets, secrets changes,
function deployment, project creation, or production access. Match each requested
effect to existing task authority and retain the delivery workflow's gates.

Run the smallest supported operation, read back saved state, and verify its relevant
behavior. On missing/expired auth, target mismatch, permission denial, or unknown
write outcome, stop dependent operations and resolve or read back before retrying.
Keep logs bounded and secret-free; browser service fallback requires a documented
authenticated CLI capability gap. Never use a broader account to bypass denial.
