---
name: youtube-library-sync
description: Incrementally retrieve authorized playlist and channel items from yt-dlp-supported platforms with bounded selection, Codex built-in browser cookies, resumable downloads, and verified archive semantics.
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

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

<!-- claude-code-notes:end -->

# Library Sync with yt-dlp

Use this existing skill for YouTube and every other platform supported by the installed
[yt-dlp extractors](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), such as
Vimeo, TikTok, Instagram and Dailymotion. The `youtube-` skill and helper names remain
compatible entry points. Site support, metadata and optional features vary by extractor;
report unsupported URLs or unavailable features instead of promising every item works.


Create bounded, rerun-safe archives for authorized playlists or channels supported by yt-dlp. A channel URL is
not authorization to retrieve all of its media.

Before first use, read [onboarding.md](references/onboarding.md). For every run, read
[sync-and-recovery.md](references/sync-and-recovery.md). Authenticated sync also requires the
cookie workflow in the media skill.

Run the shared scripts by path from the user's working directory, keeping request,
result, and output files there rather than in the plugin directory:

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py sync REQUEST.json --result-file RESULT.json`

## Required workflow

1. Establish the exact playlist/channel URL, rights basis, public/authenticated mode, output root,
   and retention purpose.
2. Inspect metadata first. Bound the run with playlist selection and `max_items` no greater than
   100. Do not infer “all” from a channel URL.
3. Choose formats, subtitles, post-processing, pacing, timeout, and partial-file policy.
4. Preview the redacted plan. Explain that the task-owned
   `.youtube-download-archive.txt` stores successful extractor IDs and makes reruns incremental.
5. Execute through the media skill's concealed Codex transport for
   `auth_mode: codex_browser`, or directly for public/legacy modes. Successful verified items enter the archive; partial and failed items must remain
   eligible for retry.
6. Verify per-item results, output hashes, archive behavior, skipped-existing items, partials, and
   failures.
7. On rerun, preserve existing media and use no-overwrite plus the same output root/archive.

## Boundaries

- No unbounded channel crawling, search discovery, comments/live chat, or background scheduler.
- No automatic retry storm after rate-limit, account, or PO-token failures.
- Never edit the download archive manually while an operation is running.
- Never delete archive/media/partials during plugin rollback.
- Protected cookies are account credentials, not a rights basis.

## Completion

Report planned versus attempted versus verified counts, skipped archive IDs, partial/failed
categories, output root, archive location without contents, new files/hashes, bounds, and the next
safe rerun condition.
