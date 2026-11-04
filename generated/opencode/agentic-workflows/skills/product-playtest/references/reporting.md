# Playtest report contract

Write for the person using or improving the product. Lead with what the user can
and cannot comfortably accomplish. Describe controls using their visible names.
Prefer “After I press Back, my answer is gone and I have to type it again” over
“State hydration is broken.” First person may describe your actual browser actions;
do not impersonate a human research participant, invent emotions, or claim user-study
results. Observed behavior and its likely user consequence are separate claims.

## Shape of the report

Use the project's existing report format when it preserves these elements:

1. **Experience:** a brief account of the primary goal, outcome, and biggest friction.
   Point to the most important finding IDs rather than repeat their full text.
2. **Context and coverage:** target/environment/build when known, date, role, actual
   browser/channel, viewport/input method, journeys/screens/states exercised, and
   blocked or untested areas with reasons. Distinguish completed, partial, blocked,
   and not applicable coverage; a list of visited pages alone is insufficient.
3. **Prioritized findings:** every distinct actionable observation, including tiny
   details. Group by priority and then journey/screen when that improves scanning.
   Each entry includes a stable ID, priority, concrete title, location/trigger,
   observation, user impact, suggested improvement, and evidence/confidence.
4. **Preserve and next:** useful behaviors worth keeping, a short suggested order
   for improvements, and remaining exploration. Do not imply fixes were made.

One compact paragraph can contain all finding fields. Use steps or extra detail
when the behavior is harder to reproduce. Put screenshot references beside the
relevant finding. For a long report, provide a navigable complete artifact plus
a concise reply with its link and top findings. Do not present only a “top five”
and discard the remaining notes. Include a compact grouped small-details list
when helpful, preserving IDs, locations, evidence, and a useful improvement for
each distinct issue. Avoid a wide table with paragraphs squeezed into every cell.

## Worked excerpt

This is fictional output showing specificity and voice, not product evidence:

> I could create a draft and find it again after refreshing. Editing it was less
> reliable: returning from the preview erased my latest answer (PT-01). The save
> confirmation also left me unsure which changes had been saved (PT-02).
>
> Context: test workspace, learner role, build not exposed; supported browser,
> 390 × 844 viewport, keyboard and pointer. Covered: draft creation and re-entry;
> editing, preview, Back, and empty-title validation. Untested: instructor access
> (no account), real touch input, and publication (outside this session's authority).
>
> **PT-01 · P1 · Returning from preview erases my answer.** In Draft → Answer, I
> typed a new answer, opened Preview, then pressed its Back button. The answer
> field was empty on both attempts, so I would have to recreate my work. Preserve
> the answer when returning. Observed behavior; reproduced 2/2; action notes A1–A4.
>
> **PT-02 · P2 · “Done” does not tell me what was saved.** After I change the title
> and press Save, the toast says “Done” without identifying the draft or action.
> The updated title does persist after refresh, but the feedback leaves its meaning
> implicit. Say “Draft saved” and make any unsaved state clear. Design judgment
> grounded in observed copy and persistence; screenshot S2.
>
> **PT-03 · P3 · The last word of the button disappears on a narrow screen.** On
> Draft → Preview at 390 × 844, the primary button reads “Continue to…” although
> space remains below it. I cannot tell where it leads. Let the full destination
> wrap or use a shorter complete label. Observed behavior; screenshot S3.
>
> **PT-04 · P3 · “Answer” and “Response” name the same field.** Editing calls it
> “Answer”; Preview calls it “Response.” The change makes me check whether they
> are different things. Keep one term across both screens. Design judgment based
> on the two visible labels; screenshots S1 and S3.

The excerpt is intentionally incomplete coverage. In a real report, retain every
distinct finding, support actual claims with actual evidence, and state unknowns.
Do not copy these examples as findings or infer implementation causes from them.
