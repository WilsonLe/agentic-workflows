---
name: github-account-operations
description: Use whenever the user selects an Infisical-backed GitHub token to inspect or manage a GitHub account, repository, Actions run, release or integration. Use gh with the exact stored token and verify host, actor and repository access. Ordinary repository delivery retains its existing Git and gh authentication unless this token is explicitly selected for it.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Service CLI and Infisical access** — Install gh and Infisical CLI; resolve the explicitly selected GitHub token, host and repository. Deliver GH_TOKEN from Infisical into a concealed child environment and verify actor/token type and repository scope without cached-login fallback. Ordinary repository delivery keeps its existing authentication unless this token is selected.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# GitHub operations with Infisical credentials

Use `gh` under the [shared provider contract](../agentic-workflows/references/service-browser-operations.md)
and load [Infisical Account Operations](../infisical-account-operations/SKILL.md).
Resolve host, owner/repository, actor/token type and operation before fetching.
Observed `/providers/github` key `VULCAN_GITHUB_TOKEN` maps to `GH_TOKEN` for
github.com; the name proves neither actor nor scope. Ordinary repository delivery
keeps existing authentication unless the user selects this token for it. Do not
log in, persist tokens, change global accounts or alter Git credential helpers.

Inspect version/help and precedence. For github.com, inject `GH_TOKEN` and set
`GH_HOST` to the verified host; exclude `GITHUB_TOKEN`/enterprise aliases. Enterprise
Server requires its selected host and matching `GH_ENTERPRISE_TOKEN`; never send
a github.com token to an inferred host. Capture/project both streams; do not run
`gh auth token`, dump auth config or pass token headers/URLs.

Verify actor with `gh api --hostname <host> user --jq '{login,id}'` when supported,
and exact repository with `gh repo view <owner/repo> --json id,nameWithOwner,url`.
Installation tokens may not support `/user`; use supported installation/repository
metadata for their intended scope, never another credential. Use explicit repo/host
selectors and bounded pagination. Missing permissions/identity evidence blocks
dependent writes without cached-login, connector or broader-token fallback.

Use supported `gh` subcommands, including `gh api` for documented GitHub endpoints;
add no HTTP/SDK client. Keep issue/PR delivery with `standard-development-workflow`.
Token possession grants no workflow dispatch, release, secret change, billing,
deletion, merge or deployment authority. Read back writes and asynchronous run
IDs/status; inspect unknown outcomes before retry. API success does not prove a
deployed artifact/app. Project only required metadata; private code/logs need scope.

Sources: [gh environment](https://cli.github.com/manual/gh_help_environment),
[gh api](https://cli.github.com/manual/gh_api),
[installation auth](https://docs.github.com/en/rest/authentication/authenticating-as-a-github-app-installation).
