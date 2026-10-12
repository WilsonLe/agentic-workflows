# YouTube inspection onboarding

1. Run `python3 <plugin-root>/scripts/youtube_yt_dlp.py preflight`.
2. Confirm a current yt-dlp, FFmpeg/ffprobe, and either Deno or Node are available.
3. Use public mode first. A protected cookie file is optional and only for account-gated content.
4. Ask for exact YouTube URLs and the smallest item bound needed.
5. Do not install or update dependencies without a separate user request.

Readiness is:

- `Ready`: required runtimes exist and public inspection can proceed;
- `Needs configuration`: runtime is missing or account-gated inspection needs protected cookies;
- `Needs input`: the exact URL or scope bound is missing.
