# Project UI conventions across tasks

For UI work, inspect the project's existing instructions, design-system guidance, shared
components, and explicit approved decisions before choosing copy or controls. Reuse only
conventions applicable to this repository and changed surface. A prior task's isolated screen
correction is not automatically a project-wide rule; another project's style is never authority.

Use a short section in existing project guidance when authorized work establishes a reusable
rule. No mandatory new file, history ingestion, or global memory write is needed. Record:

| Convention | Project and surface scope | Approved source | Exceptions or superseding source |
| --- | --- | --- | --- |
| Concise functional copy | This project's application screens | Explicit user decision or project guide | Keep useful errors, accessible labels, and decision-support text |
| Shared controls and theme | Named component consumers | Current design-system guide | Document a semantic or accessibility exception |

At intake, choose current applicable rules using their sources, not frequency of old complaints.
An explicit newer decision supersedes the affected older rule. If generalizing an ambiguous
choice would materially change scope, ask one grouped question; otherwise keep it screen-local.
Do not request confirmation again for a clear existing project convention.

Before delivery, compare changed copy, components, typography/theme tokens, and feedback states
against the applicable rules, then inspect representative rendered states. Fix conflicts or
record a justified exception supported by the current request. Preserve meaningful errors,
accessibility labels, and essential user choices. Avoid brittle exact-word tests or screenshots
of unchanged screens. Update warranted guidance in the same PR; do not redesign unrelated pages.

Optional `ui_conventions` in a task record binds each review to repository identity, source,
surface, and current/superseded status. Only current applicable rules participate in delivery.
A failed or unreviewed applicable rule blocks final evidence; an exception needs a reason.
The validator checks recorded decisions, not the truth of screenshots or preference provenance.

Fresh-task evaluations: Project A has an explicit concise-copy/shared-Select rule and a new
screen must consume it; Project B has no such rule and must not inherit it. A screen-local
correction must not spread. A newer decision must override only the affected rule. Inject a
redundant subtitle and native select to demonstrate a detected conflict, then verify the corrected
render still includes error and accessibility text. Do not use instruction-string tests alone.
