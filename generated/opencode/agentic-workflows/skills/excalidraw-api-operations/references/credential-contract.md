# Excalidraw personal-key contract

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

## Accepted credential

Accept only a **personal MCP/API key** whose type is established from observed
provider creation metadata or the user's supplied provenance. Record browser
creation evidence without asking the user to confirm the same fact again. Do not infer its type,
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
