# Browser-exported cookie authentication

Cookies are account credentials. Never paste or display them.

## Export

1. Open exactly one private/incognito browser window and sign in to YouTube.
2. In that session, navigate to `https://www.youtube.com/robots.txt`.
3. Use a reviewed local browser export mechanism to export only `youtube.com` cookies in
   Mozilla/Netscape format.
4. Close the private/incognito session without reopening it.

Browser automation may guide visible steps but must not capture cookie values into chat,
screenshots, clipboard logs, model/tool output, or shell output.

## Install and lifecycle

From the plugin root:

- `python3 <plugin-root>/scripts/youtube_cookie_store.py install /absolute/path/to/export.txt`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py status`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py verify EXACT_YOUTUBE_URL`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py rotate /absolute/path/to/new-export.txt --verify-url EXACT_YOUTUBE_URL`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py revoke --confirm I_APPROVE_YOUTUBE_COOKIE_REVOKE`

The helper rejects symlinks, unsafe ownership/writability, malformed or oversized files,
non-YouTube domains, and expired-only input. It writes a protected copy to
`~/.config/amsoft/youtube/cookies.txt`. On POSIX, the directory is `0700` and file is `0400`;
Windows uses an owner-restricted ACL.

Rotation restores the prior record if verification fails. The original browser export remains
sensitive; move it to Trash only after successful verification and explicit user approval.
Protected cookies are excluded from Git, plugin packages, evidence, and `.amsoftx` transfer.

Cookie use may trigger rate limits or account restrictions. Use it only for account-gated content,
with bounded pacing. Expired/rotated cookies require another export.
