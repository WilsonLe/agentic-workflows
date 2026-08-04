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

## Execution rules

1. Select Chrome through the host browser skill and use the documented CDP-backed browser client.
2. Navigate only to the exact in-scope Reddit page or use the visible Reddit search control.
3. Re-read the rendered page after navigation, sort changes, expansions, and pagination.
4. Record the visible page URL and capture time before summarizing. Use stable observed permalinks
   rather than guessed element identifiers.
5. Keep all actions read-only. If an action could submit, vote, join, follow, award, message, or
   change account state, do not perform it.
6. Stop on login, CAPTCHA, rate limit, safety gate, unavailable content, or unexpected navigation.

## Failure states

Use one of these states in the report:

- `chrome_unavailable`: the supported Chrome/CDP browser surface could not be selected;
- `reddit_sign_in_required`: the user must sign in in the same Chrome session;
- `reddit_rate_limited`: Reddit asks for a pause or limits the current page;
- `reddit_gate`: CAPTCHA, age/content warning, consent, or another visible gate needs the user's
  direct handling;
- `reddit_unavailable`: the requested page or content is removed, private, or unavailable; or
- `scope_complete`: the requested bounded read finished.

Never convert a failure state into an empty result or retry it with another transport.
