---
name: youtube-media-operations
description: Retrieve authorized YouTube video, audio, subtitles, thumbnails, chapters, sections, and experimental live media through bounded yt-dlp operations and protected browser-exported cookies.
---

# YouTube Media Operations

Retrieve only media the user is authorized to download or transform. Authentication is not a
rights basis.

Before first use, read [onboarding.md](references/onboarding.md). Before authenticated use, read
[cookie-authentication.md](references/cookie-authentication.md). For every operation, read
[operation-contract.md](references/operation-contract.md). Read
[research-basis.md](references/research-basis.md) when upstream behavior matters.

The shared scripts are at the plugin root. Run from the plugin root:

- `python3 <plugin-root>/scripts/youtube_cookie_store.py status`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py preflight`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 <plugin-root>/scripts/youtube_yt_dlp.py download REQUEST.json --result-file RESULT.json`

## Required workflow

1. Establish an exact HTTPS YouTube URL, requested outputs, and one explicit rights-basis category
   plus the user's statement. Stop when no lawful or service-authorized basis is supplied.
2. Inspect publicly first unless account-gated access is already explicit.
3. For authenticated mode, verify the plugin-managed cookie record is configured and protected.
   Never accept another cookie path or raw value.
4. Choose bounded settings: one video by default, maximum resolution/file size, video or audio,
   subtitle languages, thumbnail/metadata/chapter behavior, sections, SponsorBlock behavior, rate,
   pacing, timeout, and output root.
5. Treat SponsorBlock removal as a content modification that requires the rights basis to cover
   modification.
6. Treat `live-from-start` as experimental. Require `media_mode: live` and
   `experimental_live_from_start: true`; state cancellation and partial-file behavior.
7. Run `plan` and show the user URL count, output root, format constraints, authentication mode,
   overwrite policy, bounds, post-processing, and experimental flags. The cookie path remains
   redacted.
8. Run the approved request. Do not add raw yt-dlp flags.
9. Verify result JSON, file existence, sizes, hashes, and per-item status. Report partials and
   unknown outcomes; never call a failed item complete.

## Boundaries

- No DRM, geo, IP, bot, account, or platform-control bypass.
- No raw config, plugins, remote components, external downloaders, executable hooks, proxies,
  impersonation, file URLs, arbitrary postprocessor arguments, or PO-token values.
- No overwrite. Existing user files are preserved.
- No comments/live-chat collection or YouTube write API.
- Rollback never deletes downloads, archives, partial files, or protected cookies.

## Completion

Report the rights basis as user-supplied, the exact URL/item count, public/authenticated mode,
selected media constraints, output files with hashes, sidecars/post-processing, partials,
warnings, and any upstream limitation such as PO-token enforcement.
