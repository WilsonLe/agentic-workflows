---
name: youtube-media-operations
description: Retrieve authorized video from YouTube and other yt-dlp-supported platforms, including audio, subtitles, thumbnails, chapters, sections, and experimental live media through bounded yt-dlp operations and Codex built-in browser cookies.
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

# Media Operations with yt-dlp

Use this existing skill for YouTube and every other platform supported by the installed
[yt-dlp extractors](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), such as
Vimeo, TikTok, Instagram and Dailymotion. The `youtube-` skill and helper names remain
compatible entry points. Site support, metadata and optional features vary by extractor;
report unsupported URLs or unavailable features instead of promising every item works.


Retrieve only media the user is authorized to download or transform. Authentication is not a
rights basis.

Before first use, read [onboarding.md](references/onboarding.md). Before authenticated use, read
[cookie-authentication.md](references/cookie-authentication.md). For every operation, read
[operation-contract.md](references/operation-contract.md). Read
[research-basis.md](references/research-basis.md) when upstream behavior matters.

The shared scripts are at the plugin root. Run them by path from the user's
working directory, keeping request, result, and output files there rather than in
the plugin directory:

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_cookie_store.py status`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py preflight`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py plan REQUEST.json`
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/youtube_yt_dlp.py download REQUEST.json --result-file RESULT.json`

## Required workflow

1. Establish an exact HTTP(S) media URL, requested outputs, and one explicit rights-basis category
   plus the user's statement. Stop when no lawful or service-authorized basis is supplied.
2. Inspect publicly first unless account-gated access is already explicit.
3. When the user requests browser cookies, use `auth_mode: codex_browser` and the
   concealed Codex in-app browser transport in the cookie contract. Do not switch
   browser accounts or print cookies. Legacy `browser_cookie_file` is YouTube-only.
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
8. Run the approved request. For `codex_browser`, invoke `runWithCodexCookies`
   from the cookie contract; other modes use the Python CLI directly. Do not add raw flags.
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
