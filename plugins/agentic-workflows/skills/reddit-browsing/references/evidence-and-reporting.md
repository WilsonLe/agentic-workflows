# Evidence and reporting

Reddit is a mutable, personalized, user-generated surface. A browser observation is useful for the
specific page and moment observed, but it is not a complete dataset or a population estimate.

## Evidence record

For each page or item retained, record only the minimum needed:

```text
captured_at: <local time with timezone>
url: <observed Reddit permalink>
channel: <actual browser and host controls; include any fallback reason>
surface: page | subreddit | search | post | comments
sort_or_filter: <visible setting or unknown>
bound: <requested maximum>
observed_items: <number actually read>
observations:
  - <short paraphrase or necessary short quote>
  - <visible metadata that changes interpretation>
limitations:
  - <unloaded, removed, login-gated, personalized, or changing state>
```

Do not include cookie values, tokens, hidden JSON, authorization headers, private messages, or a
bulk list of usernames. Hashing or redacting a secret does not make it appropriate to collect.

## Synthesis rules

- Separate **observed** page facts from **calculated** counts and **inferred** patterns.
- Report the denominator: pages, posts, comments, sort order, time window, and bound.
- Use “in this sample” for patterns; do not claim subreddit-wide consensus or general sentiment.
- Preserve disagreement, removed/deleted items, duplicate posts, and unknowns when they affect the
  answer.
- Treat displayed score, rank, award, comment count, author, flair, and timestamps as visible
  point-in-time metadata, not permanent facts.
- Prefer permalinks and capture times over copied prose. Quote only when necessary and keep quotes
  short.

## Example final shape

```text
Scope: r/example, Top / Past week, first 10 visible posts, captured <time>.

Observed:
- ...

In this sample:
- ...

Unknown or limited:
- ...

Sources:
- <observed Reddit permalink>

Boundary: read-only observation through <actual browser/channel>; no Reddit account or page state was changed; all
task-created tabs were closed, or `tab_cleanup_failed` was reported.
```
