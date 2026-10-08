# Excalidraw personal-key contract

This contract applies only to optional protected read-only helper diagnostics or
an alternative channel explicitly requested by the user. Browser onboarding and
management require no token/key file. Establish the browser account/project first,
then independently match diagnostic identity and scope before any helper read.
Follow [service browser operations](browser-selection.md); the credential contract
does not authorize non-browser mutations or automatic credential creation.

## Accepted credential

Accept only a user-confirmed **personal MCP/API key**. Do not infer its type,
permissions, workspace, routes, or expiry from token characters. Reject
workspace keys, unknown keys, browser playground storage, OAuth material, and
keys pasted into chat or arguments.

## Input and protected storage

The source must be a current-user-owned regular file outside Git, at most 64
KiB, containing either one key or exactly:

```json
{"token_type":"personal","token":"..."}
```

The normalized record is
`~/.config/agentic-workflows/excalidraw/credentials.json`. Its directory is `0700`; the
file is `0400`. Writes are atomic and do not replace an existing valid record
without `--replace`.

The standalone and central packages use the same Agentic Workflows credential primitives
for private-file validation, atomic writes with directory synchronization,
collision-safe archival, and transactional archive rollback.

A broadly readable source is refused unless the user supplies the non-secret
confirmation `I_AUTHORIZE_SECURING_EXCALIDRAW_SOURCE`; only that exact file is
then narrowed to `0600`.

## Verification and relocation

`GET /collections?limit=1&offset=0` proves that the key authenticates and may
read that route. It does not prove personal key type or every route permission.
Verification failure restores the previous credential and preserves the
source. After success, `--archive-source` moves the source into
`~/.config/agentic-workflows/excalidraw/imported-sources/` with protected modes. Name
collisions fail closed.

## Execution and secrecy

Load the key only from protected storage and attach it to the in-memory
`Authorization: Bearer` header. Remove inherited Excalidraw key variables from
child environments. Never store or emit the key in Git, payload files, shell
history, logs, screenshots, issues, PRs, backups, or evidence.

Rotation, replacement, revocation, and local removal require explicit requests
targeting the exact key or protected path.
