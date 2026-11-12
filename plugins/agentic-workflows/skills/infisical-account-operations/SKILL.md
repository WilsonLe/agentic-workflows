---
name: infisical-account-operations
description: Use whenever authenticating to Infisical, getting or setting secrets, or obtaining API tokens for service CLI operations. Use the Infisical CLI with explicit instance/project/environment/folder scope, conceal secret values, and inject only the required token into the service CLI process.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Infisical CLI** — Install the official Infisical CLI and inspect its version/help. Authenticate with human-present browser login or an approved machine identity; verify instance, organization, project, environment and folder without revealing secrets.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Infisical Account Operations

Infisical owns provider tokens. This skill owns authentication, scoped secret
get/create/update, and delivery into a CLI subprocess; the provider skill owns
the service operation and target. Follow the
[provider channel contract](../agentic-workflows/references/service-browser-operations.md)
and [concealed-secret contract](../agentic-workflows/references/task-authority-and-secrets.md).
Do not introduce a persistent token store, exporter or parallel service client.

## Resolve and authenticate

Record the nonsecret Infisical domain, organization/profile, project ID,
environment slug, folder, secret name, and intended provider account/resource.
These are separate targets: an Infisical `dev` environment does not prove the
stored token belongs to a development provider account. Resolve ambiguity before
fetching secrets or writing. Never default to the first project or production.

Read [authentication](references/authentication.md) for installation, human-present
browser login, headless identities, expiration and secure bootstrap. Inspect
`infisical --version` and the installed command's `--help`; the examples target
CLI 0.45.6's `secrets-manager` commands. Older aliases are not proof of equivalent
behavior. Verify login status and accessible project/environment metadata without
printing tokens. Installation and a login alone do not prove secret access.

## Get and set

Read [secret operations and token delivery](references/secret-operations.md)
before any secret-bearing command. Get one named shared secret with imports,
recursion, personal overrides and expansion disabled. Capture its value inside
the transfer process; never return it to chat or tool output. A caller asking to
use a token needs a functioning consumer, not a displayed key.

For set, distinguish create from replacement. Use the supported `create` or
`update --file` input with an owner-only temporary YAML file outside Git, never
`NAME=value` or token flags. Validate the file route with synthetic data before
real use; capture both output streams. Check the same exact secret by concealed
readback and equality, then remove task-owned plaintext even on failure. A timeout
or unknown write outcome requires readback before retry; never blindly turn a
failed create into an overwrite. Report names and status only.

Credential creation, replacement, deletion, identity permissions and provider
effects retain their actual authority and enforced human-approval requirements.
Do not rotate, delete, migrate or harvest existing credentials just to test setup.

## Run a provider CLI

Use [the shared token mappings](../agentic-workflows/references/service-browser-operations.md#cli-token-mappings).
Fetch the named token from Infisical for every remote operation, validate presence
before launching the CLI, and use its documented environment input. Keep
Infisical bootstrap credentials and unrelated service tokens out of the provider
child. Preserve Railway account/project token types and Polar sandbox/production.
Never pass a secret through argv, shell tracing or a tool argument. If the CLI
version cannot accept a concealed input, report that capability gap.

Missing, empty, expired, denied or mismatched credentials block dependent calls;
do not fall back to cached CLI login, a connector, dashboard management, broader
credentials, or raw account API calls. Verify provider identity/scope read-only,
execute only the authorized effect, and read back state and relevant live behavior.
Keep local, synthetic, authenticated and live-operation evidence distinct.
