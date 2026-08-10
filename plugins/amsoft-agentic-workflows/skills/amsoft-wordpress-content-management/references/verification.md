# WordPress content verification

## Local

- Confirm the intended theme and registered blocks are active.
- Read back the saved blocks, patterns, page layouts, copy, media, IDs, slugs, and status.
- Open the affected local routes in a real browser at desktop and mobile sizes.
- Check layout, text, links, media, navigation, keyboard use, console errors, and overflow.
- Iterate locally until the requested result looks and works right.

## Live

- Before writing, save a re-applicable snapshot of every live object and setting being changed.
- Apply the same locally verified payload through the authorized WordPress path.
- Read back the live objects and open the exact live routes logged out at desktop and mobile sizes.
- Check the same behavior verified locally, plus obvious cache or CDN differences.
- If any required readback or browser check fails, restore the snapshot immediately and verify the
  restored live routes. Stop before applying another page.

A command exit code, API response, HTTP 200, admin save notice, or screenshot alone is not browser
verification.
