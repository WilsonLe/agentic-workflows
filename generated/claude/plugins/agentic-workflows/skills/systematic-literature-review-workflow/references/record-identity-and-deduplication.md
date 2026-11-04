# Record identity and deduplication

Keep three levels distinct:

- a source record is one database/export occurrence;
- a report is one document or dissemination object;
- a study is the underlying investigation represented by one or more reports.

Assign stable IDs independent of mutable filenames. Link corrections, errata, protocols, abstracts,
secondary analyses, companion reports, retractions, and withdrawals without erasing history.

Cluster exact DOI, PMID, trial-registration, or other normalized identifiers first. Conservative
title/author/year similarity produces review candidates only. A human records every merge,
non-merge, split, or unmerge decision, rationale, aliases, actor, timestamp, and prior/new links.
Never delete raw records or silently discard a fuzzy match. Multiple reports of one study remain
linked and may each contribute distinct data.

Flow counts come from current ledger states and reconcile source records, deduplicated reports,
reports sought/retrieved/assessed, included reports, and included studies.
