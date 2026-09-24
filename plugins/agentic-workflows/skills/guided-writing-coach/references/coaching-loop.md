# Coaching loop

## Build the paragraph map

Before asking for prose, map each outline item to one target paragraph. For the
active paragraph, record internally:

- its role in the larger document;
- the ideas that must be present;
- facts, qualifications, exact terms, quotations, and citations that must be
  preserved;
- ideas that belong in another paragraph; and
- the audience and any supplied length or tone constraint.

Show only a compact idea checklist. Do not turn the map into a draft.

## Multi-turn state

Track these items for the active paragraph:

- ordered user contribution identifiers and their exact text;
- the displayed working paragraph derived from those contributions;
- covered and missing ideas;
- unresolved factual, attribution, contradiction, or coherence concerns;
- any proposed structural edit and whether the user approved it; and
- paragraph status: `collecting`, `fits-awaiting-acceptance`, or `accepted`.

A user turn may contain a sentence, clause, fragment, bullet, direct edit,
complete replacement, acceptance, or question. Separate writing contributions
from control instructions. Never put words such as “accept this” or “move the
second sentence first” into the paragraph merely because the user typed them.

## Compile without ghostwriting

Append contribution text exactly as supplied. When several contributions form
one display paragraph, retain every character within each contribution and use
one space only as the display separator. Do not silently normalize spelling,
capitalization, punctuation, citation style, or grammar.

If the user asks to undo the last contribution, remove that exact contribution.
If they specify an exact replacement, use their replacement exactly. If they
supply a complete replacement, discard the prior contribution sequence and use
the replacement as the sole paragraph contribution.

For a proposed reorder or deletion:

1. keep the current paragraph unchanged;
2. identify the exact user-supplied segment or contribution involved;
3. show the proposed order or deletion without adding prose;
4. ask whether to apply it; and
5. mutate the contribution sequence only after an unambiguous approval.

## Prompting cadence

Ask one question per turn. Target the highest-priority missing or inaccurate
idea. Useful prompt forms ask the user to explain a cause, consequence,
comparison, example, qualification, connection, or reader takeaway in their
own language. Avoid sample wording and avoid stacking several questions.

If the user asks a content question, explain the idea at the concept level and
then return to one writing prompt. Do not convert the explanation into paragraph
prose unless the user later expresses it themselves.

## Accept and advance

Once the fit gate passes, ask the user to accept or revise. An explicit “accept,”
“keep this paragraph,” or equivalent freezes the exact paragraph. Then show the
next outline role and idea checklist. Never carry unused user wording into a
different paragraph without asking.
