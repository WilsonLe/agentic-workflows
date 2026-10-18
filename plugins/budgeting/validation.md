# Budgeting instruction walkthroughs

All examples are synthetic. Trace each request through the linked skill and its
shared logging contract. These are authoring acceptance scenarios, not evidence
that an agent operated a real bank or that the plugin is installed.

| Request or condition | Reachable behavior and observable finish |
| --- | --- |
| “Sync again”; both apps authenticated | Account sync resolves established scope, reads overlapping history, builds comparison, applies missing/corrected entries, reconciles each account, verifies Server Sync and reload. |
| One app has expired login | Shared contract pauses dependent mutations; user signs in in the built-in browser; resume reads fresh data before changing anything. |
| Identical sync repeated | Existing identified rows are kept; no duplicate entries or transfer pairs are added. |
| Pending purchase settles for a changed amount | Match original entry using source details; update it and settlement Notes, then recompute target and reconcile. |
| Pending row disappears | Look for settlement/replacement before release; uncertainty blocks that account's locking. |
| Hold confirmed released | Resolve original hold amount; optional zero record retains original amount and release evidence in Notes. |
| Same merchant/amount occurs twice | Use dates/reference/card suffix; retain two supported purchases instead of merging by amount. |
| Transfer already imported on both sides | Transaction skill uses Make transfer on matching opposite entries; verifies both account deltas and individual status. |
| Employer receipt includes reimbursement | Verify component amount; split into existing reimbursement and Income categories, keeping the parent sum unchanged. |
| Cash payment covers several weeks | Use actual payment date and coverage Notes; separate confirmed payments use their own actual dates. |
| Rule unexpectedly populates Payee | Correct affected entry to blank ordinary payee; report the cause without creating rules or doing unrelated bulk cleanup. |
| Bank available differs for unexplained reasons | Investigate source evidence; no plug entry, no lock/completion claim for that account. |
| Uncleared debit and credit cancel | Zero uncleared total alone fails; inspect for remaining uncleared entries before available-balance completion. |
| New instruction requests posted-only | Pending entries stay uncleared; cleared total reconciles to posted target and report identifies that target type. |
| Network fails after a saved import | Preserve saved-work checkpoint; report server completion unverified; reload/re-match before resuming, never replay blindly. |
| Historical payee cleanup requested | Backup first, preserve ordinary payee text in existing Notes before removal; retain transfer linkage and verify unchanged balances. |

Verify catalog inclusion and bundle mirrors with the existing package tests and
generator; verify every local reference with the package validator. A future live
acceptance run requires a separately requested operation and authenticated apps.
