# Safe inspection operations

The wrapper disables inherited yt-dlp configuration, external plugin directories, remote
components, watched-state mutation, comments, and executable hooks. It accepts only HTTPS YouTube
hosts and produces an allowlisted metadata projection without format URLs, request headers,
cookies, account/session identifiers, or local credential paths.

Playlist and channel results are bounded. Flat playlist inspection may omit metadata; label those
fields unknown rather than escalating automatically to full extraction.

Authenticated inspection uses only the plugin-managed protected cookie file. Never accept another
cookie path at operation time and never show the protected path in a command preview.
