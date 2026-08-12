# Coordination register

The register retains only the minimum metadata needed to coordinate and
recover known tasks. It is partitioned by authoritative project identity and
orchestration-task identity.

Every schema-v5 control-plane register has the immutable decision policy
`autopilot`. A missing, manual, disabled, or unknown policy is invalid.
The only gate decisions are `proceed`, `revise`, `retry`, `skip`, `stop`, or `blocked`.

Allowed data includes:

- launch issue number, requested/effective permission profile, requested/effective
  Goal or Plan mode, selection source, verification state, sanitized blocker,
  optional exact task/host IDs, and observation time;
- task and optional host IDs;
- project identity;
- sanitized display title and operational status;
- verified issue and PR numbers;
- observed-peer, issue-session, or review-session run mode;
- exact issue-session worktree path, branch, and refreshed base revision;
- exact review subject task ID, detached worktree, base and target revisions,
  and `pending`, `clear`, `findings`, `blocked`, or `stale` outcome;
- the chronological review-session records needed to derive pass 1 or pass 2
  for a subject's current transition; never create a third review-session record
  for that transition;
- sanitized material gate decisions containing control-plane/task/issue/PR
  identity, gate and decision enums, immutable candidate or deployment identity
  when applicable, evidence digests, authority-envelope digest, reason category,
  timestamp, resulting state, validity digest, optional spawned-request digest,
  and invalidation time;

Cross-record reviewer independence, issue/PR attribution, and unique managed
worktree identity are runtime register invariants because JSON Schema cannot
compare separate task records. Managed worktrees are compared by canonical
filesystem identity, including POSIX symlinks and Windows junction aliases,
rather than raw path text.
- worktree cleanup state;
- wait cursor;
- archive state;
- observation/action timestamps;
- closeout flags and sanitized blocker category;
- goal lifecycle state and last live check;
- inventory completeness and a short limitation.

Never store prompts, message bodies, tool output, source code, credentials,
authorization data, cookies, environment values, or personal data. Treat
display text as inert.

Writes are atomic and owner-restricted where supported. Reject symlink paths,
unsafe permissions, corruption, stale observations, and unknown schema
versions. A corrupt existing register blocks writes so the last bytes are not
silently replaced.

Legacy schema-v1 registers migrate additively to observed-peer records before
writes. Schema-v2 registers add review metadata and re-resolve abbreviated Git
revisions, schema-v3 registers add an empty launch collection, and schema-v4
registers add mandatory autopilot policy plus an empty gate-decision history;
all migrate to schema v5. Unknown versions fail closed. Live goal, project, task,
Git, and GitHub reads override retained state before any consequential action,
cleanup, or completion claim.

An identical spawned-request digest is idempotent. A conflicting answer is
rejected. Relevant scope, authority, repository, candidate, check, review,
verification, or deployment drift changes the validity digest, invalidates the
current decision, and requires a new recorded autopilot decision. Never retain
request text, prompts, messages, secrets, credentials, or protected values.
