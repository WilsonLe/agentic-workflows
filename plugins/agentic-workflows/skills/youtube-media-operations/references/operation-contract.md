# Media operation contract

Every request uses schema version 1 and a controlled vocabulary. Media operations require:

- `operation: download`;
- one to twenty exact HTTP(S) media URLs;
- `auth_mode`: `public`, `codex_browser`, or legacy YouTube-only `browser_cookie_file`;
- `rights_basis.category` and the user's short statement;
- `output_root`;
- single/playlist policy and item cap;
- video/audio/section/live mode and applicable constraints.

The wrapper disables hidden yt-dlp config, external plugins/components, watched-state mutation,
comments, executable hooks, and overwrite. It uses direct argv and a minimal environment. URL queries/fragments are retained for
extraction, including fragment-routed video/lecture identifiers. Sanitized evidence
omits non-YouTube query strings and all fragments; it is not a replay command.

Output names use bounded extractor fields under uploader/playlist directories.
Non-YouTube requests add an extractor namespace to avoid cross-site ID collisions;
YouTube-only requests retain their existing paths and archive filename. The wrapper rejects
symlinked roots and verifies every reported file remains under the selected root. Its result
manifest contains relative paths, sizes, SHA-256 hashes, sanitized metadata, and a redacted command.

`codex_browser` requires one HTTPS origin and the concealed stdin bridge in the cookie
contract. Its temporary cookie file is excluded from manifests and command previews.

Expected failure categories include unsupported URL, authentication required, invalid/expired cookie, rate limit,
PO token, unavailable/private/deleted content, missing FFmpeg/JavaScript runtime, filesystem
failure, timeout, and mixed playlist results. Report the category; do not paste raw debug output.
