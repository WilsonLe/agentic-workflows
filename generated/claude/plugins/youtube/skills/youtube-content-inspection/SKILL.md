---
name: youtube-content-inspection
description: Inspect YouTube videos, playlists, channels, formats, subtitles, thumbnails, chapters, and live state through bounded, media-free yt-dlp operations.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer and the package dependencies before running its helper scripts.
- **Required: yt-dlp** — Install yt-dlp; install FFmpeg for media transformations.

<!-- catalog-prerequisites:end -->

# YouTube Content Inspection

Inspect first. Do not retrieve media merely to answer a metadata, format, subtitle, playlist, or
availability question.

Before first use, read [onboarding.md](references/onboarding.md). For every operation, read
[safe-operations.md](references/safe-operations.md). Read
[research-basis.md](references/research-basis.md) when upstream behavior or limitations matter.

The shared scripts are at the plugin root. Run commands from the plugin root:

- `python3 <plugin-root>/scripts/youtube_yt_dlp.py preflight`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py inspect REQUEST.json`

Use the request schema in this skill's `schemas/` directory. Inspection requests set
`operation` to `inspect`; they do not require a rights basis or output directory.

## Workflow

1. Validate that every input is an exact HTTPS YouTube URL. Do not turn free text into a search.
2. Default to `auth_mode: public`. Use the protected cookie record only when the user explicitly
   requests account-gated inspection or public inspection proves authentication is required.
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
