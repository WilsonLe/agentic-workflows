# Reddit browsing onboarding

Use a read-only readiness pass before opening Reddit. Do not navigate merely to prove that the
plugin is installed.

## Confirm the request

Record:

- the exact Reddit URL, subreddit, or topic supplied by the user;
- the requested task: page reading, subreddit sample, Reddit UI search, post reading, or selected
  visible comments;
- the maximum number of pages, posts, and comments to inspect;
- the sort, time range, language, and location assumptions if they affect the request; and
- the desired output and whether links or a reusable evidence note are needed.

If a limit is missing, choose a small bounded default and state it before browsing. If a broad goal
would materially change the sample, ask for a narrower target instead of guessing.

## Check the browser surface

The host `control-chrome` skill is a required runtime dependency. Confirm that:

- Chrome is the explicitly selected browser family;
- the supported browser extension/CDP connection is available;
- the browser documentation has been read for this connection; and
- the chosen tab is a current Reddit tab or a new tab created through the documented browser API;
- any new tab is marked task-owned immediately and a documented close path is ready for completion
  and early-exit cleanup.

Do not inspect or report cookie values, browser profile paths, history, storage, passwords, or
tokens. A signed-in Chrome session may provide access to a page, but it never authorizes extracting
the session itself.

## Return readiness

Report one of:

- **Ready:** Chrome/CDP is connected and the exact read scope is bounded;
- **Needs input:** URL/topic, sample size, time window, or output format is missing;
- **Needs sign-in:** Reddit requires the user to sign in in the same Chrome session;
- **Needs configuration:** the supported Chrome extension/CDP connection is not ready; or
- **Blocked:** Reddit presents a rate limit, CAPTCHA, unavailable page, or other boundary that the
  workflow must not bypass.

Give the next safe action and keep account details, private text, and authentication material out of
the report.

When the operation ends, close task-owned tabs even if Reddit is blocked or the operation fails. Do
not close pre-existing user tabs or the browser; report `tab_cleanup_failed` if the supported close
operation does not succeed.
