# Drift, rollback, and incidents

## Before a consequential change

Capture the narrowest useful snapshot: exact object/config/runtime identity, revision or checksum,
status/access state, relevant dependencies, backup type/location/owner, and rollback command/path.
Keep backup exports outside the public web root and never expose their contents. A backup existing
is not evidence that restore was tested.

Immediately before a write, revalidate target identity and drift. For enrolled content, use
[content-as-code-and-concurrency.md](content-as-code-and-concurrency.md). For other REST changes,
refetch the stable object and stop on an unexpected modified value/content change. For WP-CLI/IaC,
reuse the discovered runtime and exact scope; never apply to a guessed host/service/path.

## Recovery units

- content object/revision and metadata;
- menus/navigation;
- media attachment and references;
- theme/child-theme files, templates, patterns, global styles, and builder state;
- plugin package/version, activation, options, scheduled events, custom tables, and connections;
- database/config/runtime/IaC snapshot;
- cache/CDN, maintenance, noindex, consent, and publication state.

## Incident sequence

1. Stop further mutation and preserve first evidence.
2. Reconfirm exact target identity and current state.
3. Classify source, content, runtime, rendering, integration, provider, or deployment failure.
4. Choose repair-forward or rollback only under the applicable approval gate.
5. Re-read and re-verify every affected surface.
6. Record residual drift, cache/recrawl delay, provider delay, and follow-up work.

Do not retry an unknown-outcome write blindly. Do not use broad reset, deletion, search-replace,
clean import, cache purge, or database restore as diagnosis. Keep rollback and production outside
the local/PR claim unless separately evidenced.
