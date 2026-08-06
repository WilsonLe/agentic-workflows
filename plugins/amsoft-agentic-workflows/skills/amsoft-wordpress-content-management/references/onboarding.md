# WordPress Content onboarding

Use this guide for setup and first-run requests. Read
[application-password-contract.md](application-password-contract.md) first.

## Readiness inputs

Require the canonical HTTPS site URL, environment, site/project key, intended
pages/posts/media/design scope, username, and an approved local reference to a
WordPress Application Password. The reference may be a macOS Keychain item,
another OS credential store, a secret manager, or a protected local file path.

Do not ask for the Application Password value, cookie, nonce, or authorization
header in chat.

## Read-only first run

1. Resolve the secret-free contract and compare its site/environment with the
   request.
2. Authenticate through the selected local secret boundary without printing
   the credential.
3. Read `/wp-json/`, identify the WordPress identity, namespaces, content
   types, media support, editor, and token/design surfaces.
4. Perform the smallest authenticated read for the intended scope.
5. Report `Ready`, `Needs input`, `Needs configuration`, or `Blocked`, with
   the exact next safe action.

Do not create content, upload media, publish, change tokens, install plugins,
or modify files as an onboarding test.

## Ready state

`Ready` requires the intended site and environment, a reusable credential
reference, a successful authenticated identity read, and the endpoint/UI
capability needed for the first task. Authentication alone does not prove
publication, media upload, token editing, or visual verification capability.
