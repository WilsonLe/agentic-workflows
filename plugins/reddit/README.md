# Reddit

Agentic Workflows Reddit plugin provides a bounded, read-only workflow for browsing Reddit through the
Codex in-app browser by default, or another explicitly selected or required supported browser.

It includes `reddit-browsing` for:

- opening a named Reddit URL, subreddit, post, or Reddit UI search;
- reading the rendered page through supported host browser controls;
- inspecting a small, explicit number of visible posts or comments; and
- returning evidence that separates what was visible from inference and unknowns.

## Runtime

The plugin requires supported host browser controls and prefers the Codex in-app browser.
An explicit browser choice takes precedence; a capability limitation can justify an authorized
equivalent browser. See [browser selection](skills/reddit-browsing/references/browser-selection.md).
It does not bundle a browser, a DevTools Protocol client, Playwright, a
Reddit API client, a Reddit scraper, a proxy, or a credential store.

## Safety boundaries

- The workflow is read-only. It does not vote, follow, join, subscribe, award, post, comment,
  message, moderate, change settings, or submit forms.
- It uses the selected browser session only as an authenticated browser surface. It never reads
  cookies, passwords, local storage, history, tokens, or unrelated tabs.
- It uses small explicit page and comment bounds. It does not infinite-scroll, crawl Reddit,
  export bulk datasets, or harvest usernames or personal data.
- Reddit scores, comment trees, availability, and UI behavior are time-sensitive. Reports include
  the observed scope and limitations rather than presenting a page sample as a complete census.

Start a new Codex session after installing or updating the plugin so the new skill is discoverable.
