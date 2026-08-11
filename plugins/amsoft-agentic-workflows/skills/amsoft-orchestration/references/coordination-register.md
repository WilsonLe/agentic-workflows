# Coordination register

The register retains only the minimum metadata needed to coordinate and
recover known tasks. It is partitioned by authoritative project identity and
orchestration-task identity.

Allowed data includes:

- task and optional host IDs;
- project identity;
- sanitized display title and operational status;
- verified issue and PR numbers;
- observed-peer or issue-session run mode;
- exact issue-session worktree path, branch, and refreshed base revision;
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
writes. Unknown versions fail closed. Live goal, project, task, Git, and GitHub
reads override retained state before any consequential action, cleanup, or
completion claim.
