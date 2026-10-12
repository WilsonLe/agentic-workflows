# Media operation contract

Every request uses schema version 1 and a controlled vocabulary. Media operations require:

- `operation: download`;
- one to twenty exact HTTPS YouTube URLs;
- `auth_mode`;
- `rights_basis.category` and the user's short statement;
- `output_root`;
- single/playlist policy and item cap;
- video/audio/section/live mode and applicable constraints.

The wrapper disables hidden yt-dlp config, external plugins/components, watched-state mutation,
comments, executable hooks, and overwrite. It uses direct argv and a minimal environment.

Output names use bounded extractor fields under uploader/playlist directories. The wrapper rejects
symlinked roots and verifies every reported file remains under the selected root. Its result
manifest contains relative paths, sizes, SHA-256 hashes, sanitized metadata, and a redacted command.

Expected failure categories include authentication required, invalid/expired cookie, rate limit,
PO token, unavailable/private/deleted content, missing FFmpeg/JavaScript runtime, filesystem
failure, timeout, and mixed playlist results. Report the category; do not paste raw debug output.
