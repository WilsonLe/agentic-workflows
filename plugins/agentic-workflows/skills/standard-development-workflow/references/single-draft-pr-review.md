# Single automatic draft-PR review

For an ordinary implementation task, run one automatic review-and-address cycle after
opening its draft PR and before final handoff. Use the bundled
[Engineering Review](../../engineering-review/SKILL.md) skill; no additional plugin
installation is required. Explicit user limits take precedence. A verified control
plane retains its own review policy; this default does not activate autopilot.

1. Read back the live PR URL, base SHA, and committed head SHA after required local
   checks pass. Review that exact base-to-head diff against the originating request,
   all tracking issues, repository instructions, and relevant tests. Include existing
   PR comments, reviews, and unresolved threads in the feedback snapshot; a bot's
   pending review is not a completed review.
2. Retain a cycle note in the task evidence and PR comment: PR URL, reviewed base/head,
   reviewer identity, status (`started`, `reviewed`, `addressed`, or `blocked`), findings,
   disposition, resulting head, and validation evidence. On resume or PR update, read
   the existing note and continue the first incomplete step. A new fix commit, a
   refreshed base, or a resumed chat does not reset the one-cycle budget.
3. Delegate one read-only review to a separate reviewer sub-agent when supported.
   Supply the pinned revisions, request/issue links, repository instructions, and
   Engineering Review skill. The reviewer must not edit files or launch another
   reviewer. An available independent review tool may serve the same role if it can
   bind findings to the exact candidate. Never substitute the implementer's self-review
   for an independent review. If neither channel is available, or the review fails,
   keep the draft PR, record the blocker, and report the automatic cycle incomplete.
4. Read the complete review result and feedback snapshot. For each finding, record an
   in-scope fix or an evidence-backed explanation when no change is warranted. Address
   actionable feedback without a new routine permission wait. Track out-of-scope work
   and report any unresolved required findings; do not silently dismiss them. No
   findings is a valid reviewed outcome only when the reviewer actually completed.
5. After fixes, run affected verification and all repository-required pre-update
   checks. Commit and push only after they pass, update the PR evidence and cycle note,
   and read back its resulting head and checks. Report the reviewed SHA separately
   from the resulting SHA: fixes were validated, not independently re-reviewed. If
   the base or head changed outside this cycle, report stale review evidence instead
   of claiming that the new candidate was reviewed.
6. Stop after this one review and its feedback disposition. Do not request a second
   automatic review, including after fixes or a failed reviewer invocation. Read back
   newly arrived feedback at handoff and report remaining findings or pending reviews;
   they do not restart the cycle. Keep unresolved required findings visible and the
   PR draft. A clean result permits the next already-authorized workflow step, not
   merge or deployment. Do not submit a GitHub approval on behalf of the reviewer.

The cycle note is provenance, not a new workflow-record schema or review approval.
When structured task records are used, reference this evidence from their existing
verification/handoff fields. Do not mark the updated candidate's independent review
gate passed solely because its pre-fix head was reviewed.
