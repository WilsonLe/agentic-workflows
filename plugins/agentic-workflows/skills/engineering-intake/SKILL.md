---
name: engineering-intake
description: Triage a software issue or pull request, clarify product decisions, and turn an agreed outcome into a spec or dependency-aware implementation slices.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering intake

Use this skill when the work is still being defined. Read the repository's issue, PR, and decision conventions first. Inspect the live request, comments, relevant code, related issues, and prior decisions before recommending a disposition. For tracked edits, follow the repository's delivery rules and the Codex Standard Development Workflow when available. This skill does not grant permission to publish, merge, or deploy.

## Triage

1. Separate the report's claim from verified behavior. For a bug, attempt a safe reproduction on the named revision and environment. For a PR, inspect its diff and applicable checks. Search for an existing implementation and related open or closed work by concept as well as wording.
2. Recommend a disposition using the repository's existing labels or states. Typical outcomes are ready to implement, needs a specific answer, needs human judgment, already delivered, or declined. Do not invent labels or close another person's request without the authority the task provides.
3. When information is missing, preserve what is settled and ask only for decisions or facts that cannot be found from the sources. Make each question actionable. Read prior answers before asking again.
4. For ready work, leave a durable brief: user outcome, verified present behavior, scope, acceptance evidence, constraints, dependencies, and open decisions. Link the primary source and record what could not be verified.

## Clarify decisions

For ambiguous product or design work, map which decisions depend on others. Present the decisions that can be made now as a small group, with concrete options and a recommended answer where evidence supports one. Let the user's answers expose the next group. Check environmental facts yourself before posing a product choice. Stop the interview when the remaining choices are implementation details within the authorized scope.

When a shared product term is ambiguous, compare the user's meaning with code and existing documentation. Record a settled domain term in the project's chosen glossary only if that glossary exists or the repository needs a durable vocabulary for this work. Record a decision in an ADR only when it involved a material tradeoff, will be costly to reverse, and would surprise a future maintainer without its rationale.

## Prepare implementation

- Synthesize decisions already present in the conversation into the issue or spec. Do not interview the user again to rediscover agreed answers.
- Describe externally observable behavior, important edge cases, out-of-scope work, and where evidence will establish completion. Identify the highest useful test seam that exercises the real behavior.
- For a large outcome, propose independently verifiable vertical slices, each covering the layers needed to make one user-facing path work. Record true blocking relationships. Keep a wide mechanical migration as an explicit expand, migrate, contract sequence when individual vertical slices cannot remain green.
- Size slices so each can be reviewed and validated independently. Preserve the parent outcome and combined acceptance evidence under the repository's decomposition rules.

Publish or edit issues only when the user has authorized that external work. Give the user a concise readback of the resulting issue, brief, or proposed breakdown.
