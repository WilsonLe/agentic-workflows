# Research basis

This skill uses the same dated upstream sources and limitations documented by
`youtube-content-inspection/references/research-basis.md`.

Important yt-dlp feature surfaces include format selection/sorting, audio extraction, subtitle and
thumbnail writing/embedding, metadata and chapters, `--download-sections`, `--split-chapters`,
SponsorBlock, bounded retries/pacing, and experimental `--live-from-start`.

Checked 2026-07-29 against yt-dlp `2026.07.04`. Reverify before live operation.


Cross-platform URL routing checked 2026-10-19 against the upstream
[supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) and
[authentication options](https://github.com/yt-dlp/yt-dlp#authentication-options).
The installed extractor decides whether a URL works; inclusion in that list is not
proof of a successful download. Retain YouTube-specific PO-token and private-session
advice only for YouTube. SponsorBlock and live-from-start are extractor-dependent.
