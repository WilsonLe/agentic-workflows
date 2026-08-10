# WordPress content boundary

WordPress Content is independent of Standard Development Workflow. For theme-backed content,
registered blocks, patterns, layouts, copy, media, and rendered pages, use this workflow directly.
Do not add worktrees, Git branches, commits, issues, pull requests, pinned plans, or content-as-code
synchronization.

Use private temporary files outside the repository and the site's existing authorized REST,
administrator, or WP-CLI path. Verify locally in a browser before live application. Back up the
affected live content first and roll back immediately if live verification fails.

Only route out of this workflow when the requested result genuinely requires source code or
infrastructure: theme/plugin installation or file edits, PHP, JavaScript, CSS, server software,
hosting, filesystem repair, database maintenance, or deployment configuration. Report that as a
separate dependency; do not wrap ordinary content work in a development workflow.
