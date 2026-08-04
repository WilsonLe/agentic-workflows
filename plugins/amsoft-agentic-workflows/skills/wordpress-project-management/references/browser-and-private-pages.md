# Browser and private-page verification

Use the real requested browser/control channel when the acceptance claim depends on it. Preflight
origin, target environment, authentication identity, page status, and requested capture before
performing a long visual run.

## Preflight

Record:

- local loopback, staging, or production origin and canonical URL;
- authenticated account/scope without recording cookies, tokens, passwords, or private values;
- object ID/slug/status and whether it is private, draft, password-protected, noindex, coming-soon,
  staging-only, or public;
- viewport/device matrix, required interactions, and whether fresh video/capture is requested;
- portal/iframe, consent, cache/CDN, and browser-control constraints.

## Evidence

For affected surfaces, inspect DOM/accessible names, landmarks/headings, keyboard/focus order,
expanded/collapsed state, links/deep links, responsive layout, media, forms, console/network evidence,
visible errors, and cache behavior. Use authenticated proof only for private/admin claims;
use logged-out proof for public claims.

If the browser or Chrome CDP is blocked, including loopback control errors such as
`ERR_BLOCKED_BY_CLIENT`, mark that surface `blocked` or `partial`. Do not substitute REST, a
screenshot, wp-admin, or a later production run and report the requested browser claim as passed.

Video/fresh capture is evidence only when the requested capture exists, is tied to the final
committed/relevant target, and has an explicit filename/viewport/URL mapping. Rehearsal captures do
not prove the final candidate.
