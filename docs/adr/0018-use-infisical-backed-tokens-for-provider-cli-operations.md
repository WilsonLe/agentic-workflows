# ADR-0018: Use Infisical-backed tokens for provider CLI operations

- Status: accepted
- Date: 2026-11-12
- Owner: Project maintainer
- Evidence: Explicit maintainer request to enforce CLI usage with tokens obtained from Infisical, introduce Infisical operation skills, and use human-present authentication; [issue 121](https://github.com/WilsonLe/agentic-workflows/issues/121)
- Supersedes: 0015, 0017
- Superseded by: none

## Context

ADR-0015 selected Codex-only distribution and Vercel's connected app. ADR-0017
extended connected-app operations across providers and retired checkout token
stores. The maintainer now explicitly selects CLI operations with tokens obtained
from Infisical. Entry points, provider references, catalog prerequisites, shared
bootstrap, configuration transfer guidance and regression checks must agree.

## Decision

Keep the existing shared provider operation contract as the single channel owner.
Require service CLIs with named tokens fetched from Infisical for Vercel, Supabase,
DigitalOcean, Cloudflare, Railway, PostHog, Polar, Resend and other configured
service-management operations. Keep Git/GitHub repository delivery under its
existing Git/gh authentication contract. External plugin knowledge can supplement
product details; connected account tools are not the execution route.

Add one Infisical Account Operations skill owning human-present login, unattended
machine identity bootstrap, scoped get/create/update and concealed token delivery.
The host keyring or approved workload mechanism bootstraps Infisical; Infisical
owns provider tokens. Provider skills own identity/target validation, requested
resource effects and result verification. Reuse official CLIs and the existing
concealed-process pattern; add no persistent token registry, exporter, custom
service client or new authentication subsystem.

Resolve Infisical instance/profile/project/environment/folder/key independently
of provider account/project/environment/resource. Fetch only the required named
shared token without imports, recursion, expansion or personal overrides. Require
success and presence before launching the provider CLI, preventing cached-login
fallback. Deliver tokens through documented child environments without token
arguments, Infisical bootstrap credentials or unrelated inherited auth. Capture
and project both streams before tool output. Use owner-only temporary YAML input
outside Git for secret writes, compare exact concealed readback and clean task-owned
plaintext on failure as well as success. Unknown write outcomes require readback.

Use explicit token types, host and environment selectors, with read-only provider
identity/scope checks before dependent work. Missing/expired/denied access or absent
CLI support blocks that operation without connector, dashboard, broader-token,
cached-login or raw account API fallback. A product CLI does not promise complete
account/API coverage. Preserve task authority, enforced approvals, bounded data,
asynchronous completion, saved-state readback and relevant live verification.

Inherit Codex-only distribution, native delegation, the title hook and opt-in
configuration responsibilities from ADR-0015. Inherit preferences-only version-2
configuration transfer and rejection of credential-bearing legacy archives from
ADR-0017; change recovery guidance to separate Infisical authentication. Preserve
its optional, explicitly authorized OpenRouter runtime and environment-only input.
Worktrees carry only required application configuration via safe-copy controls;
never copy provider/Infisical bootstrap authentication stores. Leave legacy user
credentials and archives untouched; migration, rotation and deletion need scope.

## Alternatives

Connector-only execution contradicts the maintainer's selected CLI interface.
Per-project token files recreate the retired duplication and worktree-copy risks.
Passing expanded shell variables as token flags exposes secrets in process argv.
Bulk Infisical run/export inherits unrelated credentials and forwards output, so it
cannot alone establish safe named-token delivery. Adding provider API clients to
fill CLI gaps would create a parallel channel and unsupported coverage promise.
A new generic credential manager is unnecessary: official Infisical and provider
CLIs already own storage, authentication and service requests.

## Consequences

The suite gains an Infisical CLI prerequisite and one discoverable operations
skill. Initial human login and token population remain setup steps; the repository
change does not migrate provider credentials or activate an installed plugin.
CLI gaps may block operations previously exposed by connectors. Tokens must have
the actual provider permissions; a vault environment label is not a service target.

Instruction/package checks establish source consistency and portable distribution,
not OS-level enforcement or future agent adherence. Human-present login can prove
current vault access, but live service-token delivery and actual provider operations
need separate evidence. No production service change, charge, merge or release is
authorized by this policy edit. Rollback is source revert and verified regeneration;
existing credentials remain in place.

## Revisit

Revisit a service mapping when official CLI auth inputs or command coverage change,
or when the maintainer selects another channel. Change bootstrap storage, transfer
schema or execution boundaries through the existing owners and a replacement ADR;
do not silently enable a connector or local-token fallback.
