# Workflow-record archetype examples

These examples show applicability decisions, not commands to copy. Repository evidence supplies
every real command, path, service, account, and verification channel.

| Archetype | Capability profile | Task-run decisions | Final evidence |
| --- | --- | --- | --- |
| Small library | Static, unit, package metadata; no services, browser, reusable artifact, or staging | One focused-to-complete validation ladder; sandbox, operation, resource budget, and artifact sections not applicable | Committed source plus complete static/unit results |
| CLI/package | Static, unit, build/package commands and supported platforms | Immutable artifact bound to source, lockfile/build-input digest, command, platform, and package digest | Source, package digest, complete tests, and CLI behavior claims |
| Stateful service | Migrations, database, queues, integration commands, readiness, ports, and cleanup ownership | Separate suite-owned mutable state; resource/capacity preflight; failure clean-state comparison | Source, migrations, integration results, state identities, limitations |
| Browser application | Build/runtime commands, browser channels, responsive and accessibility boundaries | Browser suite isolated from integration state; requested channel preflight; interaction and visual claims kept distinct | Source/artifact identity plus inspectable responsive, interaction, console, and accessibility evidence |
| Authenticated staged service | Local and staging commands, provider/account boundary, external approvals, deployment identity, rollback | Local completion precedes separately approved staging; local evidence cannot satisfy deployed claims; long deployment/check operations checkpointed | Squash-merged source, immutable deployed artifact, authenticated staging channel, logs/health, and rollback readiness |

## Required negative scenarios

- a changed instruction, manifest, lockfile, CI file, runtime definition, or deployment runbook
  invalidates only affected profile sections;
- a blocking unknown cannot become implementation-ready;
- an unapproved material expansion stops work;
- insufficient capacity does not authorize shared-cache reclamation;
- a failed prerequisite prevents an expensive dependent validation;
- product, harness, fixture, environment, platform, external, expected, nondeterministic, and
  unknown failures retain distinct remedies;
- shared mutable suite state without safety evidence is rejected;
- mutable tags, stale inputs, architecture mismatch, or unverified output invalidate artifacts;
- a compacted session inspects a checkpoint before resuming and never duplicates a mutation;
- partial or diagnostic channels cannot satisfy a required claim;
- rehearsal or drifted evidence cannot satisfy the PR, merge, or staging gate.
