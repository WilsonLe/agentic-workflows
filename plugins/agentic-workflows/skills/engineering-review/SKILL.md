---
name: engineering-review
description: Review a software diff against its originating request and repository standards, then summarize findings, evidence, and merge risk for a PR handoff.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Engineering review

Use this skill for a branch, PR, or working diff review. It is an analysis method, not merge authority. Keep the repository's independent-review and exact-candidate requirements when they apply.

1. Pin the comparison point and candidate revision. Confirm both resolve and capture the actual diff, commit list, and changed surfaces. If the base is ambiguous, explain the candidate comparison before treating a finding as definitive.
2. Read the originating request, issue, or spec. If none exists, state that the requirements axis is limited. Read repository standards, local instructions, and relevant architecture decisions. Let repository rules override generic style preferences and avoid repeating automated lint findings.
3. Review on two independent axes:
   - **Requested behavior:** missing, partial, incorrect, or unrequested behavior; cite the source requirement and affected code or evidence.
   - **Engineering quality:** concrete violations of repository rules, likely defects, and maintainability problems introduced by the diff; distinguish required fixes from judgment calls.
4. Report findings with file and line, consequence, and a feasible correction. Keep the two axes distinct so a clean style review cannot hide a missed requirement. State what you checked, what you could not check, and whether the reviewed revision changed afterward.

For a PR handoff, make the summary easy to scan: the smallest diagram, flow, or file map that clarifies the change when one helps; before/after evidence tied to the candidate; and a short account of merge risk, blast radius, and rollback where relevant. Include the repository's required local checks and documentation-impact result. Follow its PR template and approval rules if they prescribe more detail.
