# Excalidraw onboarding

## Prerequisites

- An Excalidraw Plus workspace.
- A personal MCP/API key created after a workspace administrator enables
  personal keys.
- The key stored in one local regular file outside Git.
- Python 3.

Personal keys act as the member and can access that member's private
collection. Workspace API/MCP keys represent shared integrations and are not
accepted by this release.

## First-run workflow

1. Ask only for the local key-file path and the user's confirmation that it is
   a personal key. A successful request cannot prove key type.
2. Inspect only path, type, owner, permissions, and size.
3. If group or other permissions are present, obtain
   `I_AUTHORIZE_SECURING_EXCALIDRAW_SOURCE` before narrowing the exact source to
   `0600`.
4. Run `excalidraw_configure_credentials.py` with `--token-type personal`,
   `--verify`, and `--archive-source`.
5. Verification performs only `GET /collections?limit=1&offset=0`.
6. Report protected storage readiness and sanitized route access. Do not create
   a collection or scene as an onboarding test.

## Ready state

Ready means the protected record validates, the bounded read succeeds, and the
source has been moved only after verification. Route-specific permissions still
need to be checked for the intended task.
