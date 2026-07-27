# WordPress Site Management onboarding

Use this guide for setup and first-run requests.

## Access contract

Require:

- the canonical HTTPS site URL and whether it is production or staging;
- the intended first task and allowed scope;
- either an existing signed-in administrator browser session or an authenticated API method;
- for core Application Password authentication, a username plus Application Password supplied
  through the process environment or secret manager, never in chat.

Do not assume a generic API key works with core WordPress. Record the authentication type without
recording the credential.

## Read-only first run

1. Open the REST index and identify WordPress and plugin namespaces exposed by the site.
2. Verify the configured identity with the smallest authenticated read request.
3. Inspect endpoint methods and schemas needed for the first task.
4. Inventory only the relevant content types, editor/theme architecture, and plugins.
5. If visual or administrator UI work is intended, verify that the existing browser session can
   reach the correct site without exposing cookies or storage.
6. Report the site identity, environment, authentication method, observed role/capabilities,
   supported execution surfaces, missing configuration, and next safe action.

Do not create a test post, upload media, change settings, install software, or publish anything as
an onboarding check.

## Ready state

Mark the skill `Ready` when the intended site and environment are confirmed, an authenticated
read identifies the intended administrator account, and the specific endpoint or UI needed for the
task is available. Administrator authentication alone does not prove every requested capability.

## Suggested first prompt

> Use WordPress Site Management to inspect my site read-only, verify the configured administrator
> access, identify its theme/editor/content architecture and the API or UI surfaces available for
> my task, then return a readiness summary. Do not make changes.
