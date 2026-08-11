---
name: amsoft-youtube-library-sync
description: Incrementally retrieve authorized YouTube playlist and channel items with bounded selection, protected browser-exported cookies, resumable downloads, and verified archive semantics.
---

# YouTube Library Sync

Create bounded, rerun-safe archives for authorized YouTube playlists or channels. A channel URL is
not authorization to retrieve all of its media.

Before first use, read [onboarding.md](references/onboarding.md). For every run, read
[sync-and-recovery.md](references/sync-and-recovery.md). Authenticated sync also requires the
cookie workflow in the media skill.

Run from the plugin root:

- `python3 <plugin-root>/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py sync REQUEST.json --result-file RESULT.json`

## Required workflow

1. Establish the exact playlist/channel URL, rights basis, public/authenticated mode, output root,
   and retention purpose.
2. Inspect metadata first. Bound the run with playlist selection and `max_items` no greater than
   100. Do not infer “all” from a channel URL.
3. Choose formats, subtitles, post-processing, pacing, timeout, and partial-file policy.
4. Preview the redacted plan. Explain that the task-owned
   `.youtube-download-archive.txt` stores successful extractor IDs and makes reruns incremental.
5. Execute. Successful verified items enter the archive; partial and failed items must remain
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
