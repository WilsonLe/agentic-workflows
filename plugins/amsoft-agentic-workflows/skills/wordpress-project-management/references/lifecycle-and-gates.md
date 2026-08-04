# WordPress lifecycle and gates

Keep lifecycle states independent. A plan, repository change, site change, release, publication,
and provider data collection are different claims.

## Standard sequence

`discover -> classify -> plan/spec -> approve -> isolate/rehearse -> snapshot/drift-check ->
change -> read-back -> surface verification -> release handoff`

For every task, report these dimensions separately:

| Dimension | Example states | What it proves |
| --- | --- | --- |
| Plan/spec | planned, approved, reapproval-required | Intended scope and authority only |
| Source/PR | changed, checks-passing, draft-PR, merged | Repository state only |
| Local/staging | rehearsed, applied, verified, blocked | That environment only |
| Production | approved, applied, verified, rolled-back | Production target only |
| Publication | draft, private, noindex, published | WordPress access/indexing state |
| Provider data | configured, consent-enabled, collecting, recorded | External analytics/audit/email state |

Never infer a later state from an earlier one. Merged is not deployed, deployed is not published,
and a published page is not proof of analytics collection.

## Authority gates

- **Plan gate:** user-approved issue/plan; no site mutation.
- **Content gate:** approved source facts, managed-field diff, current remote lock, and publication
  status.
- **Runtime gate:** exact environment fingerprint, discovered adapter, backup/rollback, and narrow
  command.
- **Browser gate:** exact origin/account/status, viewport and interaction matrix, and required
  console/network evidence.
- **Production gate:** explicit production authorization, current target proof, backup, rollback,
  and release window where applicable.
- **Provider gate:** explicit data-flow/consent authorization and provider-specific evidence.

An unresolved prerequisite is `blocked`, not an invitation to use a weaker substitute.

## Scope expansion

Stop and update the issue/plan before proceeding if implementation reveals a new runtime, public
interface, persistence model, migration, credential, external mutation, broad site-wide change,
or a weaker verification channel than approved. Keep separable cleanup or generalization as a
follow-up issue.
