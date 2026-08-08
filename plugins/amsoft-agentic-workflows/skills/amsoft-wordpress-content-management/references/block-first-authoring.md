# Block-first authoring and migration

WordPress Content is block-first. For new content and every content refactor,
never use the Custom HTML block (`core/html`), a raw HTML blob, HTML stored in
an unrelated block attribute, or convert rendered HTML back into post content.
HTML serialized by a registered block is normal; using HTML as the authoring
model is not.

## Component decision order

Use this order for every required section or component:

1. **Existing registered block:** inspect the site's editor and block registry,
   then use a core or site-registered block that already owns the required
   structure and behavior.
2. **Pattern composed from registered blocks:** when a composition repeats,
   reuse an existing pattern or create a pattern from registered blocks. State
   whether it is synced or unsynced and preserve intentional per-instance
   content.
3. **New registered block:** when neither existing blocks nor a pattern can
   express the requirement, stop the content mutation and give WordPress
   DevOps a concrete static or dynamic block requirement. Include the editor
   controls, attributes, output contract, accessibility behavior, styles,
   compatibility, migration mapping, and rendered checks. Resume the content
   change only after the block is released and discovered on the target site.

Do not use Custom HTML as a temporary shortcut while waiting for a block. Do
not disguise raw HTML in a Shortcode, Code, Paragraph, Group, or another block.
If a supported embed, Shortcode, or legacy integration is genuinely required,
use its registered block and record the dependency; do not paste its rendered
output into Custom HTML.

## Inventory and target design

Before proposing a change, read the exact raw edit-context source and parse its
serialized block tree. Inventory:

- every block name, nesting relationship, reusable block or pattern reference,
  and unsupported or invalid block;
- every `core/html` occurrence and raw HTML fragment, including scripts,
  styles, forms, embeds, event handlers, IDs, classes, and data attributes;
- the target site's registered block types, variations, patterns, templates,
  theme supports, and editor constraints; and
- links, media, structured data, forms, analytics, consent, localization, and
  other behavior that the target must preserve.

Design the target as serialized registered blocks and explicit pattern or
component references. A front-end DOM snapshot is verification evidence only;
it is not target block source.

## Legacy Custom HTML migration

Treat existing Custom HTML as migration input, never as the target state.
Migrate one stable page, post, template, or pattern at a time:

1. Resolve the object by stable ID and canonical URL and capture its status,
   modified time, revision, template, and exact raw source digest.
2. Save the minimum rollback fields outside the write payload and preserve the
   original Custom HTML source until the migration is verified.
3. Map each fragment and dependency to an existing registered block, a pattern
   composed from registered blocks, or a separately released registered block.
4. Build and review a target payload that contains no `core/html` block and no
   disguised raw HTML blob.
5. Refetch immediately before the write. Stop on source, revision, object,
   status, template, registered-block, or dependency drift.
6. Apply only the approved object and fields; never run an implicit bulk
   conversion.
7. Read back the edit-context source, parse it, reload it in the editor, save it
   without changes when safe, and parse it again. Confirm that the editor did
   not recover, invalidate, or rewrite blocks unexpectedly.
8. Verify the rendered result and required behavior before selecting another
   object.

If exact behavior cannot be mapped without executable inline markup or an
unregistered component, stop. Preserve the current object and route the missing
registered block or supported integration to DevOps instead of weakening this
contract.

## Target acceptance

A block-first target is acceptable only when:

- its serialized source parses without invalid, recovered, or unsupported
  blocks;
- every block and pattern is registered on the exact target environment;
- it contains no Custom HTML block and no raw HTML authoring workaround;
- synced and unsynced pattern behavior matches the approved ownership model;
- an editor open/save/reload round trip preserves the intended block tree;
- desktop and mobile rendering, links, media, forms, structured data, keyboard
  operation, focus order, contrast, language variants, and console/network
  behavior pass for the affected surface; and
- the rollback source and object identity remain available until acceptance is
  complete.
