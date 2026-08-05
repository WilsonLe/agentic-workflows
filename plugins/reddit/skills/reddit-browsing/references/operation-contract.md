# Reddit operation contract

This contract keeps a Chrome/CDP Reddit read small, visible, and reversible.

## Inputs

The operator supplies:

- one exact Reddit URL, one subreddit name, or one topic for Reddit's own visible search;
- an operation of `page`, `subreddit`, `search`, `post`, or `comments`;
- an explicit or agreed item bound;
- optional sort and time-window filters; and
- a requested output shape.

Do not accept raw JavaScript, raw CDP commands, arbitrary URLs, proxy settings, browser profile
paths, cookie paths, headers, API keys, or extraction scripts as operation inputs.

## Allowed read operations

| Operation | Allowed evidence | Default bound |
| --- | --- | --- |
| `page` | One named Reddit page and its visible title/metadata | 1 page |
| `subreddit` | Visible post cards from one named subreddit listing | 10 posts |
| `search` | Visible Reddit UI search results for one topic | 10 results |
| `post` | One post's visible title, body, metadata, and permalink | 1 post |
| `comments` | Selected visible comments on one post | 10 comments |

The bound is a ceiling, not a target. Stop early when the requested question is answered or the
page becomes unavailable. A new subreddit, query, outbound site, or post is a new scope decision.

## Tab ownership and cleanup

Record the tab set before navigation. Prefer an existing in-scope Reddit tab. If the documented
browser API creates a tab, mark it task-owned immediately and retain its binding. Close every
task-owned tab through the documented tab-close method after the final read and on every early exit,
including login, gate, error, cancellation, or reporting failure. Do not close pre-existing user tabs,
unrelated tabs, or the browser. A task-owned tab may remain open only when the user explicitly asks
for it. Report `tab_cleanup_failed` when cleanup cannot be completed.

## Execution rules

1. Select Chrome through the host browser skill and use the documented CDP-backed browser client.
2. Establish tab ownership before navigating and mark any newly created tab as task-owned.
3. Navigate only to the exact in-scope Reddit page or use the visible Reddit search control.
4. Re-read the rendered page after navigation, sort changes, expansions, and pagination.
5. Record the visible page URL and capture time before summarizing. Use stable observed permalinks
   rather than guessed element identifiers.
6. Keep all actions read-only. If an action could submit, vote, join, follow, award, message, or
   change account state, do not perform it.
7. Stop on login, CAPTCHA, rate limit, safety gate, unavailable content, or unexpected navigation;
   then run the tab cleanup path before reporting the state.

## Failure states

Use one of these states in the report:

- `chrome_unavailable`: the supported Chrome/CDP browser surface could not be selected;
- `reddit_sign_in_required`: the user must sign in in the same Chrome session;
- `reddit_rate_limited`: Reddit asks for a pause or limits the current page;
- `reddit_gate`: CAPTCHA, age/content warning, consent, or another visible gate needs the user's
  direct handling;
- `reddit_unavailable`: the requested page or content is removed, private, or unavailable; or
- `tab_cleanup_failed`: a task-created tab could not be closed through the supported browser API;
- `scope_complete`: the requested bounded read finished.

Never convert a failure state into an empty result or retry it with another transport.
