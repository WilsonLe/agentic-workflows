# Browser-exported cookie authentication

Cookies are account credentials. Never paste or display them.

## Codex built-in browser (preferred when requested)

Use `auth_mode: codex_browser` for any supported site. This uses the current Codex
in-app browser session, not `--cookies-from-browser` or a Chrome/Firefox profile.
Requires a host with tab-scoped CDP, Node.js 18+, local Python, and a POSIX filesystem.
No native browser database or Keychain access is needed.

1. Prepare a normal version-1 request for `inspect`, `download` or `sync`, with
   `auth_mode: codex_browser` and URLs from exactly one HTTPS origin. Keep one
   bounded request per origin. `plan` works normally and never reads cookies.
2. Select/create the Codex built-in browser tab through the host's documented
   browser entry point and navigate to the requested URL. Read current browser
   documentation and `capabilities/tab/cdp` with `agent.documentation.get` in hosts
   that require it. Check `tab.capabilities.list()` for `cdp`. Complete any required
   sign-in using the host's concealed authentication or human handoff.
3. Import the bundled transport into the same `cua_repl` session. The `tab` below
   must be the existing, navigated Codex in-app tab. Use absolute local paths:

   ```javascript
   let cookieBridge = await import("file:///ABSOLUTE_PLUGIN_ROOT/scripts/codex_browser_cookies.mjs");
   let result = await cookieBridge.runWithCodexCookies({
     tab,
     requestPath: "/absolute/work/REQUEST.json",
     resultFile: "/absolute/work/RESULT.json",
     python: "python3"
   });
   nodeRepl.write(result);
   ```

   Set `python` or `ytDlp` to verified local executable paths only when necessary.
   The request's operation determines which fixed helper subcommand runs. Relative
   output roots resolve from the request file's directory; request/result paths must
   be absolute, so the browser runtime's working directory cannot redirect outputs.
4. The transport calls only `Network.getCookies` with the requested URLs. Cookie
   values stay inside the local process and pass to Python over stdin. The existing
   cookie helper validates scope and fields, rejects partitioned cookies rather
   than dropping their isolation, and writes a `0600` Netscape file inside a `0700`
   temporary directory. yt-dlp receives that file; cleanup runs after success,
   failure or its timeout. Browser sessions and stored exports remain intact.
5. Report only the sanitized helper result. Never call `Network.getAllCookies`,
   `Storage.getCookies`, return a raw CDP response, print child output, inspect
   native storage, or save the cookies in the request/result, logs or evidence.
   Missing capability, denied access, no usable cookies, partitioned cookies or
   unavailable local execution is a concrete authentication blocker. Stop that
   operation without silently choosing another browser or public mode.

Cookie-bearing temporary files are not crash-proof: forced process termination can
leave the task-owned `agentic-codex-cookies-*` directory. Remove only the identified
stale directory after confirming its consumer stopped. Normal cleanup preserves all
media and archives. YouTube session rotation or PO-token enforcement can still
prevent a download; a signed-in browser is not proof that yt-dlp authentication works.

## Legacy YouTube-only export

Follow [browser selection](browser-selection.md) for visible browser steps. In
For this legacy YouTube export, prefer the in-app browser only if it supports the private session and
reviewed concealed export required below. Otherwise use an explicitly authorized browser
with those capabilities and record the reason; do not extract cookies through
browser inspection tools as a substitute for this legacy workflow. The scoped Codex bridge above is a separate explicit mode.

1. Open exactly one private/incognito browser window and sign in to YouTube.
2. In that session, navigate to `https://www.youtube.com/robots.txt`.
3. Use a reviewed local browser export mechanism to export only `youtube.com` cookies in
   Mozilla/Netscape format.
4. Close the private/incognito session without reopening it.

Browser automation may guide visible steps but must not capture cookie values into chat,
screenshots, clipboard logs, model/tool output, or shell output.

## Install and lifecycle

Run by path from any working directory:

- `python3 <plugin-root>/scripts/youtube_cookie_store.py install /absolute/path/to/export.txt`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py status`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py verify EXACT_YOUTUBE_URL`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py rotate /absolute/path/to/new-export.txt --verify-url EXACT_YOUTUBE_URL`
- `python3 <plugin-root>/scripts/youtube_cookie_store.py revoke --confirm I_APPROVE_YOUTUBE_COOKIE_REVOKE`

The helper rejects symlinks, unsafe ownership/writability, malformed or oversized files,
non-YouTube domains, and expired-only input. It writes a protected copy to
`~/.config/agentic-workflows/youtube/cookies.txt`. On POSIX, the directory is `0700` and file is `0400`;
Windows uses an owner-restricted ACL.

Rotation restores the prior record if verification fails. The original browser export remains
sensitive; move it to Trash only after successful verification and explicit user approval.
Protected cookies are excluded from Git, plugin packages, evidence, and `.agenticx` transfer.

Cookie use may trigger rate limits or account restrictions. Use it only for account-gated content,
with bounded pacing. Expired/rotated cookies require another export.
