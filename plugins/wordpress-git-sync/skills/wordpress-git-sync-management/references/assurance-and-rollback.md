# Assurance and rollback

Required evidence progresses from schemas and fake transport to PHP runtime
tests, disposable WordPress, one-object staging canary, and separately approved
production. Local/CI success proves the package candidate only.

Exercise clean round trips, stale hashes, identity collision, unowned fields,
unknown blocks, theme/version mismatch, missing dependencies, private content,
oversized media, MIME/rights failure, duplicate/out-of-order events, runner or
network loss, interrupted apply, failed editor/rendered verification, code and
content rollback divergence, restore, resume, and de-enrolment.

Audit events record correlation/idempotency identities, actor reference,
project/site/environment/object, pre/post hashes and revisions, result,
duration, and redacted error class. Never record credentials or payload bodies.

Rollback units remain separate: content object/revision, Site Editor entity,
media mapping, code artifact/release, plugin/runtime version, and database/file
snapshot. Stop mutations, preserve first evidence, re-read target, classify the
failed layer, obtain the applicable rollback approval, recover the narrowest
unit, and verify every affected surface.
