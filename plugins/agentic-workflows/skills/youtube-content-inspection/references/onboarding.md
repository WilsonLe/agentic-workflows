# Inspection onboarding

1. Run `python3 <plugin-root>/scripts/youtube_yt_dlp.py preflight`.
2. Confirm a current yt-dlp, FFmpeg/ffprobe, and either Deno or Node are available.
3. Use public mode first. When cookies are requested, use the concealed Codex bridge in the media skill cookie contract; the stored export remains YouTube-only.
4. Ask for exact media URLs and the smallest item bound needed.
5. Do not install or update dependencies without a separate user request.

Readiness is:

- `Ready`: required runtimes exist and public inspection can proceed;
- `Needs configuration`: runtime is missing or account-gated inspection needs protected cookies;
- `Needs input`: the exact URL or scope bound is missing.
