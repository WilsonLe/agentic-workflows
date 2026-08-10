# Block-first WordPress authoring

Build content in this order: active theme, registered blocks, reusable patterns, then page layout and
copy. The theme supplies the design foundation; blocks supply the editable components; patterns
supply repeatable compositions; pages arrange those pieces for the actual route.

## Blocks

Prefer a core block, then an existing site-registered block. Never use the Custom HTML block
(`core/html`), a raw HTML blob, HTML hidden in another block attribute, or rendered HTML converted
back into post content. HTML serialized by a registered block is normal.

If the registered block set cannot express a requirement, leave that part unchanged and report the
missing component. A content task must not grow into PHP, JavaScript, CSS, theme, or plugin source
work.

## Patterns

Use a pattern when a block composition repeats. Reuse an existing pattern when it fits; otherwise
compose one from blocks registered on both local and live sites. Choose synced behavior for centrally
owned repeated content and unsynced behavior when each page owns its copy.

## Layout and copy

Assemble pages and posts only after theme, block, and pattern choices are settled. Preserve IDs,
slugs, status, links, templates, metadata, and relationships unless the request changes them. Use
approved copy and inspected media; do not invent business facts or image meaning.

Existing Custom HTML may be replaced only when the same result can be expressed with registered
blocks and patterns. Keep its original source in the temporary rollback snapshot until local and
live browser verification pass.
