# Connect Vercel in Codex

1. Discover the Vercel plugin/connected app and its exposed tools in Codex. Read the
   schemas for identity, team and project inventory; do not assume a tool exists
   from its name or an earlier session.
2. If missing or disconnected, use Codex's supported plugin/app connection flow.
   Let the user complete private login, MFA, SSO or required consent. Do not create
   a local authentication store or request tokens in chat.
3. Verify the connected identity with the app's identity read. Resolve the intended
   team, project and environment using the request and repository evidence, then
   read them through this connection. Match stable IDs, not the first list result.
4. If team access needs consent, use the app's supported team-authorization flow
   within existing scope and re-read access afterward. A browser consent step
   completes connection setup; it does not authorize dashboard service operations.
5. Keep dependent work blocked on missing connection, permission or operation
   support. Report the specific recovery step. No CLI or dashboard fallback applies.

The connection is managed by Codex and is independent of the checkout. A new
worktree needs target verification through the app, without copying Vercel
credentials or logging in independently per directory.
