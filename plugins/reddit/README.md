# Reddit

AMSoft's Reddit plugin provides a bounded, read-only workflow for browsing Reddit through the
user's connected Chrome session.

It includes `reddit-browsing` for:

- opening a named Reddit URL, subreddit, post, or Reddit UI search;
- reading the rendered page through Chrome's CDP-backed browser controls;
- inspecting a small, explicit number of visible posts or comments; and
- returning evidence that separates what was visible from inference and unknowns.

## Runtime

The plugin requires the host `control-chrome` skill and a connected Chrome browser extension with
CDP-backed browser control. It does not bundle Chrome, a DevTools Protocol client, Playwright, a
Reddit API client, a Reddit scraper, a proxy, or a credential store.

## Safety boundaries

- The workflow is read-only. It does not vote, follow, join, subscribe, award, post, comment,
  message, moderate, change settings, or submit forms.
- It uses the existing Chrome session only as an authenticated browser surface. It never reads
  cookies, passwords, local storage, history, tokens, or unrelated tabs.
- It uses small explicit page and comment bounds. It does not infinite-scroll, crawl Reddit,
  export bulk datasets, or harvest usernames or personal data.
- Reddit scores, comment trees, availability, and UI behavior are time-sensitive. Reports include
  the observed scope and limitations rather than presenting a page sample as a complete census.

Start a new Codex session after installing or updating the plugin so the new skill is discoverable.
