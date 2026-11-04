# Research basis

Checked 2026-07-29 against:

- [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md) for CLI, formats,
  playlists, subtitles, post-processing, structured output, and runtime dependencies;
- [yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ) for Netscape cookies, archives, and
  rate-limit troubleshooting;
- [yt-dlp YouTube extractor guidance](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#youtube)
  for account-cookie rotation, restriction risk, request pacing, and OAuth limitations;
- [yt-dlp PO Token guide](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide) for current,
  changing PO-token enforcement;
- [YouTube Terms](https://www.youtube.com/static?template=terms) for download, automation, and
  circumvention restrictions.

The implementation was designed against yt-dlp `2026.07.04`. Recheck upstream documentation for
live use because YouTube extraction behavior and supported clients change frequently.
