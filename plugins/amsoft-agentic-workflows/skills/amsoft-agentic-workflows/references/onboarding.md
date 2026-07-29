# AMSoft Agentic Workflows onboarding

Use this guide to onboard the complete suite or the smallest subset that matches the user's work.

## Component guides

- [Academic Writing](../../academic-writing-workflow/references/onboarding.md)
- [Standard Development Workflow](../../standard-development-workflow/references/onboarding.md)
- [Humanizer](../../humanizer/references/onboarding.md)
- [Food Image Editing](../../food-image-editing/references/openai-image-editing-prompt-workflow.md)
- [Restaurant Marketing Management](../../amsoft-restaurant-marketing-management/references/onboarding.md)
- [AMSoft YouTube Content Inspection](../../amsoft-youtube-content-inspection/references/onboarding.md)
- [AMSoft YouTube Media Operations](../../amsoft-youtube-media-operations/references/onboarding.md)
- [AMSoft YouTube Library Sync](../../amsoft-youtube-library-sync/references/onboarding.md)
- [AMSoft DigitalOcean Account Operations](../../amsoft-digitalocean-account-operations/references/onboarding.md)
- [AMSoft Cloudflare Account Operations](../../amsoft-cloudflare-account-operations/references/onboarding.md)
- [AMSoft Railway Account Operations](../../amsoft-railway-account-operations/references/onboarding.md)
- [AMSoft Excalidraw REST Operations](../../amsoft-excalidraw-api-operations/references/onboarding.md)
- [AMSoft Config Transfer](../../amsoft-agentic-workflows-config-transfer/references/onboarding.md)
- [WordPress CLI Operations](../../wordpress-cli-operations/references/onboarding.md)
- [WordPress Site Management](../../wordpress-site-management/references/onboarding.md)
- [WordPress Stream Audit Logging](../../wordpress-stream-audit-logging/references/onboarding.md)
- [ERPNext Operations](../../amsoft-erpnext-operations/references/onboarding.md)

Read this guide first, then read only the selected component guides.

## Onboarding flow

1. Confirm that `amsoft-agentic-workflows` is installed and enabled. If it was just installed or updated, have the user restart Codex and begin a new task before testing newly added skills or tools.
2. If the immediate task will create, publish, or maintain GitHub repositories, branches, commits,
   pull requests, or releases, complete the GitHub CLI check below before starting GitHub work.
3. Ask whether the user wants the complete suite introduced or has one immediate task. Prefer onboarding only the relevant components.
4. Explain the 15 components in one sentence each, including their important boundaries:
   - Standard Development Workflow reuses provenance-backed repository capabilities, establishes
     scope/resource/verification contracts, runs fail-fast and state-isolated validation, freezes
     final evidence, requires separate plan, PR, and staging approvals, and never deploys
     automatically to production.
   - Academic Writing is review-gated and evidence-first.
   - Humanizer changes style without inventing facts or promising detector evasion.
   - Food Image Editing is food-only, creates evidence-backed linked curation
     reports when shortlisting a shoot, and never uses image generation.
   - Restaurant Marketing Management verifies restaurant facts and operational readiness, checks
     offer contribution, separates drafting from external action, and measures business outcomes
     without treating reach as revenue.
   - YouTube operations inspect publicly first, require an explicit rights basis for media
     retrieval, bound playlist/channel work, and use only a protected browser-exported
     YouTube-cookie file for account-gated yt-dlp access.
   - DigitalOcean operations use `doctl` with a token supplied outside chat and require explicit
     approval for writes.
   - Cloudflare operations use CLI commands with a token supplied outside chat and require explicit
     approval for writes.
   - Railway operations accept only an account token created with **No
     workspace**, install it outside the plugin with owner-only permissions, and
     require exact-target, production, and destructive approvals as applicable.
   - Excalidraw operations use a protected personal key with the public REST API only, require
     exact-target approval for writes, and apply stronger gates to replacement and deletion.
   - Config Transfer exports preferences and supported cloud credentials only
     inside authenticated encryption; portable cross-OS files require a
     passphrase entered locally rather than in chat.
   - WordPress CLI Operations uses authorized SSH and the installation's existing WP-CLI runtime,
     discovers Docker or bare-metal topology, and verifies changes in the real site.
   - WordPress Site Management uses authenticated administrator access, discovers actual REST/UI
     capabilities, and requires rendered desktop/mobile verification for visual work.
   - WordPress Stream Audit Logging is opt-in, requires an explicit per-site policy and recovery
     path, and proves a real reversible event plus scheduler, data, and administrator UI health.
   - ERPNext Operations asks only for the path to a JSON API key file, copies credentials to a
     persistent owner-read-only file, verifies identity with a read-only call, and requires
     previews, explicit approval, and readback for all ERPNext writes.
5. Read the selected component onboarding guides and check their prerequisites.
6. Run only safe first-use checks requested by the user. Never edit an image,
   create an academic draft, change WordPress or ERPNext, or change
   DigitalOcean, Cloudflare, Railway, or Excalidraw merely to prove installation.
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

## Install or update from the private GitHub marketplace

Register the marketplace once using a Git transport that already has read access:

```bash
codex plugin marketplace add anhminhsoft/amsoft-agentic-workflow-codex-plugin \
  --ref main --json
codex plugin add amsoft-agentic-workflows@amsoft --json
```

SSH is supported when already configured:

```bash
codex plugin marketplace add \
  git@github.com:anhminhsoft/amsoft-agentic-workflow-codex-plugin.git \
  --ref main --json
```

Never embed credentials in a URL. Refresh and reinstall later releases with:

```bash
codex plugin marketplace upgrade amsoft --json
codex plugin add amsoft-agentic-workflows@amsoft --json
codex plugin list --json
```

Verify marketplace, version, enabled state, resolved source, and installed cache, then start a new
task so the updated skills load.

## Suggested first prompt

> Onboard me to AMSoft Agentic Workflows. Ask what I want to accomplish, check only the relevant prerequisites, and give me a readiness summary plus the safest first prompt for each selected workflow.
