# WordPress Content

AMSoft's standard WordPress content-management workflow.

This plugin captures practical best practices for building and updating WordPress content without
the Standard Development Workflow. It uses no Git branches, commits, issues, pull requests, or
content-as-code synchronization.

The working order is:

1. confirm the installed theme and its editor-exposed design foundation;
2. choose registered core or site blocks;
3. compose reusable synced or unsynced patterns;
4. build the actual page or post layouts;
5. add approved copy and inspected media;
6. verify the result in a local browser;
7. capture a live rollback snapshot, apply the same payload, and verify live; and
8. roll back immediately if live readback or browser verification fails.

Working payloads and rollback exports belong in a private temporary directory outside the
repository. The workflow may use the site's existing REST API, administrator UI, or WP-CLI path.
Secrets stay in an approved local credential store or native masked prompt and never enter chat,
temporary payloads, or logs.

The plugin uses the current installed theme, registered blocks, and supported WordPress surfaces.
It does not edit theme/plugin source or turn a missing component into a development project. New and
refactored content never uses the Custom HTML block (`core/html`) or disguised raw HTML.

Example prompt:

```text
Use WordPress Content to build this page locally from the active theme, registered blocks, and
patterns. Verify it in the browser, then back up and apply it live; roll back if live verification
fails. Do not use Git or Standard Development Workflow.
```
