# ADR-0002: Use a concealed Codex browser cookie bridge in the existing media helpers

- Status: accepted
- Date: 2026-10-19
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User requested all-platform yt-dlp downloads and explicitly confirmed Codex built-in browser cookies; [tracking issue](https://github.com/WilsonLe/agentic-workflows/issues/53); routine design authority in Standard Development Workflow
- Supersedes: none
- Superseded by: none

## Context

The media helper restricted URL hosts and stored cookie exports to YouTube. The
requested downloader must follow yt-dlp's extractor coverage and use the current
Codex in-app browser session. Browser-level controls expose no cookie-export API,
but tab-scoped CDP supports Network.getCookies for the current origin. Credentials
must never appear in chat, argv, logs, manifests or committed files.

## Decision

Extend the existing Python request/command and cookie-store owners. Keep version-1
requests, skill names, helper paths and legacy YouTube export storage compatible.
Delegate credential-free HTTP(S) URL recognition to the installed yt-dlp rather
than maintaining a platform list. The legacy persistent cookie record stays
YouTube-only; a new explicit codex_browser mode requires one HTTPS origin.

A small host-side JavaScript transport owns only the Codex CDP capability and its
concealed subprocess channel. It requests cookies for the exact request URLs and
pipes the response to the Python helper's stdin. The existing cookie-store helper
validates scope and fields, rejects partitioned cookies, and supplies yt-dlp with
an owner-only temporary Netscape file. Normal success, failure and timeout unwind
that context. No new persistent credential store is created. The bridge returns
only the existing sanitized result contract; plans never read browser cookies.

The user's implementation request and explicit browser-source choice authorize
this design on 2026-10-19. Availability on other hosts, real account authentication,
review, merge and release remain separate evidence.

## Alternatives

Using yt-dlp's cookies-from-browser option would select a separate desktop browser
profile and could use a different account. Reading native cookie databases would
depend on undocumented storage/encryption and risk selecting a stale profile.
Returning CDP cookies to the agent or writing an export in the workspace would
expose credentials. A second downloader/store would duplicate existing validation,
execution and lifecycle owners. HTTP(S) extractor delegation avoids a permanently
stale host list while preserving rejection of search, file and executable input.

## Consequences

Authenticated Codex operations require tab-scoped CDP, host Node, local Python and
POSIX permissions. Missing capabilities and unusable cookies fail explicitly;
there is no silent switch to another browser or public mode. Partitioned cookies
remain unsupported because flattening their scope changes their isolation. Forced
termination may leave a protected task-owned temporary directory; recovery must
identify its stopped consumer before removing that exact directory. Browser login
does not prove yt-dlp access, platform support or media rights.

## Revisit

Revisit when Codex provides a first-party concealed cookie transfer, Windows gets
an equivalent tested temporary ACL contract, or supported media requires safely
preserving partitioned cookies. Extend the existing owners and retain explicit
source and cleanup guarantees.
