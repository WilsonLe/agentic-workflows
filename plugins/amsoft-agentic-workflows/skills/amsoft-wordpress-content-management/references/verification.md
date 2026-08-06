# WordPress Content verification

Verification must match the surface changed.

## Before a write

- re-read the exact object by stable ID and canonical URL;
- compare its modified time/revision, publication state, and approved fields
  with the planned baseline;
- confirm the Application Password contract still identifies the same site,
  environment, username, endpoint, and scope; and
- capture only the rollback fields needed for the exact object.

## After a write

- fetch the exact object and compare the intended fields, ID, revision, slug,
  media association, and draft/published state;
- open the canonical preview or public URL logged out;
- inspect the affected desktop and mobile layout, links, media, captions,
  focus order, keyboard behavior, contrast, console/network failures, and
  language variants; and
- report cache/CDN/indexing limitations and the content rollback or draft
  path.

Do not call a REST response, HTTP 200, wp-admin save notice, or screenshot
alone proof of a completed user-facing change.
