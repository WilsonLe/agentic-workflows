# Single bounded automatic draft-PR review cycle

For an ordinary implementation task, run one bounded adversarial review-and-address
cycle after opening its draft PR and before final handoff. Use the bundled
[Engineering Review](../../engineering-review/SKILL.md) skill; no additional plugin
installation is required. Explicit user limits take precedence. A verified control
plane retains its own review and independence policy; this default does not activate autopilot.

1. Read back the live PR URL, base SHA, and committed head SHA after focused development
   checks pass. Full-suite checks remain deferred until merging is requested. Review
   the complete exact base-to-head diff and affected contracts against the originating
   request, all tracking issues, repository instructions, and relevant tests. Include
   existing PR comments, reviews, and unresolved threads in the feedback snapshot;
   a bot's pending review is not a completed review.
2. Retain a cycle note in the task evidence and PR comment: PR URL, each started pass,
   reviewed base/head, reviewer identity, status (`started`, `reviewed`, `addressed`,
   or `blocked`), coverage/limits, findings and disposition, resulting head, and
   validation evidence. On resume or PR update, read the existing note and continue
   the first incomplete step. A fix commit, refreshed base, or resumed chat does not
   reset the one-cycle budget. Count a pass when its reviewer is invoked; failed,
   blocked, or stale attempts consume a pass. Allow at most two passes in this cycle.
3. Delegate a read-only adversarial review to a separate reviewer sub-agent when
   supported. Supply pinned revisions, request/issue links, repository instructions,
   and Engineering Review skill. The reviewer must not edit files, launch another
   reviewer, or schedule a pass. An available independent review tool may serve the
   same role if it binds findings to the exact candidate. Never substitute the
   implementer's self-review for an independent review. If neither channel is
   available, keep the draft PR, record the blocker, and report the automatic cycle incomplete.
4. Read the complete review result and feedback snapshot. Evaluate every finding
   against the candidate and supported contracts. Fix supported in-scope issues;
   record evidence-backed reasons for rejected findings and the impact, owner, and
   required decision for deferred/out-of-scope work. Do not silently dismiss required
   findings. No findings is a valid outcome only when the reviewer actually completed
   the relevant coverage; passing tests do not substitute for review.
5. After fixes, run affected focused verification and relevant static/generated checks.
   Do not run the full suite unless merging is already requested. Commit and push only
   after applicable checks pass, update PR evidence and the cycle note, and read back
   the resulting base/head and checks. Material fixes change behavior, acceptance,
   interfaces, state/failure contracts, or the evidence supporting clearance. Review
   the final changed state again after such fixes: use pass 2 with an independent
   reviewer, the full updated diff and contracts, prior findings/dispositions, and
   verification results. Prioritize fixes and their interactions without omitting
   other relevant changes. For any base/head drift, reconcile review evidence to the
   final PR head before claiming clearance; never carry an old SHA's review forward
   merely because a new commit looks trivial. If pass 1 fails or becomes stale,
   pass 2 may recover within the same budget; otherwise report the blocker.
6. Stop when the unchanged final base/head has completed required review with all
   findings dispositioned and required findings resolved, or when two passes are
   consumed. Pass 2 is final: later fixes may be implemented and verified within
   authority, but their changed candidate remains unreviewed until further review is
   explicitly authorized. Never start pass 3 automatically or reset the budget by
   renaming a cycle. Read back new feedback and live base/head at handoff. Unresolved
   required findings, incomplete coverage, failed review, or drift leave the review
   gate incomplete and PR draft. A clear result permits the next already-authorized
   workflow step, not merge or deployment. Do not submit a GitHub approval on behalf
   of the reviewer.

The cycle note is provenance, not a new workflow-record schema or review approval.
When structured task records are used, reference it from existing verification/handoff
fields. Report each reviewed SHA separately from the final PR head, and distinguish
verified fixes from independently reviewed fixes. Finish with the
[self-contained chat summary](decomposition-and-pr-handoff.md#self-contained-chat-summary).
