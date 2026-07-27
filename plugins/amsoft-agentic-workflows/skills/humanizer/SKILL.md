---
name: humanizer
description: Rewrite or review prose to remove AI-writing patterns, preserve meaning, match a natural or supplied voice, and onboard users to Humanizer. Use for setup or first-run guidance, or when the user asks to humanize, de-AI, de-slop, un-ChatGPT, voice-match, or check text for AI tells.
---

# Humanizer

Rewrite prose so it sounds specific, natural, and appropriate to its context. Preserve the writer's meaning and factual claims while removing formulaic AI patterns.

For setup, onboarding, or first-use requests, read
[references/onboarding.md](references/onboarding.md) and follow its bounded sample workflow.

This skill adapts Hermes Agent's built-in `creative/humanizer` v2.5.1. Read [references/hermes-humanizer-v2.5.1.md](references/hermes-humanizer-v2.5.1.md) when performing a full pattern audit, when examples would help, or when the user explicitly asks for the Hermes method.

## Core rules

- Preserve meaning, commitments, uncertainty, names, figures, and citations unless the user asks to change them.
- Never invent facts, sources, quotes, personal experiences, emotions, opinions, or voice quirks to make text seem human.
- Match the requested register: casual, professional, academic, technical, promotional, or another stated tone.
- Treat a supplied writing sample as the strongest voice reference. Copy its rhythm and level of formality, not its unrelated facts or distinctive phrases verbatim.
- Prefer concrete wording and simple sentence construction where they improve clarity.
- Keep intentional domain language, necessary structure, accessibility, and legal or technical precision.
- Do not make text worse merely to make it less polished. Natural writing can still be careful and grammatically clean.
- Do not claim that a rewrite evades AI detection. Detection is unreliable; describe the work as style editing.

## Workflow

1. Read the complete input and identify its purpose, audience, tone, and non-negotiable facts.
2. If the user supplies a voice sample, note its sentence length, vocabulary, paragraph openings, punctuation, transitions, and recurring habits.
3. Scan for the pattern groups below. For a thorough audit, load the Hermes reference.
4. Rewrite only what needs rewriting. Keep strong, natural passages intact.
5. Read the result aloud mentally. Fix repetitive cadence, forced transitions, vague claims, and over-tidy structure.
6. Run a final private audit: ask what still makes the prose sound generated, then revise once more.
7. Return the polished rewrite first. Add a short change summary only when it helps or the user asks for analysis.

For a file, inspect it before editing, make the smallest coherent change, preserve its format, and show the changed section or a concise diff summary.

## Pattern checklist

Check for these 34 patterns from the Hermes skill:

1. Inflated claims about significance, legacy, or broader trends
2. Notability claims based on media lists rather than substance
3. Superficial `-ing` phrases that add fake analysis
4. Promotional language where a neutral description is needed
5. Vague attribution and weasel words
6. Formulaic "challenges and future prospects" sections
7. High-frequency AI vocabulary and business clichés
8. Avoiding simple forms of `is`, `are`, and `has`
9. "Not only...but" framing and clipped tailing negations
10. Forced groups of three
11. Synonym cycling to avoid ordinary repetition
12. False "from X to Y" ranges
13. Passive voice or subjectless fragments that hide the actor
14. Em-dash overuse
15. Mechanical boldface
16. Vertical lists with bold inline headers when prose is clearer
17. Title Case headings
18. Decorative emojis
19. Curly quotation marks when the surrounding style uses straight quotes
20. Chatbot artifacts such as "I hope this helps" or "let me know"
21. Knowledge-cutoff disclaimers left inside the prose
22. Sycophantic or servile tone
23. Filler phrases
24. Excessive hedging
25. Generic positive conclusions
26. Unnaturally consistent hyphenation
27. Persuasive-authority tropes such as "the real question is"
28. Announcing the explanation instead of giving it
29. Headings followed by a sentence that merely restates the heading
30. Forced metaphors and figurative overwriting
31. Dramatic fragments and slogan-like kickers
32. Rhetorical questions answered immediately
33. Repetitive sentence-opening tics
34. Unasked-for reassurance kickers

Apply judgment. A listed feature is not automatically wrong; remove it when it is repetitive, vague, performative, or mismatched to the writer's voice.

## Output

Default to only the final rewrite. If the user asks for an audit, provide:

1. The revised text
2. A compact list of the strongest patterns found
3. Any meaning, factual, or tone decisions that require the user's confirmation

When the source contains unsupported claims, preserve them only if the task is purely stylistic and flag them briefly. Do not silently strengthen or fabricate support.

## Attribution

Adapted from Hermes Agent's built-in Humanizer v2.5.1, ported by Hermes Agent from Siqi Chen's `blader/humanizer`. The original and this adaptation are distributed under the MIT License in [LICENSE](LICENSE).
