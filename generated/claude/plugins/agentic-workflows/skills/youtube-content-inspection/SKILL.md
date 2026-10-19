---
name: youtube-content-inspection
description: Inspect videos from YouTube and all other yt-dlp-supported platforms, playlists, channels, formats, subtitles, thumbnails, chapters, and live state through bounded, media-free yt-dlp operations.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Required: yt-dlp** — Install yt-dlp; install FFmpeg for media transformations.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

<!-- claude-code-notes:start -->
## Claude Code

This skill's references write `<plugin-root>` for `${CLAUDE_PLUGIN_ROOT}`. Use those absolute paths in commands you run or give to the user; never show the placeholders.

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

<!-- claude-code-notes:end -->

# Content Inspection with yt-dlp

Use this existing skill for YouTube and every other platform supported by the installed
[yt-dlp extractors](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), such as
Vimeo, TikTok, Instagram and Dailymotion. The `youtube-` skill and helper names remain
compatible entry points. Site support, metadata and optional features vary by extractor;
report unsupported URLs or unavailable features instead of promising every item works.


Inspect first. Do not retrieve media merely to answer a metadata, format, subtitle, playlist, or
availability question.

Before first use, read [onboarding.md](references/onboarding.md). For every operation, read
[safe-operations.md](references/safe-operations.md). Read
[research-basis.md](references/research-basis.md) when upstream behavior or limitations matter.

The shared scripts are at the central plugin root. Run them by path from the user's
working directory, keeping request, result, and output files there rather than in
the plugin directory:

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py preflight`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py inspect REQUEST.json`

Use the request schema in this skill's `schemas/` directory. Inspection requests set
`operation` to `inspect`; they do not require a rights basis or output directory.

## Workflow

1. Validate that every input is an exact HTTP(S) media URL. Do not turn free text into a search.
2. Default to `auth_mode: public`. When browser authentication is requested, use
   `auth_mode: codex_browser` and the concealed transport in the media skill's
   [cookie contract](../youtube-media-operations/references/cookie-authentication.md).
   Legacy `browser_cookie_file` remains restricted to the protected YouTube record.
3. Bound playlist/channel inspection with an explicit policy, item range when applicable, and
   `max_items` no greater than 100.
4. Preview the redacted command with `plan`.
5. Run `inspect` and use only its sanitized JSON. Do not attach raw yt-dlp debug output or raw info
   JSON to evidence.
6. State unavailable fields as unknown. Extractor metadata is not guaranteed.
7. Classify failures such as authentication required, rate limited, PO token, unavailable, or
   runtime missing without attempting a bypass.

## Boundaries

- Inspection never writes media, subtitles, thumbnails, comments, or live chat.
- Comments and live chat remain excluded because they add requests and may contain personal data.
- Never use raw yt-dlp flags, user config, external plugins, remote components, file URLs,
  executable hooks, proxies, impersonation, geo-bypass, or direct cookie values.
- Browser cookies prove account authority only. They do not establish media rights.
- If the request becomes a download or archive, route to `youtube-media-operations` or
  `youtube-library-sync`.

## Completion

Report the exact inspected URL scope, public or authenticated mode, item count and truncation,
available formats/languages/chapters/live state, unknowns, warnings, and the sanitized evidence
file when one was requested.
