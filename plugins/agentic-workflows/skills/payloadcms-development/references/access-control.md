# Payload access control

Access is part of the data contract, not an Admin UI visibility setting. Payload evaluates it before
operations complete and scopes rules to an operation. Put reusable rules in typed modules, name them
for what they permit, and test both a broad privileged role and constrained/anonymous callers.

## Start from an authorization matrix

Before coding, write a row for each actor and operation: create, read, update, delete, version read,
admin login, and unlock if supported. Include document ownership or tenancy and field-level secrets.
Keep an explicit default-deny policy for privileged actions.

```ts
import type { Access } from 'payload'
import type { User } from '../payload-types'

export const isEditorOrAdmin: Access<User> = ({ req: { user } }) =>
  user?.role === 'editor' || user?.role === 'admin'

export const publishedOrEditor: Access<User> = ({ req: { user } }) => {
  if (user?.role === 'editor' || user?.role === 'admin') return true
  return { status: { equals: 'published' } }
}

export const ownDocuments: Access<User> = ({ req: { user } }) => {
  if (!user) return false
  if (user.role === 'admin') return true
  return { owner: { equals: user.id } }
}
```

A `read` rule may return a boolean or a query constraint. Prefer a query constraint for document
subsets so the Local API, REST, GraphQL, and Admin list cannot fetch unauthorized documents and
filter them only afterwards. Treat `overrideAccess` as a tightly reviewed system boundary rather
than a normal convenience in user-facing code.

## Collection, global, and field rules

- Collections define `create`, `read`, `update`, and `delete`; auth collections can also define
  `admin` and `unlock`, and versioned collections can define `readVersions`.
- Globals expose their own access map. A globally readable setting does not imply that it is
  globally updateable.
- Field access protects sensitive fields even when a caller may read the document. Do not rely on
  hidden Admin fields to protect values from API callers.
- Use `req.user` for identity and apply the same tenant/ownership condition to every applicable
  operation. For create, validate that caller-supplied owner or tenant fields cannot cross a
  boundary; a hook may set ownership from the authenticated user.

## Verification matrix

Test the real operation for at least: anonymous, allowed role, disallowed authenticated role,
different-owner/tenant, and privileged role. For a read constraint, seed an allowed and a forbidden
document and assert only the allowed data is returned. In E2E, prove a denied user cannot discover a
hidden navigation route by entering its URL directly, not only that a button is absent.

## Official sources

- [Access-control overview](https://payloadcms.com/docs/access-control/overview)
- [Collection access control](https://payloadcms.com/docs/access-control/collections)
- [Global access control](https://payloadcms.com/docs/access-control/globals)
- [Field access control](https://payloadcms.com/docs/access-control/fields)
