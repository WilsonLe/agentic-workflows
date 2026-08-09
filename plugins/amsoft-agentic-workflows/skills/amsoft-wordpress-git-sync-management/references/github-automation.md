# Reviewed GitHub automation

The runtime queues eligible public managed-object saves. Autosaves, revisions,
private/restricted content, and bot applies are excluded. A repository workflow
consumes a bounded event, runs fresh inventory/pull/diff, and creates or updates
a bot branch and pull request after debounce. It never commits to a protected
branch.

An approved Git merge triggers a new remote read, validation, plan, CAS apply,
canonical readback, and status report. The merge does not reuse a PR-time lock.
Staging and production use environment protection and separate approval.

Every event carries a correlation ID, site/environment/object concurrency key,
actor reference, and idempotency identity. Per-site/environment concurrency,
loop suppression, cancellation, duplicate/out-of-order delivery handling,
dead-letter state, and reconciliation keep partial failure truthful.

Workflow permissions default to `contents: read`. Bot branch/PR creation uses
the narrow additional permissions in its reviewed job. WordPress credentials
are environment-scoped secret references and never appear in workflow input,
commands, output, artifacts, or pull-request content.

The shipped workflow is an integration template, not an autonomous writer. A
repository must provide reviewed executable adapters at
`.wordpress-sync/pull-and-open-pr` and
`.wordpress-sync/fresh-read-plan-apply`. The template passes the validated
project and event paths to both; the apply adapter also receives `plan` or
`apply`. It derives the protected GitHub environment from the validated event,
rejects escaping/symlinked paths, and fails if either adapter is absent.
