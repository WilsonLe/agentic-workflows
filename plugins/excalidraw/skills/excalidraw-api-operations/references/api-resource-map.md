# Excalidraw account resources and optional diagnostics

Apply [service browser operations](browser-selection.md). Use visible UI for
workspace settings, members/invites, collections, scenes, names, moves, sharing,
and deletion. Use `excalidraw-scene-operations` for canvas/content changes.

Optional protected helper reads can inspect collections, scenes/metadata/content,
workspace/users/invites, and audit logs only after independently matching the
browser identity and target. The base API URL is `https://api.excalidraw.com/api/v1`;
verify current official read documentation before relying on route shapes.
Bound pagination/item counts and private content; list access is not proof of
identity or permissions for every resource.

API creation, PATCH, PUT, DELETE, and invite/member mutations are not the default
management path. Existing helper capabilities do not confer channel authority;
report missing UI controls and obtain explicit direction before a non-browser write.
No API key is needed for normal browser operations.

Official reference: [Excalidraw API documentation](https://plus.excalidraw.com/docs/api/endpoints).
