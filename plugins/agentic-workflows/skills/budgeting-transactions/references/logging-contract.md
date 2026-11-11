# Budgeting logging contract

Read this contract before either budgeting skill operates. These are the user's
approved workflow defaults; newer task instructions take precedence. They are
not general accounting advice or permission to change unrelated history.

## Browser, scope and authority

Actual Budget and Commonwealth NetBank must both be open and logged in within
Codex's built-in browser before ledger work begins. Resolve the user's Actual
budget and the relevant bank accounts from the current authenticated pages;
never hardcode account numbers, private hosting URLs or historical balances.
If either login expires, pause dependent mutations and ask the user to sign in
in that browser. Continue independent read-only preparation where useful.

Use the supported host browser controls and read their documentation before
operating tabs. Reuse relevant existing tabs. Inspect and act on rendered pages;
refresh UI state after navigation, filtering, edits or modal changes. Do not use
browser storage, cookies, credentials, private app internals, raw database edits,
undocumented endpoints or direct requests to substitute for this workflow.
Never ask for passwords or one-time codes; the user completes authentication.

A request to sync or log transactions authorizes the necessary Actual ledger
steps, not bank payments, money movement, recurring jobs or unrelated cleanup.
An Actual transfer records an existing bank movement. Do not create rules or
schedules unless newly requested. Budget allocations do not record payments.

Keep bank exports, comparisons, recovery backups and screenshots private and
outside Git/published artifacts. Use AUD and Australia/Brisbane dates unless the
current task says otherwise. Before broad historical edits or destructive cleanup,
export a recovery backup; routine sync does not authorize bulk payee/rule deletion.

## Notes, payees and categories

- Leave ordinary Payee fields blank; do not create or reuse merchant payees.
  Preserve Actual's special Transfer To/From payees for account linkage.
- Put merchant, employer, recipient and useful bank descriptions in descriptive
  Notes. Preserve existing notes and former payee information on corrected entries.
  If historical payee migration is explicitly requested, copy information into
  Notes before removing ordinary payees; preserve transfer linkage and balances.
- Include payment purpose, references, value/posted dates when provided, pending
  or settled status, and relevant coverage periods. Keep card details to a suffix
  only when useful for matching. Do not overwrite useful original context.
- Use existing categories supported by current options, source evidence and
  comparable prior entries. Do not infer purpose from the amount alone or create
  a category to make an uncertain entry fit. Ask about material ambiguity.
- Approved category treatments: OpenAI spending goes to existing Business;
  personal subscriptions go to Subscriptions; petrol/gas goes to Car. Verify the
  corresponding category exists; ask if the current budget lacks it.
- For a payment containing earnings and a verified OpenAI reimbursement, split the
  received payment: reimbursement to the existing reimbursement category, remainder
  to existing Income. Verify the reimbursement amount; do not infer that an entire
  employer payment is income or that an expected reimbursement has arrived.
- Ordinary purchase refunds use the original expense category where appropriate,
  with the original purchase identified in Notes.

## Verification and reporting

Read back saved date, amount, direction, blank ordinary payee or transfer linkage,
category and Notes. Splits must total the original payment exactly. Check each
affected account delta. A saved preview or a lock icon alone does not prove the
result. Reconcile again after a balance-changing correction to a locked entry.

After writes, inspect Server Sync for outstanding operations/errors and verify
persistence after reload. **Server online** proves connectivity only. Report saved
changes, verified results and any unresolved account/login/sync problem separately.
A failed sync leaves completion unverified; preserve the saved-work checkpoint.
