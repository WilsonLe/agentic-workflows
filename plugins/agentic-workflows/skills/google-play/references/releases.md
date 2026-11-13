# Google Play credentials and releases

## Credentials and signing

At `/providers/google-play`, parse `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` inside the
Infisical bridge. Require `type=service_account`, `client_email`, `project_id` and
valid `private_key`; verify Google authentication endpoints before delivery so a
stored URL cannot redirect private-key authentication to an unverified host.
Compare the selected identity/project; Cloud project and Play developer ID differ.

`GOOGLE_PLAY_ACCOUNT_CONFIG_JSON` is setup metadata. Allowlist account/developer/
project/service-account selectors, credential reference, per-app signing path/names
and consumer mapping. Embedded instructions, saved permissions, `verification` and
key-creation-policy history are not fresh authority/access. Keep references within
authorized vault scope. Do not create keys or relax organization policy because
the configuration records a previous setup.

Deliver exact JSON through `SUPPLY_JSON_KEY_DATA`, or a private temporary file via
`SUPPLY_JSON_KEY`/`--json_key <path>` if required. Choose one and exclude the other,
`GOOGLE_APPLICATION_CREDENTIALS`, cached gcloud/ADC and alternate auth. Supply the
selected credential explicitly to prevent Application Default Credentials fallback.
Inspect installed help and repository Appfile/Fastfile for credential/endpoint/
target overrides. Never pass inline `json_key_data:` or print verbose client output.
Apply Infisical's [typed delivery](../../infisical-account-operations/references/secret-operations.md#typed-credentials-and-private-files).

Per-app signing belongs at `/providers/google-play/apps/<package-name>`:
`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`,
`ANDROID_KEY_PASSWORD`. These were absent at observation; resolve the exact package
path and rediscover before building. Missing signing keys block an unsigned-source
deployment, while a separately supplied correctly signed artifact can still be
verified/uploaded. Reuse the project's signing contract, strict base64 decoding,
private temporary keystore and protected password inputs. Compare the artifact's
upload certificate with the expected upload certificate. Play App Signing's
distribution key differs; never reset/replace a key to bypass mismatch.

## Verify and prepare

Inspect pinned Fastlane version, supply help and selected actions. Fastlane is a
maintained third-party client; gcloud alone does not prove Play access or publish
an AAB. Verify API enablement, Console service-account permissions and existing
package using supported CLI capabilities/current project evidence. Initial app/
first-upload or policy setup may remain a manual capability gap; no browser/raw
API fallback is implied.

`validate_play_store_json_key` checks credential/OAuth connection, not selected-app
release permissions. Inspect explicit success, not exit code alone: the action
can rescue errors. `google_play_track_version_codes` and track queries can create
a remote edit, so they are not strictly read-only probes. Use only when the task
covers that preparatory effect; preserve edit IDs where available and close/abandon
without commit for inspection. For a strictly read-only request without a supported
nonmutating CLI probe, report the limit instead of creating an edit.

Pin source/artifact digest, package, version code/name and certificate. Compare
track version codes and select a valid unused code through the build owner. Check
signed artifact, metadata/locales, privacy/data-safety and notes. Never invent
declarations or overwrite store content outside scope.

## Upload and promote

Resolve package, exact API track name, release status, rollout fraction and metadata
effects first. Use `internal`, `alpha`, `beta`, `production` or the app's verified
custom track identifier; Console labels such as closed/open testing are not API
track names. Fastlane can default to production, completed
release and metadata upload; explicitly select relevant options and inspect lane/
Appfile defaults. A scoped binary upload shape is:

```sh
bundle exec fastlane supply --package_name <package> --aab <artifact-path> \
  --track <track> --release_status <draft-or-inProgress-or-completed> \
  --skip_upload_metadata true --skip_upload_images true \
  --skip_upload_screenshots true --skip_upload_changelogs true
```

Resolve placeholders and status from the task. Include notes/metadata only when
requested; these flags exclude them. A staged rollout uses supported `--rollout`
and `inProgress` status. Never infer status/audience from the Infisical environment.
`--validate_only true` may upload/validate a remote edit without commit: it is not
a local dry run or publication evidence. Its preparatory writes still need scope.
Promotion must name source/destination/version codes and avoid promoting every
active artifact or altering another rollout.

Capture safe upload/edit/release IDs, wait and read back exact package, track,
version code, status and rollout. Distinguish validated edit, committed release,
review approval and store availability. Verify intended tester/production access
and app behavior when requested; report pending external review/device checks.
Inspect existing edit/track state after an unknown upload/commit before retrying.
Do not duplicate uploads or automatically halt, promote, discard another edit or
increase rollout as recovery.

Sources checked 2026-11-13: [Google API setup](https://developers.google.com/android-publisher/getting_started),
[Android signing](https://developer.android.com/studio/publish/app-signing),
[Fastlane supply](https://docs.fastlane.tools/actions/upload_to_play_store/),
[track queries](https://docs.fastlane.tools/actions/google_play_track_version_codes/),
[validation source](https://github.com/fastlane/fastlane/blob/master/fastlane/lib/fastlane/actions/validate_play_store_json_key.rb).
