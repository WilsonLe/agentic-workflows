# Excalidraw change management

## Required preview

Before every write, provide:

- exact resource type and ID;
- HTTP method and fixed API path;
- payload file and a field/element-count summary, never a raw secret-bearing
  dump;
- current metadata/content summary;
- expected effect and affected access;
- readback assertions;
- protected backup and recovery approach.

## Authorization classes

- POST, PATCH, and content PUT: the user's explicit request to create or change
  the exact resource authorizes the operation. Do not ask for a typed token or
  a second confirmation.
- DELETE: require `I_APPROVE_EXCALIDRAW_DESTRUCTIVE` for the exact resource.

Authorization is operation-specific. Do not reuse it for a materially
different target or payload.

## Outcome handling

Definite HTTP failures are not retried. A timeout, reset, or transport failure
after a write is an unknown outcome. Perform only safe GET readback. If the
intended state is not unambiguously observable, stop and present recovery
choices.

Scene and collection deletion moves the resource to trash; it is not permanent
deletion. Invite deletion revokes the invite, while user deletion removes the
user from the workspace and revokes access. Do not claim public-API restoration
or permanent deletion when the docs do not provide those endpoints.
