# Payload configuration, collections, globals, and components

## Compose typed configuration

Keep config as a small composition root. Define collections and globals in their own files, type them
with `CollectionConfig` and `GlobalConfig`, then include them in `buildConfig`. This keeps a feature
reviewable and lets a plugin append only what it owns.

```ts
import { buildConfig } from 'payload'
import { Posts } from './collections/Posts'
import { Users } from './collections/Users'
import { SiteSettings } from './globals/SiteSettings'

export default buildConfig({
  admin: { user: Users.slug },
  collections: [Users, Posts],
  globals: [SiteSettings],
  plugins: [],
})
```

Use a collection for plural documents and a global for one application-wide document. Do not add a
global solely to avoid defining an ownership model: identify the editor, API client, lifecycle hooks,
and access policy before implementation.

```ts
import type { CollectionConfig, GlobalConfig } from 'payload'
import { canManageContent, publishedOrEditor } from '../access/content'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: { useAsTitle: 'title', defaultColumns: ['title', 'status'] },
  access: {
    create: canManageContent,
    read: publishedOrEditor,
    update: canManageContent,
    delete: canManageContent,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    { name: 'status', type: 'select', required: true,
      options: ['draft', 'published'], defaultValue: 'draft' },
  ],
}

export const SiteSettings: GlobalConfig = {
  slug: 'site-settings',
  access: { read: () => true, update: canManageContent },
  fields: [{ name: 'announcement', type: 'textarea' }],
}
```

Use field `access`, field hooks, validation, and `forceSelect` deliberately. In particular, if an
access rule or hook needs a field, make its data availability explicit; do not depend on an Admin
list view happening to select it.

## Custom Admin components

Payload components are React Server Components by default. Prefer a server component when it only
needs server data or the Local API. Mark a component `'use client'` only for interactive browser
state; pass only serializable client props, and obtain client-safe config through Payload UI hooks.

Register by config path, naming a default export directly or a named export after `#`:

```ts
export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    components: {
      edit: { beforeDocument: ['/components/PostGuidance#PostGuidance'] },
    },
  },
  fields: [
    {
      name: 'title', type: 'text', required: true,
      admin: { components: { Field: '/components/TitleField#TitleField' } },
    },
  ],
}
```

Choose the narrowest component scope: root for application-wide chrome, collection/global for one
document surface, and field for a field. Preserve the underlying field contract when replacing a
field component. Check that the import map is generated at startup/HMR or run the project's
`payload generate:importmap` command when needed; do not edit generated import-map output by hand.

## Reusable Payload plugins

A Payload plugin is a typed config transform. Give it defaults and allow callers to turn it off.
Copy/append config values rather than mutating shared arrays, and document composition order.

```ts
import type { Config, Plugin } from 'payload'

type BannerPluginOptions = { enabled?: boolean; label?: string }

export const bannerPlugin = (
  { enabled = true, label = 'Editorial tools' }: BannerPluginOptions = {},
): Plugin => (incomingConfig: Config): Config => {
  if (!enabled) return incomingConfig

  return {
    ...incomingConfig,
    admin: {
      ...incomingConfig.admin,
      components: {
        ...incomingConfig.admin?.components,
        providers: [
          ...(incomingConfig.admin?.components?.providers ?? []),
          { path: '/components/BannerProvider', serverProps: { label } },
        ],
      },
    },
  }
}
```

Validate plugin options early, avoid adding a collection whose slug collides with the host, and make
every injected collection, global, field, endpoint, dependency, and component path visible in the
README. Test composition with an existing config, not only an empty one.

## Official sources

- [Payload configuration](https://payloadcms.com/docs/configuration/overview)
- [Collection configs](https://payloadcms.com/docs/configuration/collections)
- [Global configs](https://payloadcms.com/docs/configuration/globals)
- [Custom components](https://payloadcms.com/docs/custom-components/overview)
- [Building a Payload plugin](https://payloadcms.com/docs/plugins/build-your-own)
