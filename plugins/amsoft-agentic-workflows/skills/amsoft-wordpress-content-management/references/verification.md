# WordPress Content verification

Verification must match the surface changed.

## Before a write

- re-read the exact object by stable ID and canonical URL;
- compare its modified time/revision, publication state, and approved fields
  with the planned baseline;
- parse the raw edit-context source and recheck the registered block types,
  patterns, reusable references, legacy Custom HTML occurrences, invalid
  blocks, and dependencies used by the approved target;
- confirm the Application Password contract still identifies the same site,
  environment, username, endpoint, and scope; and
- capture only the rollback fields needed for the exact object.

## After a write

- fetch the exact object and compare the intended fields, ID, revision, slug,
  media association, and draft/published state;
- parse the saved source and confirm every block and pattern is registered on
  the exact environment, the target contains no `core/html` block or disguised
  raw HTML blob, and synced/unsynced pattern behavior matches the approval;
- open the exact object in the block editor, check for invalid or recovered
  blocks, and verify that a safe save/reload round trip preserves the intended
  block tree;
- open the canonical preview or public URL logged out;
- inspect the affected desktop and mobile layout, links, media, captions,
  focus order, keyboard behavior, contrast, console/network failures, and
  language variants; and
- report cache/CDN/indexing limitations and the content rollback or draft
  path.

Do not call a REST response, HTTP 200, wp-admin save notice, or screenshot
alone proof of a completed user-facing change.

For a legacy Custom HTML migration, keep the original raw source and bounded
rollback fields until both editor round-trip and rendered verification pass.
Verify one object before beginning another; a successful sample is not evidence
that a bulk conversion is safe.
