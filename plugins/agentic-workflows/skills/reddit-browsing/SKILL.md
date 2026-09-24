---
name: reddit-browsing
description: Browse Reddit pages, subreddits, posts, and a bounded number of visible comments through the user's connected Chrome session using the host's CDP-backed browser controls.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Connected Chrome browser** — Connect Chrome through the host browser controls and sign in only when required.

<!-- catalog-prerequisites:end -->

# Reddit Browsing

Use this skill for a bounded, read-only Reddit task that must happen in Chrome. It is a browser
workflow, not a Reddit API client or a scraper. The browser's DevTools Protocol (CDP) connection
is only the transport; the evidence must come from the rendered Reddit page visible in the selected
Chrome session.

Before first use, read [onboarding.md](references/onboarding.md) and
[operation-contract.md](references/operation-contract.md). Read
[evidence-and-reporting.md](references/evidence-and-reporting.md) whenever the user wants a
research summary, comparison, or reusable evidence.

## Select Chrome and connect

1. Use the host `control-chrome` skill before any browser action. The user requested Chrome, so
   select the Chrome family explicitly; do not substitute the in-app browser, web search, direct
   HTTP, Reddit's API, or a standalone Playwright process.
2. Follow `control-chrome`'s setup contract exactly: reuse an existing browser binding when one is
   available, initialize the browser client once, and read the selected browser's complete
   documentation before obtaining or operating a tab.
3. Use only the documented browser-client tab methods and rendered-page inspection/actions. The
   client is CDP-backed, but do not attach to an arbitrary debugging port, open a raw CDP socket,
   send undocumented protocol commands, execute page-context `fetch`/XHR to Reddit endpoints, or
   read network headers, cookies, storage, passwords, or tokens.
4. If Chrome or its browser extension/CDP connection is unavailable, report that prerequisite and
   stop. Direct the user to connect Chrome through the supported browser setup; do not silently
   fall back to another browser or a server-side Reddit client.
5. If Reddit asks the user to sign in, stop at the login boundary. Ask the user to sign in in the
   same Chrome session and tell you when it is ready. Never ask for a password, OTP, recovery code,
   cookie, token, or copied page secret.

## Track and close task-created tabs

- Prefer an existing in-scope Reddit tab. Before creating a tab, establish the current tab set using
  the documented browser API without inspecting unrelated tab content.
- Mark every tab created for this task as task-owned immediately and retain its binding for cleanup.
- Close every task-owned tab with the documented browser tab-close method after the final observation,
  and also on login, content blockers, errors, cancellation, or other early exits. Use a
  `try`/`finally`-equivalent cleanup path so cleanup is attempted even when reporting fails.
- Never close a pre-existing user tab, an unrelated tab, or the browser itself. Keep a task-created
  tab open only when the user explicitly asks for it.
- If a task-owned tab cannot be closed, report `tab_cleanup_failed` and do not describe the task as
  cleanly completed until the user knows which cleanup remains.

## Establish the exact read scope

Before navigating, restate the smallest useful scope:

- exact Reddit URL, named subreddit, or user-supplied topic/search query;
- whether the target is a subreddit listing, Reddit search results, one post, or a comment thread;
- maximum pages or posts to inspect; use a small default such as 10 posts or 10 visible comments;
- sort/filter and time window, if the user specified them; and
- the requested output: a short summary, comparison, quote-free notes, links, or a research packet.

If the user gives only a broad goal such as “find what Reddit thinks,” ask for a subreddit/topic,
time window, and sample size before browsing. Do not turn a broad goal into an unbounded crawl.

## Navigate and inspect

1. Start at the named Reddit page or use Reddit's own visible search UI. Keep navigation within
   `https://www.reddit.com/` unless the user explicitly supplies another Reddit-owned URL. Treat
   outbound links as separate destinations that require a new scope decision.
2. After every navigation or filter change, wait for the rendered page to settle and re-check the
   visible title, canonical URL, subreddit, sort/filter, and result count or page state. If Reddit
   shows a login wall, consent prompt, rate limit, safety warning, or unavailable page, record that
   state and stop or ask what to do.
3. Discover controls semantically from visible labels, landmarks, accessible names, and observed
   stable Reddit permalinks. Do not depend on generated CSS class names, React internals, hidden
   JSON, or a guessed DOM shape. Do not click a control merely because it looks like a vote,
   subscribe, join, award, share, post, or message action.
4. Read only the requested visible content. For a listing, inspect at most the agreed number of
   post cards. For a post, inspect its title, body, visible metadata, and at most the agreed number
   of top-level or visibly loaded comments. Do not repeatedly expand nested replies to exhaust a
   tree.
5. Preserve exact links observed in the page when useful. Paraphrase by default; quote only a
   short user-requested excerpt and keep public usernames, flair, timestamps, and scores to the
   minimum needed for the task.
6. If the page uses infinite scroll, treat the current rendered batch as one page. Do not scroll
   until the bound is reached, and never use a loop that continues until no more content appears.

## Privacy and platform boundaries

- Never inspect Chrome history, cookies, passwords, local storage, session storage, cache, browser
  profiles, extensions, or unrelated tabs.
- Never copy authentication material, authorization headers, CSRF values, hidden state, Reddit
  JSON blobs, or private messages into notes or chat.
- Minimize public personal data. Omit usernames unless attribution is necessary; redact email
  addresses, phone numbers, addresses, direct-message content, and other sensitive details if they
  appear in visible text. Do not build a person or lead database from Reddit.
- Do not bypass a login, age gate, content warning, rate limit, CAPTCHA, robots restriction, or
  Reddit UI control. Do not use alternate hosts, proxies, stealth settings, fingerprint changes,
  or API keys to evade a boundary.
- Do not perform any write or engagement action: voting, following, joining, subscribing,
  awarding, saving, posting, commenting, editing, messaging, reporting, moderating, or changing
  account/settings state is outside this skill.
- Stop if the requested task becomes bulk extraction, continuous monitoring, automated account
  activity, or collection of sensitive or identifying information. Explain the smallest safe
  read-only alternative.

## Report what was actually observed

Return a compact report with:

- **Scope:** exact URL/subreddit/query, sort/time filters, page or item bound, and capture time;
- **Observed:** only text, metadata, links, counts, and states visible in Chrome;
- **Synthesis:** clearly labelled patterns or comparisons derived from those observations;
- **Unknowns:** unloaded replies, hidden/removed content, personalization, login-gated content,
  changing scores, rate limits, and any requested fields not visible;
- **Source links:** Reddit permalinks observed in the page; and
- **Boundary:** confirmation that the operation was read-only, used the connected Chrome session,
  and closed all task-created tabs (or reported `tab_cleanup_failed`).

Do not call a sample representative of all Reddit users, a subreddit consensus, or current global
sentiment. Scores and comment order are mutable, Reddit can personalize results, and a visible page
does not prove that omitted or removed content does not exist.

## Completion

The task is complete when the bounded pages have been read or a clear browser/content blocker has
been reported, the final report distinguishes observation from inference, no external Reddit state
changed, and all task-created tabs have been closed or an explicit `tab_cleanup_failed` limitation
has been reported. A browser connection, a loaded page, or a copied URL alone is not evidence that
the requested content was successfully inspected.
