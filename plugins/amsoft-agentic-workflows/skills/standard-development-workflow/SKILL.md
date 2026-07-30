---
name: standard-development-workflow
description: Deliver repository changes through an isolated worktree, provenance-backed discovery, an explicit execution contract, fail-fast and state-isolated verification, a frozen evidence handoff, a reviewed draft PR, safe cleanup, and separately approved staging. Use when the user asks to build, fix, change, or ship software with the Standard Development Workflow, requests a spec-first worktree-to-PR process, or asks to resume one of its stages.
---

# Standard Development Workflow

Run one traceable change from request to reviewed staging. Repository evidence controls exact
commands and capabilities; the stage contracts control sequencing and approval. Use concise
human-readable readbacks in conversation. Structured records preserve provenance across long runs,
handoffs, and compaction without becoming user-facing ceremony.

For onboarding or first use, read [references/onboarding.md](references/onboarding.md). Before
starting work, read the operating references that apply:

- [references/stage-contracts.md](references/stage-contracts.md)
- [references/spec-ready.md](references/spec-ready.md)
- [references/worktree-bootstrap.md](references/worktree-bootstrap.md)
- [references/verification-deployment-cleanup.md](references/verification-deployment-cleanup.md)
- [references/workflow-record-model.md](references/workflow-record-model.md)
- [references/discovery-contract-and-scope.md](references/discovery-contract-and-scope.md)
- [references/validation-state-and-resume.md](references/validation-state-and-resume.md)
- [references/verification-evidence-and-release.md](references/verification-evidence-and-release.md)
- [references/evaluation-matrix.md](references/evaluation-matrix.md)

Read the shared record model every time structured records are used. Read the remaining focused
references only when their capability is required or uncertain.

## Non-negotiable sequence

1. Perform only the minimum read-only checks needed to resolve the repository, canonical checkout,
   base branch, current worktrees, dirty state, and local instructions.
2. Create a new feature branch in a separate Git worktree before issue research, planning, editing,
   dependency installation, or service startup.
3. Reuse a still-valid repository capability profile or refresh only the sections whose evidence
   changed. Fully onboard the worktree from repository evidence.
4. Research the request deeply enough to create or refine one spec-ready GitHub issue.
5. Produce the task execution contract, minimal-change envelope, resource budget, validation
   ladder, and verification-channel plan. Post that complete plan as the one canonical pinned
   GitHub issue comment, read it back, and record its stable comment identity. Activate failure,
   sandbox, artifact, checkpoint, and evidence records only when applicable.
6. Present the issue and canonical pinned plan comment, request explicit approval, and stop. Do
   not implement.
7. After approval, implement only the approved envelope. Reconcile the pinned plan comment at
   implementation start and after material findings, updating that same comment in place with
   status, decisions, findings, and changed test mappings. Run cheap prerequisites before
   expensive work, classify failures before remedies, isolate mutable validation state, and
   resume rather than duplicate long operations.
8. Freeze the candidate before final evidence. Open or update a draft pull request only after the
   complete required local checks and evidence-identity checks pass. Present the evidence, request
   review, and stop.
9. After an explicit approval message, re-check the PR and required checks, mark it ready if needed,
   squash-merge by default, and fast-forward the canonical checkout.
10. Clean up the feature worktree, feature runtime, and merged branch exhaustively but safely.
11. If the repository has a staging environment, ask separately for permission to deploy. Stop
    until approved.
12. After staging approval, deploy from the merged canonical revision, repeat the applicable local
    verification against staging using its real endpoints, report evidence, and stop for review.
13. Never deploy to production automatically.

## Approval interpretation

- Plan approval authorizes only the documented implementation and local test plan.
- PR approval messages such as “approved”, “looks good, merge”, or “squash merge and pull” authorize
  the default squash merge and canonical fast-forward pull when the target PR is unambiguous.
- A status request, silence, partial feedback, or approval of a different artifact is not approval.
- Staging deployment always needs its own explicit approval after merge and synchronization.
- Production deployment always requires a new, explicit user request outside this workflow.
- When feedback changes scope, update the issue and plan. Re-open the plan gate if the change is
  material; update the canonical pinned plan comment in place and keep an audit trail rather than
  silently broadening the work. Never create a second authoritative plan comment.
- A verification-channel fallback that proves less than the approved channel is not plan approval
  and cannot satisfy completion.
- Shared cache, infrastructure, or host-wide reclamation requires exact impact disclosure and a
  separate explicit approval.

## Evidence and safety rules

- Obey repository `AGENTS.md`, contributing docs, CI configuration, deployment runbooks, and the
  actual application behavior. Do not invent commands, behavior, credentials, or success.
- Preserve unrelated dirty or untracked files in every checkout.
- Never print, commit, attach, or paste secret values. Environment files copied into the worktree
  remain local and ignored.
- Keep issue, branch, commits, pull request, checks, merge revision, deployment, and verification
  mutually linked where the platform supports it.
- Treat repository capability profiles as cached evidence, never authority. Validate repository
  identity and evidence digests before reuse; recheck transient external state when applicable.
- Never store secret values, environment values, protected data, or broad home-directory state in
  workflow records. Environment key names and credential requirements may be recorded.
- A failed prerequisite blocks dependent expensive work. Unknown required failures block review.
- Mutable tags, filenames, paths, and timestamps do not establish reusable artifact identity.
- Rehearsal screenshots, videos, or reports are not final evidence. Final evidence binds to the
  committed clean candidate and invalidates on relevant source, test, workflow, artifact, or
  evidence drift.
- Do not weaken tests, bypass branch protection, dismiss findings, or force a merge merely to make
  the workflow pass.
- Prefer a draft PR as the review artifact. Do not interpret draft status as permission to skip
  checks.
- If the repository cannot support a safe worktree, isolated runtime, GitHub issue, or required
  approval gate, stop at the affected stage and report the exact blocker.

## Structured record helper

The bundled dependency-free helper validates the shared schema and semantic cross-record rules:

```bash
python3 <skill-root>/scripts/standard_workflow_record.py validate <task-record.json> \
  --profile <repository-profile.json> \
  --source-root <repository-root>
python3 <skill-root>/scripts/standard_workflow_record.py summary <task-record.json>
```

Use `--require-final` at the draft-PR, merge-readiness, and applicable staging evidence gates.
Canonicalize or digest a record with the corresponding helper subcommand. The helper does not
approve work, execute repository commands, delete resources, or access credentials.
