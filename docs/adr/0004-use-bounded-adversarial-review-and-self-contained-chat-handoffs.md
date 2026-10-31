# ADR-0004: Use bounded adversarial review and self-contained chat handoffs

- Status: accepted
- Date: 2026-10-31
- Owner: Project maintainer and implementing agent within task authority
- Evidence: User implementation request on 2026-10-31 for adversarial review, verified remediation and final-state review, and a self-contained PR summary directly in chat; routine design authority in Standard Development Workflow; [tracking issue](https://github.com/WilsonLe/agentic-workflows/issues/65); [implementation PR](https://github.com/WilsonLe/agentic-workflows/pull/66)
- Supersedes: none
- Superseded by: none

## Context

Engineering Review already owns review method and findings; Standard Development
Workflow owns ordinary review sequencing and PR handoff; SDLC Loop and Orchestration
own their control-plane policies. The ordinary cycle explicitly stopped after one
review, leaving fixes validated but not independently reviewed. A detailed PR body
also did not ensure users received enough information to assess a change in chat.

## Decision

Extend these existing owners. Engineering Review actively seeks supported
counterexamples across the full change and affected contracts, using risk-based
depth and explicit coverage limits. The ordinary workflow retains one cycle with
at most two reviewer invocations, counting failed, blocked and stale attempts.
After material fixes, review the final changed state within that budget. Final
clearance belongs to the reviewed base/head; fixes or drift never inherit it.
Unresolved required findings or exhausted review evidence leave the gate incomplete.

Keep reviewer independence and control-plane session rules intact. The delivery
owner evaluates findings, fixes supported in-scope defects, explains rejected or
deferred findings, and verifies fixes. Tests remain distinct from review. The
existing terminal handoff reference owns a self-contained final chat summary of
behavior, meaningful structure, rationale, review and verification evidence/limits;
the standalone loop carries its equivalent contract without a new plugin dependency.

The user's explicit implementation request authorizes this policy choice on
2026-10-31. Acceptance does not imply merge, deployment or observed compliance by
future agents. No new workflow schema, validator, scheduler or approval gate is added.

## Alternatives

Keeping a single pass would leave material fixes outside final review. Unlimited
review loops could churn without a stop decision. A separate adversarial workflow
would duplicate method and gates. A link-only chat response would require users to
open GitHub to assess the result; an exhaustive file dump would obscure behavior.

## Consequences

Some changes need a second independent pass and its associated cost. A failed or
stale second pass blocks clearance even if fixes pass focused tests; further review
needs explicit authorization. Summary detail scales to meaningful complexity, not
diff size. Canonical instructions and generated packages remain synchronized through
the existing generator. Text assertions and scenario inspection provide bounded
instruction evidence; fresh-agent behavioral trials require separate authorization.

## Revisit

Revisit with observed workflow evidence if the two-pass budget repeatedly blocks
otherwise sound changes, final-candidate review becomes stale despite the identity
checks, or users still cannot assess the resulting behavior and structure from chat.
