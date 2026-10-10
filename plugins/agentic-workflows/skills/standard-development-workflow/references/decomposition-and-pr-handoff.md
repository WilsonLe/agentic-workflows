# Issue decomposition and PR handoff

## Required many-to-many tracking

Every SDLC request has at least one tracking issue before implementation and at least one
linked PR before completed delivery. One issue may span several PRs, and one PR may deliver
several issues. Read back each pair in both directions; list all tracking issues in each PR
body and all associated PRs in each issue body or canonical comment. A reference to a
dependency does not count as implementation tracking. See [delivery tracking](delivery-tracking.md).

## Decide whether to split

Inspect the request's independently testable outcomes, coupled files and data, verification
cost, review size, and rollback boundaries. Use one issue for a cohesive change. For a broad
request, write one parent issue with the overall acceptance matrix and dependency graph, then
create the smallest useful child issues. Each child needs a deliverable, likely surfaces,
dependencies, an exact test mapping, and a contribution to the parent outcome. Use native
sub-issues when supported; preserve an explicit link otherwise. A child must be valuable and
reviewable on its own, not a ceremony-only phase.
Prefer a narrow vertical slice that makes one user-facing path work through all necessary
layers. Name the child issues that truly block it, so any unblocked child can be worked
without waiting for unrelated work. For a wide mechanical migration that cannot keep each
vertical slice green, use expand, migrate, contract steps with explicit dependencies and a
combined verification point. Do not force independent PRs where coupled changes need one
candidate to remain valid.
For a structured candidate list, `standard_workflow_record.py decomposition-plan
<request.json>` accepts `outcomes` with IDs, deliverables, cohesion groups, dependencies,
and mapped tests plus `one_pr_requested`. It groups coupled outcomes and exposes the
minimal child dependency graph for review; the agent still verifies the issue plan and
creates the actual GitHub issue relationships. An explicit one-PR request yields one delivery.

## Branch and merge topology

Create the parent issue branch from freshly verified `main`. Create isolated child branches
from the appropriate current parent head. Each child PR targets the parent branch; verify
its base and head by live readback before review or merge. Use focused development checks for
the child draft PR; at its authorized merge stage run full local tests. After those checks, exact-head CI,
required review, and verification pass against the same child head and parent base, the trusted
child delivery envelope may merge that
child PR into the parent branch automatically. Resolve conflicts and stale evidence first.
Read back the child merge, close the delivered child issue, and update the parent matrix.
Independent children may progress only with isolated worktrees and mutable test resources.

After all children merge, run focused combined checks on the parent branch and open one parent
PR targeting `main` with the child links and focused evidence. **Do not merge that PR or enable
auto-merge until the user explicitly approves merging the parent branch through that PR.**
A plan approval, child-merge authority, control-plane activation, or `$sdlc-loop` invocation
does not supply this approval. Then run the full combined integration/regression suite and local
CI. Approval persists through in-scope fixes on the same branch/PR/base, under the
[branch approval rule](../SKILL.md#approval-and-evidence-boundaries). Recheck current-head
tests, branch protection, review, base/head, and mergeability before merging or enabling
auto-merge. Deployment remains a separate gate.
Child merges do not update `main`, staging, or production. Keep parent and child branches
until their evidence is safely handed off; never delete unmerged work.
Record the live closed state of each merged child issue and its readback reference. The
parent PR record must list every child issue, its exact head/base, and the live readback
reference before approval or merge.

An explicit request for one PR, as with a grouped implementation, overrides the default
split topology for that task. Record that decision; it is not a reason to omit acceptance
coverage for the grouped components.

## Terminal PR handoff for worktree changes

For tracked code, documentation, configuration, or artifact edits in a Git worktree, finish
appropriate checks, commit and push the branch, open or update its reviewable PR, and read
back the PR URL, exact head, base, state, and checks **before the terminal user response**.
Attach it to the task when the host supports attachments. Do not stop at local edits, a
commit, or a pushed branch. An existing matching PR should be updated, not duplicated.
Record its current open/draft state, review state, and checks from the live readback.
Make the PR body easy to scan: use the smallest flow, diagram, or file map that clarifies
the change when helpful; put before/after evidence near the claim it proves; and describe
merge risk and blast radius for consequential changes. Include all repository-required
checks and release notes from the stage contract.
List changed tracked paths, including code, documentation, and configuration, in the handoff
record. Carry the existing PR URL found at intake; a new PR URL must not replace it. If remote
or permission failure blocks PR creation, record the preserved branch/commit reference and
the concrete blocker.

Pure inspection, issue/plan work with no repository diff, and an unchanged checkout do not
need empty PRs. A direct user instruction to keep changes local overrides the default and
must be recorded. If no remote, permission, branch access, or a required check prevents a
PR, continue resolving the blocker where authorized; if genuinely impossible, preserve the
work and report the exact blocker as incomplete. Opening a PR never authorizes merging or
deployment. Record mandatory `delivery_tracking`; use `pr_handoff` and `decomposition` task-record sections to validate
the recorded identities and gates.
