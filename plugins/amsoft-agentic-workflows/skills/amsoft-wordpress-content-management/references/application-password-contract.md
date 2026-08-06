# WordPress Content Application Password contract

This contract is the authentication boundary for `amsoft-wordpress-content-management`.
It is site-scoped, secret-free in recorded state, and reusable across tasks
only after target and capability revalidation.

## Accepted access

Require:

- a canonical HTTPS WordPress URL and explicit environment (`local`, `staging`,
  or `production`);
- a site/project key that is stable within the user's project;
- a WordPress username and a WordPress **Application Password** created for
  that user and site; and
- the minimum REST/UI capability required by the requested content operation.

The user may call this an application key; WordPress core calls it an
**Application Password**. It is not a generic API key. Do not silently substitute a
JWT, cookie, nonce, provider token, SSH credential, or an unknown plugin token.
If the site uses a documented alternative, record that it is an exception and
stop unless the user explicitly selects the compatible content adapter.

## Secret-safe provisioning

The user may provide a local path or select an existing approved secret-store
record. The assistant must never request the secret value in chat.

On macOS, a local helper may use a `getpass` prompt for first provisioning,
save the prompted value in the current user's Keychain through the system
Security API or the protected `security add-generic-password` path, and later
resolve it with `/usr/bin/security find-generic-password` using the exact
service/account labels recorded in `credential_ref`. The value must be passed
directly to the request process and discarded after the operation. Do not
print `security` output, a shell command with an interpolated value, request
headers, or a response containing credentials.

On other platforms, use the platform credential store or an approved secret
manager. File-based input, if the user's environment requires it, must be an
owner-protected local file whose path—not contents—is recorded.

## Reusable contract shape

Record only the following classes of data:

```json
{
  "schema_version": 1,
  "contract_kind": "wordpress-content-auth",
  "plugin": "wordpress-content",
  "site": {
    "key": "example-site",
    "canonical_url": "https://example.invalid"
  },
  "environment": "staging",
  "username": "content-editor",
  "auth_method": "wordpress_application_password",
  "credential_ref": {
    "store": "macos-keychain",
    "service": "com.amsoft.wordpress.content",
    "account": "example-project/example-site"
  },
  "scopes": ["pages", "posts", "media", "design-tokens"],
  "last_verified_at": "2026-08-05T00:00:00Z"
}
```

The Application Password itself, cookies, nonces, authorization headers,
secret-store contents, and raw response bodies are never contract fields.
Validate the shape with `schemas/content-auth-contract-v1.schema.json` and
keep examples synthetic.

## Project-specific reuse

After the reusable contract has passed a read-only identity check, create or
update a project-specific reference outside the repository, for example:

```text
~/.config/amsoft/wordpress/content/<project-key>/<site-key>.json
```

The project contract may contain the contract identity/digest, environment,
allowed content surfaces, endpoint allowlist, and `credential_ref`. It must
not copy the Application Password. Before each task, compare the contract's
canonical URL and environment with the user request and perform a fresh
authenticated read. A changed site, username, scope, credential reference,
or capability invalidates reuse and requires re-onboarding.

## Failure and rotation

Mark the contract `Needs input` when the URL, environment, username, credential
reference, or requested scope is missing. Mark it `Blocked` when the read
identifies the wrong site/account, TLS is invalid, the Application Password is
revoked, or the endpoint denies the needed capability. Rotate or remove the
local secret-store item only on an explicit request; do not edit repository
contracts to conceal authentication failure.
