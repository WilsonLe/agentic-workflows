# Media downloads with yt-dlp

The existing YouTube component provides bounded workflows across all sites supported by the external
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp) command-line tool.

It includes:

- `youtube-content-inspection` for media-free metadata, format, subtitle, thumbnail, chapter,
  playlist, channel, and live-state inspection;
- `youtube-media-operations` for authorized video, audio, subtitle, thumbnail, chapter, section,
  and experimental live retrieval;
- `youtube-library-sync` for bounded, rerun-safe playlist and channel archives.

The skill names, helper paths, archive filename and request version remain compatible.
Platform recognition belongs to the installed yt-dlp extractors; supported sites and
optional subtitle/live/SponsorBlock features can change. Unsupported URLs return a
sanitized failure. HTTP(S) URLs are accepted in public mode; authenticated Codex mode
requires HTTPS.

## Runtime

Install a current stable yt-dlp release, FFmpeg/ffprobe, and a supported JavaScript runtime. The
implementation was designed against yt-dlp `2026.07.04`; YouTube extraction behavior is
drift-sensitive, so preflight reports the runtime actually found.

The plugin does not bundle yt-dlp, FFmpeg, JavaScript runtimes, PO-token providers, browser
extensions, or account credentials.

## Codex built-in browser cookies

Use `auth_mode: codex_browser` to authenticate with the current Codex in-app browser
session. The bundled `scripts/codex_browser_cookies.mjs` transport requests only the
current site's cookies through tab-scoped CDP, pipes them to the Python helper over
stdin and returns only sanitized results. Python validates cookie scope, creates an
owner-only temporary Netscape file for yt-dlp and removes it on success/failure/timeout.

Requires Codex tab-scoped CDP, host Node.js 18+, local Python and POSIX. Prepare a
request for one HTTPS origin, navigate the built-in tab there, then follow the exact
concealed invocation in
[cookie-authentication.md](skills/youtube-media-operations/references/cookie-authentication.md).
A missing capability or failed authentication is reported; no fallback to another
browser account or native cookie database occurs. No cookie values belong in chat.

The existing `browser_cookie_file` mode and `youtube_cookie_store.py` lifecycle
commands remain compatible for protected YouTube-only exports. They do not accept
cookies for other platforms. Public mode still requires no credentials.

## Safety boundaries

- Media retrieval requires a stated rights basis. Authentication does not establish copyright
  permission.
- Raw yt-dlp flags, user configuration, external plugins, remote components, executable hooks,
  file URLs, proxies, impersonation, geo-bypass, and DRM circumvention are not exposed.
- Account-cookie use can trigger platform rate limits or account restrictions. The workflow uses
  public mode first and bounded pacing.
- PO-token enforcement changes frequently. The plugin reports the condition but does not install
  a provider or accept token values.
- User downloads, archives, partial files, and the protected cookie record are preserved during
  plugin rollback.
