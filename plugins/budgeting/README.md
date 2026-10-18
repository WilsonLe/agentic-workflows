# Budgeting

Commonwealth Bank → Actual Budget syncing and transaction logging through Codex's
built-in browser. Both apps must be open and logged in before ledger operations.
The user completes expired logins in that browser.

- [Account sync](skills/budgeting-account-sync/SKILL.md): compare current activity,
  prevent duplicates, resolve pending purchases, reconcile available balances,
  clear and lock, and verify Server Sync and persistence.
- [Transactions](skills/budgeting-transactions/SKILL.md): blank ordinary payees,
  descriptive Notes, existing categories, linked transfers, cash, refunds and
  income/reimbursement splits. Its [logging contract](skills/budgeting-transactions/references/logging-contract.md)
  owns the approved workflow preferences; newer user instructions take precedence.

This is a canonical source component bundled into the single `agentic-workflows`
marketplace plugin. The skills are Codex-only because they require its built-in
browser. Update the bundle and start a fresh session to discover them. This package
contains instructions, not a bank connector, credential store or scheduled sync.
It never initiates bank payments. Account mappings and financial evidence remain
private in the user's task workspace.

[Walkthrough scenarios](validation.md) describe instruction-level acceptance;
package checks do not demonstrate live bank operations or future agent behavior.
