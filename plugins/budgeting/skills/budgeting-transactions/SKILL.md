---
name: budgeting-transactions
description: Use this skill whenever the user asks to log, correct, categorize, split or refund an Actual Budget transaction, record cash spending or a transfer, or separate income from reimbursement using descriptive notes and existing categories.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Authenticated built-in browser** — Open Actual Budget and Commonwealth NetBank and log in to both in Codex's built-in browser. The user restores expired logins before ledger changes.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Actual transaction logging

Read [the shared logging contract](references/logging-contract.md) first. It owns
both-app built-in-browser login, blank ordinary payees, descriptive Notes,
existing categories, user-specific treatments, privacy and scope. For a bank sync,
use [account syncing](../budgeting-account-sync/SKILL.md) as the reconciliation owner.

## Record or correct

1. Resolve the requested account and source facts: payment date, signed amount,
   direction, purpose and evidence. Search the current ledger before adding;
   compare dates, merchant, references and any earlier pending entry.
2. Enter expenses as payments and receipts/refunds as deposits. In private working
   comparisons use signed cents, negative for expenses and positive for deposits.
   Currency conversions require source evidence.
3. Apply the logging contract's Notes and category treatment; leave the ordinary
   Payee blank. If an import or existing rule fills it unexpectedly, correct the
   affected entry and report the cause; do not create a replacement rule.
4. For a split, verify each component and its category, then confirm the children
   sum exactly to the unchanged parent amount. An unknown reimbursement amount
   requires clarification before splitting.
5. Read back the saved entry and balance delta. Remove unused unsaved drafts.
   Apply the contract's persistence and Server Sync checks before completion.

## Cash and payment dates

Record cash spending in the existing Cash account on its actual payment date.
Distinguish when money was paid from the period it covers. For multiple payments,
use the user-confirmed individual dates; a payment covering several weeks can
retain one payment with its coverage in Notes. Do not spread an advance payment
across assumed dates or create future payments because rent is weekly. Ask when
the user's statement does not establish which payments actually happened.

## Transfers and corrections

Search both account ledgers first. Use Actual's special Transfer To/From payee to
record an existing movement; it creates the counterpart automatically. If two
independent matching entries already exist, use **Make transfer** rather than
adding another pair. Verify both deltas, including an out-of-scope counterpart;
that check does not independently reconcile its bank account.

Transfer amounts and Notes propagate; cleared/reconciled flags are per account.
Inspect **Sync both transfer dates** before date edits. On-budget transfers use
Actual's transfer treatment; select an existing category on the budget side when
crossing an on/off-budget boundary. See [Actual transfers](https://actualbudget.org/docs/transactions/transfers/).

A requested locked-entry correction can use the app's confirmation in scope;
recheck affected balances afterwards. Do not bulk unlock history for a small edit.
Before deleting/merging duplicates, establish the authoritative record and recovery;
deleting a transfer affects both sides. See [Actual reconciliation](https://actualbudget.org/docs/accounts/reconciliation/).
