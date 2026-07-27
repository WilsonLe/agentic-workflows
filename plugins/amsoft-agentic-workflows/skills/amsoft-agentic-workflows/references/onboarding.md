# AMSoft Agentic Workflows onboarding

Use this guide to onboard the complete suite or the smallest subset that matches the user's work.

## Component guides

- [Academic Writing](../../academic-writing-workflow/references/onboarding.md)
- [Humanizer](../../humanizer/references/onboarding.md)
- [Food Image Editing](../../food-image-editing/references/onboarding.md)
- [AMSoft Cloudflare Account Operations](../../amsoft-cloudflare-account-operations/references/onboarding.md)

Read this guide first, then read only the selected component guides.

## Onboarding flow

1. Confirm that `amsoft-agentic-workflows` is installed and enabled. If it was just installed or updated, have the user restart Codex and begin a new task before testing newly added skills or tools.
2. If the immediate task will create, publish, or maintain GitHub repositories, branches, commits,
   pull requests, or releases, complete the GitHub CLI check below before starting GitHub work.
3. Ask whether the user wants the complete suite introduced or has one immediate task. Prefer onboarding only the relevant components.
4. Explain the four components in one sentence each, including their important boundaries:
   - Academic Writing is review-gated and evidence-first.
   - Humanizer changes style without inventing facts or promising detector evasion.
   - Food Image Editing is food-only and never uses image generation.
   - Cloudflare operations use credentials outside chat and require explicit approval for writes.
5. Read the selected component onboarding guides and check their prerequisites.
6. Run only safe first-use checks requested by the user. Never edit an image, create an academic draft, or change Cloudflare merely to prove installation.
7. Return a readiness summary with one status per component: `Ready`, `Needs input`, `Needs configuration`, or `Not selected`.
8. Give the user one copy-ready first prompt for each selected component.

## GitHub CLI check

Apply this check only when the selected task depends on GitHub. Do not treat the presence of the
`gh` executable as proof that authentication is valid.

1. Confirm that GitHub CLI is installed:

   ```bash
   gh --version
   ```

2. Verify the live GitHub session:

   ```bash
   gh auth status -h github.com
   ```

3. If the command reports a missing, expired, or invalid token, stop GitHub writes and
   re-authenticate:

   ```bash
   gh auth login -h github.com
   ```

4. Run `gh auth status -h github.com` again. Then confirm the active account:

   ```bash
   gh api user --jq .login
   ```

5. For AMSoft organization work, confirm the authenticated account can access `anhminhsoft`:

   ```bash
   gh api orgs/anhminhsoft --jq .login
   ```

Expected success means the status command exits successfully, the active login is the intended
publishing identity, and the organization command returns `anhminhsoft`. Never print, copy, or
store the GitHub token in onboarding output or repository files.

## Readiness summary

Include:

- the selected workflow and intended first task;
- available skills or tools that were actually observed;
- missing inputs, runtime dependencies, credentials, or restart requirements;
- GitHub CLI authentication status when the selected task depends on GitHub;
- the next safe action;
- any boundary that still requires the user's approval.

Do not claim that a component is ready from its documentation or filesystem alone. Verify what can be verified in the active task, and label anything that requires a restart or a new task.

## Suggested first prompt

> Onboard me to AMSoft Agentic Workflows. Ask what I want to accomplish, check only the relevant prerequisites, and give me a readiness summary plus the safest first prompt for each selected workflow.
