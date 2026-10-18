---
name: budgeting-account-sync
description: Use this skill whenever the user asks to sync Commonwealth Bank or CommBank with Actual Budget, sync again, import bank activity, balance accounts, or clear and lock transactions after reconciliation in Codex's built-in browser.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated built-in browser** — Open Actual Budget and Commonwealth NetBank and log in to both in Codex's built-in browser. The user restores expired logins before ledger changes.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Commonwealth to Actual syncing

Read [the shared logging contract](../budgeting-transactions/references/logging-contract.md)
and [transaction logging](../budgeting-transactions/SKILL.md) before changes. They
own browser/login prerequisites, metadata, categories and transfer handling.

## Compare fresh evidence

Resolve the accounts requested by the user. For “sync again”, reuse the established
scope only after verifying current identities; ask if no account scope can be
established. Match bank and Actual account identity, never balance or list order.
Both apps must already be logged in in the built-in browser.

Read current Actual totals, entries and last reconciliation, then capture bank
posted and available balances, pending activity and sufficient overlapping history
to resolve earlier pending entries. Timestamp observations in Brisbane time.
Create a private comparison containing account identity, amount, bank posted/value
dates, description/reference, bank status, matched Actual row and proposed action.

The approved default matches **available balance**, including visible pending
purchases. Verify how the bank explains the difference from posted balance;
unexplained restrictions are not transactions. A newer posted-only instruction
excludes pending holds from the cleared reconciliation target.

## Match before adding

| Evidence | Action |
| --- | --- |
| Identified transaction already present | Keep it; correct descriptive metadata only if needed. |
| Missing posted entry | Add once with verified sign/date, Notes and existing category. |
| Previously recorded pending purchase now settled | Update the same entry and settlement note; do not add a second expense. |
| New pending purchase included in available target | Add once with pending status and observation date in Notes. |
| Hold confirmed released without a remaining charge | Resolve the amount; a zero-value record with original amount/release context can preserve history. |
| Transfer on one or both sides | Inspect counterpart and link existing entries before creating anything. |
| Ambiguous equal amounts or disappearing pending row | Compare merchant, dates, reference and card suffix; resolve before locking. |

A missing pending row does not prove release: search settlement, replacement holds
and bank history. Preserve distinct purchases even if amount/merchant repeat.
New posted entries normally use posted dates with value dates in Notes. An existing
pending date can remain with an explanation or move to verified settlement date;
re-find the row after changing it.

## Enter or import

Use manual entry for a small incremental sync. For larger batches, export through
NetBank's visible CSV control, verify account/range and preserve the original
privately. Prepare only intended missing rows with source-to-entry mapping.
In Actual map Date and Amount (or debit/credit columns), descriptions to Notes,
and leave Payee unmapped. Verify day/month parsing, signs, delimiter and preview
count before importing. Correct a zero-row preview's mapping before retrying.

Check every resulting entry against the comparison; import merge heuristics are
insufficient for blank payees and repeated amounts. Disable **Reimport deleted
transactions** unless restoring those rows is intended. Inspect unexpected payees
or categories. See [Actual importing](https://actualbudget.org/docs/transactions/importing/).

## Clear, reconcile and lock

For available-balance syncing, verify the Actual ledger total equals the fresh
available target to the cent. For posted-only work, match verified posted entries
and reconcile their cleared total to the posted target; the ledger total can
include pending purchases. Resolve differences from evidence; never fabricate an
adjustment, income, opening balance or transfer. An existing Reconciliation
category is no exception.

Under the available-balance convention, clear all in-scope account transactions,
including documented pending purchases. This is the user's Actual bookkeeping
convention; it does not establish bank settlement. For posted-only work, keep
pending entries uncleared and compare the cleared total to posted balance instead.

1. Ensure bulk selection covers the intended account set, not a filtered subset.
2. Verify the cleared total equals the target. Under available-balance syncing,
   verify uncleared total is zero **and no uncleared entries remain**; cancelling
   debits and credits can sum to zero. Posted-only work can retain pending entries.
3. Open **Reconcile**, enter the target, confirm **All reconciled!**, then click
   **Lock transactions**. Verify locks and reconciliation date on the current ledger.
4. Repeat for every requested account, including those with no new activity;
   inspect affected transfer counterparts independently.
5. Perform the shared contract's Server Sync and reload checks. Recheck totals
   and locks after any correction. See [Actual reconciliation](https://actualbudget.org/docs/accounts/reconciliation/).

Report per-account bank target and target type, Actual/cleared balances, difference,
pending total, added/corrected entries, locks and server result. Keep private
comparison/evidence paths with the result. If blocked, finish independent verified
accounts and name the incomplete ones. On resume, read fresh bank and Actual state
and re-match saved work; never replay a previous add/import batch blindly.
