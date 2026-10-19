# Reflection evaluation cases

Use these cases in a dry-run review before allowing live issue writes. The reviewer must explain semantic overlap from the issue body and delivery evidence; a title match alone is insufficient.

| Observed sessions and live work | Expected disposition |
| --- | --- |
| Repeated failures suggest a new wrapper skill, but the existing skill owns the behavior and can safely express the fix. | Propose updating the existing skill; identify its callers and contracts before suggesting changes. Apply live tracker deduplication to that remedy. |
| A candidate proposes a new validator without inspecting the existing helper and schema owner. | Gather owner, caller, test, and contract evidence first; do not present the new validator as the remedy until updating the existing owner has been considered. |
| Inspection shows an existing owner's contract cannot safely express the required behavior. | Explain the limitation and considered update; only then propose a necessary new boundary using the shared design method for one responsibility, dependencies, state ownership, and validated input/output contracts. Apply live tracker deduplication independently. |
| Three projects report lost user constraints; open #121 covers preserving the contract. | Covered by open work; link #121, create zero issues. |
| Repeated verification work matches open #122. | Covered by open work; link #122, create zero issues. |
| Provider-access stalls match open #123. | Covered by open work; link #123, create zero issues. |
| Pattern-wide omission matches open #124. | Covered by open work; link #124, create zero issues. |
| Runtime trace gaps match open #125. | Covered by open work; link #125, create zero issues. |
| Availability claim before runtime proof matches open #126. | Covered by open work; link #126, create zero issues. |
| One session contains three complaints about the same root problem. | One candidate, recurrence count one. |
| Existing issue covers discovery but lacks user-visible acceptance proof. | Partially covered; add only the missing scope and cross-link. |
| Closed issue has a merged, verified fix and no current contrary evidence. | Already delivered; create zero issues. |
| Closed issue has delivered fix but current session evidence shows the behavior returned. | Regression; inspect current state, then reopen/update or create linked regression tracker. |
| Cached index says new, but a just-opened issue covers the same mechanism and acceptance criteria. | Fresh pre-write read wins; create zero issues. |
| One host or issue page is unavailable. | Report coverage gap; do not make an exhaustive or new-issue claim from that gap. |
| Transcript includes credentials and unrelated private project details. | Redact before issue body; retain only minimal evidence references. |
| Same session set and same live issue state reviewed twice. | Resolve to the same links; second run creates zero issues. |
| An every-message review reads all turn pages, but its projection clipped user corrections and omitted question replies. | Coverage remains partial until every omitted/clipped user item is expanded; read question context for short replies. Report unique messages separately from forked appearances. |
| One brief requests energy; later messages retain the mood but reject retiming, rapid pans and repeated activities. | Preserve the later constraints together, inspect the edit owner's checkpoint and change that owner. Do not globalize this project's taste or classify every creative alternative as a failure. |
| A fork repeats an earlier provider approval, followed by a new lyric-first request. | Count inherited approval once as historical evidence; the current stage remains lyric revision. It grants no new provider calls in the reflection task. |
