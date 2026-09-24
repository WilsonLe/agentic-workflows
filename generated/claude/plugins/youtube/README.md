# YouTube

Agentic Workflows YouTube plugin provides bounded, evidence-producing workflows around the external
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp) command-line tool.

It includes:

- `youtube-content-inspection` for media-free metadata, format, subtitle, thumbnail, chapter,
  playlist, channel, and live-state inspection;
- `youtube-media-operations` for authorized video, audio, subtitle, thumbnail, chapter, section,
  and experimental live retrieval;
- `youtube-library-sync` for bounded, rerun-safe playlist and channel archives.

## Runtime

Install a current stable yt-dlp release, FFmpeg/ffprobe, and a supported JavaScript runtime. The
implementation was designed against yt-dlp `2026.07.04`; YouTube extraction behavior is
drift-sensitive, so preflight reports the runtime actually found.

The plugin does not bundle yt-dlp, FFmpeg, JavaScript runtimes, PO-token providers, browser
extensions, or account credentials.

## Browser-exported cookie authentication

Public mode is the default. Account-gated operations use a YouTube-only Netscape cookie file:

1. Open one private/incognito browser window and sign in to YouTube.
2. In that same session, navigate to `https://www.youtube.com/robots.txt`.
3. Use a reviewed local browser export mechanism to export only `youtube.com` cookies in
   Netscape format.
4. Close the private/incognito session without reopening it.
5. From this plugin's root, install the export:

   `python3 scripts/youtube_cookie_store.py install /absolute/path/to/export.txt`

The helper validates the file locally, rejects non-YouTube domains, and installs it at
`~/.config/agentic-workflows/youtube/cookies.txt` with owner-only protection. It never prints cookie names or
values. Use `status`, `verify`, `rotate`, or `revoke` for the rest of the lifecycle.

Do not paste cookies into chat. The original export remains sensitive until the user separately
approves moving it to Trash after successful verification.

## Safety boundaries

- Media retrieval requires a stated rights basis. Authentication does not establish copyright
  permission.
- Raw yt-dlp flags, user configuration, external plugins, remote components, executable hooks,
  file URLs, proxies, impersonation, geo-bypass, and DRM circumvention are not exposed.
- Account-cookie use can trigger YouTube rate limits or account restrictions. The workflow uses
  public mode first and bounded pacing.
- PO-token enforcement changes frequently. The plugin reports the condition but does not install
  a provider or accept token values.
- User downloads, archives, partial files, and the protected cookie record are preserved during
  plugin rollback.
