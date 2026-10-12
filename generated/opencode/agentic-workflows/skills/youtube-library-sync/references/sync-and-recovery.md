# Sync and recovery

The sync wrapper places `.youtube-download-archive.txt` inside the selected output root and passes
it to yt-dlp's download-archive feature. yt-dlp records successful downloads; the wrapper also
verifies final files and hashes in its result manifest.

Use:

- `playlist_policy: playlist`;
- an explicit `max_items` from 1 through 100;
- optional bounded `playlist_items`;
- no-overwrite, resumable partials, bounded retries, and account-aware request pacing.

Mixed outcomes are normal. Distinguish:

- `verified`: final output exists and is hashed;
- `skipped-existing`: archive/no-overwrite prevented duplicate work;
- `partial`: resumable file remains;
- `failed`: item remains eligible for retry;
- `auth-required`, `rate-limited`, `po-token`, or `unavailable`: stop or correct the stated cause.

Do not remove the archive to force a rerun. If archive recovery is required, first preserve a copy,
compare it with verified outputs, and obtain approval before replacing task state.
