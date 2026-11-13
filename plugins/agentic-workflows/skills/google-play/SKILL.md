---
name: google-play
description: Use whenever inspecting Google Play deployment setup, building or signing an Android release, uploading an AAB or APK, managing testing tracks, or publishing and rolling out an app on Google Play. Use Fastlane with credentials obtained from Infisical and verify package, signing identity, version code, track and rollout state.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Service CLI and Infisical access** — Use the project's pinned Fastlane CLI and Infisical CLI. Resolve the service-account JSON and account/package selectors; deliver SUPPLY_JSON_KEY_DATA or a private credential file without ADC fallback. Verify exact package, track and permissions before a release.
- **Optional: Android build and signing tools** — Source builds require the project's Android SDK, JDK, Gradle and package-specific upload keystore/passwords; account credentials alone do not sign an AAB. A supplied signed artifact can be inspected separately.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

Reuse complete skill and reference instructions already available in the current context for the same source/version, including host-loaded content. A name, description, path, summary, or prior-session read alone is not loaded instructions. Read missing instructions when needed; reread only for a known source/version change, unavailable or truncated content (including after compaction), or an explicit request. A stage transition or repeated link does not require reloading.

When another workflow would help, use the [suite capability map](../../CAPABILITIES.md) for discovery as needed. Apply the selected skill using that reuse rule and check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Google Play operations

Use the project's pinned Fastlane CLI (`bundle exec fastlane supply`) under the
[shared provider contract](../agentic-workflows/references/service-browser-operations.md).
Load [Infisical Account Operations](../infisical-account-operations/SKILL.md) and
read [credentials and release operations](references/releases.md) before remote
work/signing. Reuse Android/Gradle/Fastlane build and release owners; add no custom
Publisher API client, global login or parallel delivery pipeline.

Resolve developer account, service-account identity, package, artifact, version
code/name, signing certificate and exact track/status/rollout. Account credentials
and per-package upload signing keys are separate. Configuration/OAuth success
prove neither app permissions nor signing. Missing app records, signing material,
Console setup or CLI capabilities block dependent work; do not create/rotate keys,
change signing identity or use a broader account as a test.

Deliver selected JSON/signing inputs concealed, capture/project both streams and
read back package/track/version and asynchronous state. Distinguish build/signature,
validation, staged edit/upload, committed testing release, production rollout,
review and store availability. Inspect unknown outcomes before retry. Testing
authority does not authorize production promotion; audience/notification/public
effects retain their actual authority under
[task authority and concealed secrets](../agentic-workflows/references/task-authority-and-secrets.md).
