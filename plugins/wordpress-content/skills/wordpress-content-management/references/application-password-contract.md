# WordPress Application Password handling

Use a site-scoped WordPress Application Password only when the chosen REST path needs one. Prefer an
existing approved local credential-store reference. On macOS, resolve it from Keychain or collect it
with a native masked prompt where Paste works. On other platforms, use the operating-system
credential store or approved secret manager.

Never request the password in chat or place it in command arguments, environment variables,
temporary payloads, files, logs, screenshots, or repository state. Pass it directly from the local
credential resolver to the HTTPS request process and discard it afterward.

Before a write, make one authenticated read to confirm the username, site URL, environment, and
needed capability. Authentication does not add any Git, issue, pull-request, or workflow-record
requirement.
