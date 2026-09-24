# Excalidraw Plus REST resource map

Base URL: `https://api.excalidraw.com/api/v1`

All routes use bearer-key authentication. The documented API is public beta.

## Collections

- `GET /collections` — paginated list.
- `GET /collections/{collectionId}` — exact collection metadata.
- `GET /collections/{collectionId}/scenes` — paginated scene list.
- `POST /collections` — create with `name`.
- `POST /collections/{collectionId}/scenes` — create a scene in a collection.
- `PATCH /collections/{collectionId}` — update collection metadata.
- `DELETE /collections/{collectionId}` — soft-delete to trash.

## Scenes and content

- `GET /scenes` — paginated scenes; optional `collectionId`.
- `GET /scenes/{sceneId}` — metadata and link records.
- `GET /scenes/{sceneId}/content` — elements, files, app state, versions.
- `POST /scenes` — create an empty scene with `name`, `pinned`, and
  `collectionId`.
- `PATCH /scenes/{sceneId}` — name, pinned state, or collection assignment.
- `PATCH /scenes/{sceneId}/content` — merge elements by ID/version, shallow
  app-state merge, and file merge.
- `PUT /scenes/{sceneId}/content` — authoritative full replacement.
- `DELETE /scenes/{sceneId}` — soft-delete to trash.

## Workspace administration

The public docs also cover workspace metadata, users, invites, and audit logs:

- `/workspaces`
- `/workspaces/users[/{userId}]`
- `/workspaces/invites[/{inviteId}]`
- `/logs`

The typed client exposes the documented account mutations as well:

- `PATCH /workspaces` — update workspace name or picture.
- `PATCH|DELETE /workspaces/users/{userId}` — update a documented user field
  or remove the user.
- `POST /workspaces/invites` — create an email invite or restricted link.
- `PATCH|DELETE /workspaces/invites/{inviteId}` — update or revoke an invite.

All writes use payload files outside Git. An explicit request authorizes
non-destructive writes. Collection, scene, user, and invite deletion require
the destructive approval phrase.

## Pagination

List endpoints use offset pagination. Default documentation values are offset
`0` and limit `10`; the endpoint reference constrains limit to `1..100`.
Continue only while `hasNextPage` is true and keep an explicit page/item bound.

Official references:

- https://plus.excalidraw.com/docs/api/endpoints
- https://plus.excalidraw.com/docs/api/collections
- https://plus.excalidraw.com/docs/api/scenes
- https://plus.excalidraw.com/docs/api/scene-content
