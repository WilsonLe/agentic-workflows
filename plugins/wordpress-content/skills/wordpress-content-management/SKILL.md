---
name: wordpress-content-management
description: Run the standard WordPress content-management workflow for themes, registered blocks, patterns, page layouts, copy, and media. Work locally with temporary files, verify in a browser, then apply to the live site with a rollback ready. Use independently of the Standard Development Workflow; do not create Git branches, commits, issues, or pull requests.
---

# Standard WordPress Content Management Workflow

Use this skill for ordinary WordPress site-building and content work. It is a lightweight operational
workflow, not a software-development workflow. Do not invoke `standard-development-workflow`, create
a worktree, open an issue or pull request, or make a Git commit for this work.

Use temporary, secret-safe working files to prepare the exact WordPress payloads or commands. Run
them against the local WordPress site first. Once the local result passes browser verification, take
a live rollback snapshot, apply the same content change to the live site, and verify it there. If the
live check fails, roll back immediately and report the failure.

## Scope

This workflow owns the user-facing content surface:

- the currently installed theme and its editor-exposed styles, templates, and layout constraints;
- core and already registered site blocks;
- synced and unsynced patterns made from those blocks;
- page and post layouts, navigation, copy, images, media, and embeds; and
- local and live rendered verification.

It does not edit theme or plugin source, install server software, change hosting, repair filesystems,
or manage databases. If a missing capability requires PHP, JavaScript, CSS, theme/plugin files,
hosting, or infrastructure changes, report that dependency separately. Do not turn the content task
into a development project.

## Authentication

Use an existing authorized administrator session, WP-CLI connection, or site-scoped WordPress
Application Password. Resolve secrets from the user's approved local credential store or a native
masked prompt; never ask for or print a secret in chat, a command, a temporary payload, or logs.
Read [application-password-contract.md](references/application-password-contract.md) when an
Application Password is needed.

## Working order

Follow this order so lower-level choices support everything above them:

1. **Theme:** identify the active local theme and the equivalent live theme. Inspect its editor-
   exposed styles, templates, typography, colors, and spacing. Use the chosen installed theme as the
   design foundation before shaping content.
2. **Blocks:** inventory the registered blocks available on both sites. Prefer core blocks, then
   existing site-registered blocks. Never use Custom HTML as a shortcut.
3. **Patterns:** reuse an existing pattern or compose a new synced or unsynced pattern from those
   registered blocks when a section repeats.
4. **Page layout:** assemble the actual page or post layout from the selected theme, blocks, and
   patterns. Preserve the intended IDs, slugs, status, links, metadata, and relationships.
5. **Copy and media:** add the approved wording and inspected media without inventing facts,
   descriptions, prices, availability, ingredients, rights, or image meaning.

Read [block-first-authoring.md](references/block-first-authoring.md) for the authoring rules and
[content-surfaces-and-design.md](references/content-surfaces-and-design.md) for the content hierarchy.

## Local-first execution

1. Inspect the relevant local objects and their rendered routes.
2. Create a private temporary directory with `mktemp -d`; keep payloads, exports, and rollback data
   there, outside the repository. Remove it when the task is accepted and rollback is no longer
   needed.
3. Write only the files needed to establish the chosen blocks, patterns, layouts, copy, and media.
4. Run the site's existing authorized REST, administrator, or WP-CLI path against local WordPress.
5. Open the affected local routes in a real browser at the required desktop and mobile sizes. Check
   layout, text, links, media, navigation, keyboard use, console errors, and obvious overflow.
6. Iterate locally until the requested result looks and works right. Temporary files may be updated;
   do not create repository artifacts or Git history.

## Live apply and rollback

When the request includes live delivery, a passing local browser check is the execution gate; do not
add a Git, issue, PR, or development-workflow approval stage.

1. Confirm the live site and target objects match the intended theme, IDs, slugs, and current
   content closely enough for the prepared change.
2. Capture a rollback snapshot of every live object and setting that will change. Keep it outside
   the repository and confirm it can be reapplied.
3. Apply only the verified local payload to the live site through the existing authorized path.
4. Read back the changed objects and verify the exact live routes in a logged-out browser at desktop
   and mobile sizes.
5. If readback or live browser verification fails, restore the rollback snapshot immediately,
   verify the restored site, and stop. Do not continue applying more pages after a failed check.

For a local-only request, stop after local browser verification. For deletion or a change outside
the requested content scope, ask before acting. Otherwise the user's request authorizes this
local-first content workflow without extra process gates.

Read [verification.md](references/verification.md) for the concise acceptance checklist and
[routing-and-boundaries.md](references/routing-and-boundaries.md) only when the task genuinely
crosses into code or infrastructure.
