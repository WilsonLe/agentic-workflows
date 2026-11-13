# Apple release operations

Use the isolated credential environment from [credentials](credentials.md).
Commands below are installed `asc` 6.3.0 shapes; inspect current help and select
only authorized effects. Capture/project both streams.

## Prepare

Read the app's release runbook and repository delivery state. Pin source/artifact,
platform, bundle/app ID, team, version/build. Inspect the IPA/PKG, signing identity,
profile and entitlements against current Xcode/Apple requirements. API access is
not signing readiness. Reuse the project's Xcode/Fastlane build owner and release
checks; do not change signing teams, certificates or entitlements to pass upload.
Verify critical app behavior where available.

Verify app identity with `asc --read-only apps view --id <app-id>`. For beta
distribution, inspect `asc --read-only testflight groups list --app <app-id>
--paginate` and match exact group IDs/internal-external type. Inspect existing
build/version state before upload. Resolve metadata, privacy/export compliance,
agreements and reviewer requirements; never invent legal declarations.

## TestFlight

An upload-only request uses:

```sh
asc publish testflight --app <app-id> --ipa <artifact-path> \
  --upload-only --wait --output json
```

For requested group distribution of an existing build, use the supported
`asc publish testflight --app <app-id> --build-id <build-id> --group <group-id>
--wait --output json` instead of uploading again. Inspect platform/artifact help.
Do not add `--notify`, invite testers, enable public links or use `--submit
--confirm` unless the request covers those effects. External beta review may be
required. TestFlight authority does not authorize App Store release.

Retain safe upload/build IDs, wait for processing and read back the exact build
and group membership/availability. Report beta-review state and remaining human
tester/device checks. Upload success or membership alone is not installability.

## App Store

Inspect `asc release stage`, `asc validate` and `asc publish appstore --help`.
The high-level `publish appstore --dry-run` previews a plan; `asc builds upload
--dry-run` reserves remote upload operations and is not read-only. A preview or
validation grants no execution authority.

Prepare the exact version, metadata/assets, build and manual/automatic release
mode through the app runbook. Stage without submission when only preparation is
requested. With submission authority, the high-level shape is:

```sh
asc publish appstore --app <app-id> --ipa <artifact-path> \
  --version <version> --wait --submit --confirm --output json
```

This can create/update a version, attach a build and submit it. Verify the stored
version's release mode first: automatic release after approval can make it public.
A review-only request requires manual release mode and readback before submission.
Reuse existing processed builds through supported staging/submission commands.
Public/phased release and rollout changes need authority for the exact audience,
storefront/version; a general ASC key does not provide it.

Read back submission/version states. Accepted submission is awaiting review,
not approval/store availability. Observe the requested terminal state or report
pending external review and its remaining gate. For public release, verify the
storefront version and relevant app journey separately. Report rejection details
without reviewer data. On timeout/unknown outcome, inspect the same app/version/
build before retrying; do not upload/submit twice or auto-withdraw a release.

Sources checked 2026-11-13: installed 6.3.0 help,
[asc upstream](https://github.com/rorkai/App-Store-Connect-CLI),
[Apple build uploads](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/),
[TestFlight](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/).
