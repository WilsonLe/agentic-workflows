# Task continuity for every workflow

Use a short working contract for the user's actual outcome. Retain named artifacts, explicit
exclusions, issue/PR/review/deployment expectations, source of truth, and the evidence that would
prove completion. Carry the contract across turns and task resumption. A newer explicit correction
updates only the affected item; do not ask again for a decision or authorization already supplied
for the same scope. Check current external state before acting or reporting because saved notes
and previous observations can drift.

When a requested source is authenticated, inspect the named channel early. If one route fails,
classify the failure and check an already-authorized equivalent route to the same source before
declaring the artifact impossible. Do not bypass access controls or treat an error/redirect page as
the source. Keep a secret-free progress list for multi-provider tasks: target, action, observed
state, saved setting, live readback, end-to-end flow result, and next unverified step. A saved
setting alone does not prove the requested flow.
Before asking about provider setup, group independent nonsecret choices into one concise
question. Reuse an answer or exact approval already supplied for the same operation;
ask separately only for dependent consent, private entry, or a materially changed scope.
Continue independent authorized work while waiting and resume at the first unverified step.

Before finishing, inspect the actual requested artifact or target environment. For a source copy,
compare the local result with the source's required pages or sections. For hosted work, distinguish
local, Preview, staging, and production evidence. If a required item remains unverified, report
that precise state and continue independent authorized work.

For repository delivery, use the Standard Development Workflow's
[record and planning guide](../../standard-development-workflow/references/efficient-delivery-and-external-work.md)
for a structured contract, measured verification, and resumable external ledger. Its helper is
optional for lighter non-code tasks.
For tracked implementation changes in a Git worktree, finish with a live PR whose head matches
the reviewed candidate. Read back its base, state, checks, and review status before the final
response, then link it. Reuse a matching existing PR. An unchanged or read-only checkout does
not need an empty PR; an unavailable remote or missing permission is an incomplete blocker.
