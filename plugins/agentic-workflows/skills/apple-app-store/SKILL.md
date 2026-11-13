---
name: apple-app-store
description: Use whenever inspecting or managing Apple App Store Connect, uploading an iOS build, deploying to TestFlight, managing beta groups or submitting an App Store release. Use asc with credentials obtained from Infisical, distinguish release and Sign in with Apple keys, and verify the exact app, build and distribution state.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Service CLI and Infisical access** — Install the community-maintained asc CLI and Infisical CLI. Resolve the exact vault scope and coherent ASC key family; deliver ASC_KEY_ID, ASC_ISSUER_ID and ASC_PRIVATE_KEY from Infisical into an isolated child environment. Verify app and bundle IDs through read-only commands without cached profiles.
- **Optional: Apple build and signing tools** — Building or signing requires the app's supported Xcode toolchain, signing identity and provisioning assets. Read-only account work does not; API keys do not replace signing assets.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Apple App Store and TestFlight

Use the community-maintained `asc` CLI under the
[shared provider contract](../agentic-workflows/references/service-browser-operations.md).
Load [Infisical Account Operations](../infisical-account-operations/SKILL.md) for
concealed named reads and read [Apple credentials](references/credentials.md)
before selecting a key family or runtime/configuration input. ASC API keys,
Sign in with Apple keys and Xcode signing identities serve different consumers.

Resolve account/team, issuer, app/bundle ID, platform, version/build, artifact and
destination from the task/project. Inspect installed version/help, verify the
selected credentials and exact app with captured read-only calls, then follow
[release operations](references/releases.md). Missing roles, signing material,
app records or CLI coverage block dependent work without cached-login, Apple ID
web-session, connector or raw HTTP fallback. Do not persist `asc` profiles,
create/rotate keys or install upstream skill packs as a preflight.

Reuse authority for the requested upload, beta distribution, review or release;
do not add groups, notify testers, submit reviews or release publicly through CLI
defaults. Apply [task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md)
to reviewer data and writes. Capture/project both streams; report app/build IDs
and state without tokens, reviewer data, tester addresses or signed upload URLs.
Distinguish local build, upload, processing, group availability, beta review,
App Review and storefront availability. Read unknown outcomes before retrying;
reuse the existing build instead of uploading a duplicate.
