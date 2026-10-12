# Chrome Web Store review and approval checklist

Use this checklist for the browser extension produced by a project. Record completion and
evidence in that project's `CHROMEWEBSTORE.md`, using [the template](../templates/CHROMEWEBSTORE.md).
Requirements checked against Google's documentation on 2026-10-07; recheck the linked sources
and current dashboard before submitting. Google makes the approval decision.

## 1. Set up the publisher account

- [ ] Register in the [developer dashboard](https://chrome.google.com/webstore/devconsole),
  accept the developer agreement/policies, and pay the one-time registration fee shown there.
- [ ] Set the publisher name and verify the contact email. Use an inbox monitored for review
  decisions and policy notices; complete any applicable account verification/address fields.
- [ ] Enable Google account 2-Step Verification before publishing or updating an extension.

Done when the intended publisher account has no outstanding setup requirements.
See [registration](https://developer.chrome.com/docs/webstore/register),
[account setup](https://developer.chrome.com/docs/webstore/set-up-account), and
[2-Step Verification policy](https://developer.chrome.com/docs/webstore/program-policies/policies).

## 2. Check functionality, permissions, and code

- [ ] Describe one narrow, useful purpose. Verify the extension delivers that benefit and
  every advertised feature works.
- [ ] Reconcile all required/optional API and host permissions with actual features. Remove
  unused permissions and narrow broad site access where possible.
- [ ] Bundle executable code for ordinary Manifest V3 contexts. Check dependencies for remote
  scripts, downloaded executable logic, and obfuscation. If relying on a documented exception,
  verify its exact scope against current policy and explain it to reviewers.
- [ ] Run project checks and the offline audit, resolve findings, then test the release build
  in Chrome. Cover permission refusal, worker restart, errors, and relevant AI fallback cases
  using [the testing guide](devtools-testing.md).

Done when the exact candidate has recorded test results and no unresolved release blockers.
See [program policies](https://developer.chrome.com/docs/webstore/program-policies/policies)
and [extension preparation](https://developer.chrome.com/docs/webstore/prepare).

## 3. Reconcile privacy and listing information

- [ ] Inventory local/sync storage, analytics, page content, accounts, and any cloud AI data.
  Record recipients, purposes, retention, deletion, and user controls.
- [ ] Publish a privacy policy when handling user data. Check that the implementation,
  policy, and dashboard data declarations agree. Obtain required user consent.
- [ ] Prepare accurate descriptions, icons, screenshots, support details, and release notes.
  Provide reproducible test instructions and reviewer access when login is required.
  Keep credentials in the dashboard's intended private fields, never in repository notes.

Done when every disclosure and listing claim can be matched to the tested candidate.
See [privacy fields](https://developer.chrome.com/docs/webstore/cws-dashboard-privacy)
and [user data policy](https://developer.chrome.com/docs/webstore/program-policies/policies).

## 4. Freeze and package the candidate

- [ ] Check the manifest name, version, icons, and description. Increase the version for
  updates; the manifest description must be at most 132 characters.
- [ ] ZIP the built extension with `manifest.json` at the archive root. Include required
  assets; exclude secrets, development files, and unrelated material.
- [ ] Record the source commit, extension version, ZIP path, SHA-256, and test evidence.

Done when the archive contains the verified build and its identity is recorded.
See [packaging requirements](https://developer.chrome.com/docs/webstore/prepare).

## 5. Upload and complete the dashboard

Follow the [store readiness authority boundary](store-readiness.md) before external actions.

- [ ] Select the correct publisher and create a new item, or open the existing extension
  for an update. Upload the frozen ZIP and check the parsed version and package details.
- [ ] Complete Store Listing, Privacy, Distribution, and Test instructions. Explain the
  single purpose, justify permissions, declare remote code/data practices, and certify
  applicable data-use statements. Resolve every dashboard validation error.

Done when the saved dashboard details match the candidate and intended distribution.
See [publishing steps](https://developer.chrome.com/docs/webstore/publish).

## 6. Submit and track review

- [ ] Choose automatic publication after approval or deferred publication, consistent with
  the user's authorized release plan. Automatic publication combines both external outcomes.
- [ ] Click Submit for Review and confirm. Record the item ID, version, submission time,
  publishing choice, and actual dashboard status.
- [ ] Monitor the dashboard and publisher email. Most reviews finish in a few days, but
  some take weeks. Contact developer support if pending for more than three weeks.

Done when the dashboard confirms submission; uploading alone does not establish review.
Google reviews new submissions and updates using automated and manual systems.
See [submission](https://developer.chrome.com/docs/webstore/publish) and
[review process](https://developer.chrome.com/docs/webstore/review-process).

## 7. Handle the decision

- [ ] If rejected, record the cited policy and decision, reproduce the concern, fix the
  package/listing/disclosures, retest, and resubmit. Use a higher version for a new package.
  If the decision appears mistaken, follow the rejection notice's appeal instructions and
  provide evidence; check current appeal limits before appealing.
- [ ] If approved, record Google's decision and the approved version. For deferred publication,
  record the dashboard's expiry: currently the approved submission must be published within
  30 days, otherwise it returns to draft and needs another review.

Done when the recorded decision is tied to the exact submitted version and next action.
See [review outcomes and appeals](https://developer.chrome.com/docs/webstore/review-process)
and [deferred publishing](https://developer.chrome.com/docs/webstore/publish).

## 8. Publish and verify availability

- [ ] For deferred publication, publish the approved version under the existing release
  authority. Read back the dashboard status and intended visibility.
- [ ] Open the store listing with an intended audience account. Verify version, descriptions,
  assets, privacy/support links, and availability; install the store-delivered extension in
  a clean profile and exercise its main feature.
- [ ] Record the listing URL, published version, time, and installation/runtime evidence.
  Apply the checklist to later updates and monitor policy notices after launch.

Done when the intended audience can obtain and use the published version.
See [publication guidance](https://developer.chrome.com/docs/webstore/publish).
