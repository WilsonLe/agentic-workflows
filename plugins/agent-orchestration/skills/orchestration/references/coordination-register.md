# Coordination register

The register retains only the minimum metadata needed to coordinate and
recover known tasks. It is partitioned by authoritative project identity and
orchestration-task identity.

Allowed data includes:

- task and optional host IDs;
- project identity;
- sanitized display title and operational status;
- verified issue and PR numbers;
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

Live goal and task reads override retained state before any consequential
action or completion claim.
