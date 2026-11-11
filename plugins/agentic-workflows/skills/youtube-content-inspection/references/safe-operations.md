# Safe inspection operations

The wrapper disables inherited yt-dlp configuration, external plugin directories, remote
components, watched-state mutation, comments, and executable hooks. It accepts credential-free HTTP(S) media URLs and produces an allowlisted metadata projection without format URLs, request headers,
cookies, account/session identifiers, or local credential paths.

Playlist and channel results are bounded. Flat playlist inspection may omit metadata; label those
fields unknown rather than escalating automatically to full extraction.

Authenticated inspection uses the concealed `codex_browser` bridge described in the media
skill's cookie contract, or the legacy YouTube-only protected record. Cookie values never
cross model-visible output. Never accept another cookie path at operation time or show
credential paths in previews. Public mode never reads browser cookies.
