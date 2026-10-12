# Evaluation scenarios

Use these realistic tasks when testing the skill's behavior. They are authored acceptance cases, not proof that a model passed them. Run them in a disposable project or against authorized fixtures. Record the task, starting context, output, inspected states, and failures. A package-validator pass establishes packaging, not frontend quality.

## 1. Empty student workspace

Prompt: “Build a student dashboard for a new account with no assigned lessons. We want a quiet, minimal start.”

Expected behavior: identify how the learner gets work; show useful orientation and the next step; defer irrelevant progress/reward detail; avoid invented activity, populated statistics, or dead controls. Inspect the transition to a populated lesson and verify the primary action works.

Failure signals: a wall of empty cards, fabricated achievements, or a blank page with no route forward.

## 2. Instructor authoring

Prompt: “Create a quest editor with title, description, objectives, levels, saved draft state, publishing, and version history.”

Expected behavior: coherent authoring sections; expandable secondary detail; truthful saving/publishing states; visible prerequisites/consequences before commitment; keyboard-accessible disclosure and preserved input. Publishing must actually work or be explicitly described as unavailable in the prototype.

Failure signals: auto-publishing during preview, hidden errors, collapsed fields losing input, or false saved state.

## 3. Manager comparison and bulk work

Prompt: “Managers compare 40 members by role and status, then archive selected records. Reduce clutter without slowing the workflow.”

Expected behavior: keep role/status comparison visible, direct search/filtering, contextual selection actions, selection count, and history/details on demand. Verify selection and cancellation with fixtures.

Failure signals: a wizard per member, hidden comparison columns, charts with no management question, or an unclear bulk-action target.

## 4. Existing expressive system

Prompt: “Our app has a playful dark theme and established components. Improve the lesson resource disclosure only.”

Expected behavior: preserve the accepted theme and components, scope edits to disclosure, use a labeled accessible entry and sensible back/focus behavior. Apply minimalism to relevant information and structure.

Failure signals: force a white monochrome restyle, replace the stack, or infer that all cards and color are forbidden.

## 5. Accessible onboarding

Prompt: “Make a three-stage setup for dependent workspace choices. It must work by keyboard and on mobile.”

Expected behavior: steps justified by dependency, progress, revisitable choices, preserved values, local errors, visible critical context, and sensible focus handling. Test narrow viewport and keyboard progression/back.

Failure signals: hover-only help, hidden prerequisites, lost choices on Back, or a step structure used merely for visual sparseness.

## 6. Scope, evidence, and learning

Prompt: “Review this dashboard; don't edit it. Our design notes say managers need all comparison columns visible. Next time, remember that I prefer fewer summary panels.”

Expected behavior: read and respect notes, give concrete prioritized findings without implementation, keep useful columns, distinguish the explicit correction from an unconfirmed hypothesis. Explain a scoped update to project notes or supply the proposed note if edits are excluded. State which states could not be inspected.

Failure signals: unauthorized code/note edits, globalizing the correction to every product, claiming inaccessible app behavior was verified, or presenting source comparisons as benchmark results.
