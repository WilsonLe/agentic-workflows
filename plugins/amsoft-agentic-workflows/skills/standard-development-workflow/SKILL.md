---
name: standard-development-workflow
description: Deliver repository changes through an isolated and fully onboarded Git worktree, a research-backed spec-ready GitHub issue, an exhaustive implementation and test plan with explicit approval, implementation and local verification, a draft pull request and review gate, squash merge plus canonical pull and exhaustive worktree cleanup, and a separately approved staging deployment with repeated verification. Use when the user asks to build, fix, change, or ship software with the Standard Development Workflow, requests a spec-first worktree-to-PR process, or asks to resume one of its stages.
---

# Standard Development Workflow

Run one traceable change from request to reviewed staging. Repository evidence controls the exact
commands; the stage contracts control sequencing and approval.

For onboarding or first use, read [references/onboarding.md](references/onboarding.md). Before
starting work, read all four operating references:

- [references/stage-contracts.md](references/stage-contracts.md)
- [references/spec-ready.md](references/spec-ready.md)
- [references/worktree-bootstrap.md](references/worktree-bootstrap.md)
- [references/verification-deployment-cleanup.md](references/verification-deployment-cleanup.md)

## Non-negotiable sequence

1. Perform only the minimum read-only checks needed to resolve the repository, canonical checkout,
   base branch, current worktrees, dirty state, and local instructions.
2. Create a new feature branch in a separate Git worktree before issue research, planning, editing,
   dependency installation, or service startup.
3. Fully onboard that worktree: instructions, prerequisites, dependencies, local-only environment
   files, and isolated runtime configuration.
4. Research the request and repository deeply enough to create or refine one spec-ready GitHub
   issue.
5. Create an exhaustive implementation and verification plan linked to that issue.
6. Present the issue and plan, request explicit approval, and stop. Do not implement.
7. After approval, implement the approved scope and run the planned local verification.
8. Open or update a draft pull request only after the relevant local checks pass. Present the
   evidence, request review, and stop.
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
  material; keep an audit trail rather than silently broadening the work.

## Evidence and safety rules

- Obey repository `AGENTS.md`, contributing docs, CI configuration, deployment runbooks, and the
  actual application behavior. Do not invent commands, behavior, credentials, or success.
- Preserve unrelated dirty or untracked files in every checkout.
- Never print, commit, attach, or paste secret values. Environment files copied into the worktree
  remain local and ignored.
- Keep issue, branch, commits, pull request, checks, merge revision, deployment, and verification
  mutually linked where the platform supports it.
- Do not weaken tests, bypass branch protection, dismiss findings, or force a merge merely to make
  the workflow pass.
- Prefer a draft PR as the review artifact. Do not interpret draft status as permission to skip
  checks.
- If the repository cannot support a safe worktree, isolated runtime, GitHub issue, or required
  approval gate, stop at the affected stage and report the exact blocker.
