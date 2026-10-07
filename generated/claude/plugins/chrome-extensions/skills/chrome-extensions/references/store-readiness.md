# Store readiness

For submission, review decisions, or approval/publication planning, follow
[the Chrome Web Store review and approval checklist](web-store-review.md).

Keep `CHROMEWEBSTORE.md` in the extension project's root, following an existing project
format where present. Use [the template](../templates/CHROMEWEBSTORE.md) for a new record.
On every extension change reconcile the actual built manifest and behavior with:

- the extension's single purpose and truthful description;
- required/optional API permissions and required/optional host permissions, with the user
  feature, call site, necessity, and narrower alternative considered for each;
- data collected, stored, transmitted, shared, and deleted, including analytics, page data,
  account identifiers, AI inputs/outputs, external providers, retention, and user controls;
- privacy policy, support contact, actual assets, version, and validation evidence; and
- packaging, release notes, reviewer instructions, and unresolved dashboard requirements.

Mark unknown facts `TODO`; do not invent a privacy policy URL, contact, data practice,
permission rationale, screenshot, or completed test. Local processing and Chrome sync
storage are different data flows. Sending data to a cloud AI service changes the disclosure
even when local inference is the default.

Before preparing a submission, check current [Web Store program policies](https://developer.chrome.com/docs/webstore/program-policies)
and [publication guidance](https://developer.chrome.com/docs/webstore/publish). Review the
artifact for unnecessary files and executable remote code, and verify listing claims against
tested behavior. Store metadata is an authoring record, not a certification or submission API.

Prepare a reviewable package/listing when requested. Uploading, submitting, paying fees,
or publishing needs the user's explicit instruction for the target account and extension.
After an authorized submission, read back the actual version and review/publishing status;
an upload is not approval and a published status needs its own live evidence.
