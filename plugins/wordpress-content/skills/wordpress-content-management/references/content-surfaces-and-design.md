# WordPress content hierarchy

Use the existing WordPress content hierarchy instead of treating a rendered page as one HTML blob.

1. **Theme foundation:** active theme, templates, template parts, global styles, typography, colors,
   spacing, and editor constraints.
2. **Blocks:** core and site-registered components available on both local and live sites.
3. **Patterns:** repeatable synced or unsynced compositions of those blocks.
4. **Page and post layout:** the route-specific arrangement of patterns and blocks.
5. **Copy and media:** approved words, links, images, captions, embeds, and metadata.

Start each task by inspecting only the relevant local surfaces. Preserve URLs, IDs, navigation,
forms, translations, structured data, analytics/consent behavior, and media relationships unless the
request explicitly changes them.

Theme or plugin source files are outside this workflow. Use editor-exposed theme styles and existing
registered components. If a source-code change is required, report it as a separate dependency and
continue with any content work that remains valid.
