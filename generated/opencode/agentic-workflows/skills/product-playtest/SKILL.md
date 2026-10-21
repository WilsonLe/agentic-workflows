---
name: product-playtest
description: Use this skill whenever the user asks to playtest an app, try a product as a user, explore it in the browser, or note what could improve the experience. Opens and uses the actual product, exhaustively records friction and tiny details, and returns prioritized, evidence-backed improvements from the user's perspective.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Supported browser controls and reachable app** — Provide a running app or URL and supported host browser controls; use authorized test accounts or disposable fixtures for state-changing journeys.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Product Playtest

Experience the product through its browser interface as a user trying to get
something done. Notice everything that affects that experience, from a blocked
journey to a one-word ambiguity or a small alignment problem. Deliver clear,
concise yet detailed findings; exhaustive observation does not require repetitive prose.

This skill owns exploration, observation, coverage, and reporting. For design
judgment, read [UI Design](../ui-design/SKILL.md) and its applicable disclosure,
role, and visual/interaction references. Preserve the product's accepted design
system and purpose. Use those criteria to explain observed friction, without
turning the session into an unsolicited redesign or code review.
Its implementation and UI-change delivery steps apply only when implementation
is separately requested; this skill's browser-first sequence owns the playtest.

## Establish the experience

Resolve the target URL or running app, environment, intended user/role, goals,
supplied scope, and authorized test data from the request and available context.
Read relevant product guidance and prior findings. Ask only for missing information
that blocks useful exploration; continue independent authorized work meanwhile.

Follow [browser selection](../agentic-workflows/references/browser-selection.md).
Read the host browser tool's documentation, open the actual target, and record
the browser/channel, date, environment, account role, viewport, and visible build
identity when available. Use supported browser controls to click, type, navigate,
and inspect the rendered result. APIs, source inspection, static screenshots,
and automated test passes can supplement a playtest; they cannot replace it.

Use available authorized accounts and disposable fixtures for ordinary in-scope
interactions. Check an action's actual effect before committing it. A playtest
request alone does not authorize purchases, paid generation, publication, messages
to others, deletion of real data, or unrelated account/permission changes. Exercise
safe previews and cancellation, record the specific untested boundary, and continue
elsewhere. Reuse existing explicit authority rather than asking again. Keep private
data and credentials out of evidence. Report findings without fixing the app,
creating external issues, or changing project instructions unless requested.

If the app, login, or required browser capability is unavailable, record the exact
blocker and reachable coverage. Do not call a source-only review a completed playtest.

## Explore as a user, then inspect the details

Keep a lightweight coverage list and observation notes in task context or an
existing requested report location. Track screens/journeys, roles, states, input
methods/viewports, findings, evidence, and what remains. Use stable finding IDs so
later discoveries and interrupted sessions can extend the same report.

1. **First arrival:** before using source code or developer explanations to find
   your way, record what the product itself communicates: what it does, where you
   are, the next useful action, and any uncertainty. Describe the observed cues
   rather than inventing how a human participant felt or how long they took.
2. **Real goals:** complete the primary journeys from entry to a visible outcome.
   Follow the interface's labels and cues. Inspect the resulting state and, where
   relevant and authorized, revisit or refresh to see whether the result persists.
   Note extra steps, dead ends, misleading success, lost context, and recovery effort.
3. **Breadth:** visit every reachable in-scope screen, navigation branch, menu,
   dialog, tab, settings area, and secondary action. Use the scope to bound the
   product, not an arbitrary number of screens or findings. Include each authorized
   role with a distinct experience; do not claim roles you could not enter.
4. **States and recovery:** exercise applicable empty/populated, loading/success,
   invalid/error, disabled, expanded/selected, cancellation, retry, and back/forward
   states. Try representative short/long/blank inputs, no-results searches, filter
   combinations, and repeated use where meaningful. Use controlled fixtures for
   failures; do not disrupt a live service to force an error.
5. **Detail pass:** inspect each visited surface using the observation sweep below.
   Revisit states hidden behind hover, focus, selection, scrolling, and dialogs.
   Check a representative narrow viewport and keyboard journey where supported;
   record actual dimensions and input methods. A resized desktop viewport does not
   establish touch behavior or real-device compatibility.

Keep the first-use observations even when later exploration reveals an explanation.
Do not stop at the first broken journey: capture it, mark downstream coverage blocked,
and explore independent paths. Group repeated manifestations only when they represent
the same user problem, retaining all affected locations and meaningful differences.
Do not discard a small issue because larger issues exist, or invent defects to fill
a quota. Keep design preferences and improvement hypotheses distinct from observed bugs.

### Observation sweep

Apply these lenses to the product's actual purpose; mark irrelevant or unreachable
areas rather than inventing a feature or forcing a universal checklist:

- **Orientation and flow:** entry cues, navigation names, active location, primary
  versus secondary actions, unnecessary steps, back paths, context and scroll retention.
- **Value and pacing:** whether the journey delivers its promised outcome, whether
  instructions and content help the task, repetition, interruptions, effort, and
  completion feedback. Ground judgments about enjoyment, motivation, or trust in
  observed interactions; do not present them as measured human reactions.
- **Words and meaning:** spelling, punctuation, capitalization, inconsistent terms,
  vague labels, placeholder versus label, units, dates/time zones, singular/plural,
  truncation, help text, errors that explain how to recover, and truthful success copy.
- **Visual craft:** alignment, spacing, padding, baseline, type hierarchy, line height,
  wrapping, contrast, icon meaning/consistency, borders, clipping, overlaps, empty gaps,
  image crop, layout shifts, and consistency across states. Describe visible defects;
  exact pixel or contrast claims require measurement.
- **Controls and input:** click/target area, hover/pressed/focus/disabled appearance,
  cursor, field defaults, validation timing, keyboard order, Enter/Escape, focus return,
  selection, paste, dialog dismissal, and accidental or duplicate submission.
- **Feedback and continuity:** loading cues, perceived waits, progress, save status,
  notifications, stale content, error placement, retry, undo where offered, preserved
  input, refresh/re-entry, and whether the user can tell the outcome succeeded.
- **Responsive and accessible use:** overflow, fixed/sticky elements, mobile navigation,
  keyboard reachability, visible focus, zoom/reflow, meaning without color or hover,
  readable text, and reduced-motion behavior where the host can exercise it. Claim
  screen-reader or accessibility conformance only with the corresponding evidence.
- **Product-specific experience:** onboarding, search/filter/sort, tables/pagination,
  forms, uploads/downloads, permissions, playback, sound, recording, gestures, and
  completion/reward loops as applicable. A playing indicator does not prove audible
  sound, a recording permission does not prove capture, and a still image does not
  prove animation quality. Disclose unsupported sensory/device capabilities.

## Capture and prioritize

For every distinct observation, retain the route/screen and trigger, what actually
happened, what the user was trying to achieve, the practical consequence, and a
specific suggested improvement. Capture a screenshot for visual findings when safe
and supported; use action/outcome notes or recordings for behavior. Link evidence
to finding IDs. Preserve enough viewport, role, and state context to reproduce it.
If capture is unavailable or unsafe, retain precise observations and name the gap.

Confirm surprising behavior with a bounded retry when safe. Record frequency as
observed (for example, once in two attempts); do not generalize from a single trial.
Label each finding as observed behavior, design judgment, or an unverified hypothesis.
Keep evidence/confidence separate from severity and avoid unsupported root causes.

| Priority | User impact |
| --- | --- |
| P1 — blocks or seriously harms a goal | A core task cannot finish, input is lost, or the interface leads to a materially wrong outcome. State the affected conditions. |
| P2 — meaningful friction | The task works but requires avoidable effort, guesswork, recovery, or has a significant readability/access barrier. |
| P3 — small friction or polish | A minor wording, visual, consistency, or interaction detail with a concrete local effect. Retain it even when it is tiny. |

Order by impact and reach, then recurrence and confidence. Do not inflate a cosmetic
finding to secure attention. Where impact is unknown, say what was observed and
what remains uncertain. Recommendations describe a better user outcome; implementation
mechanisms belong only where evidence makes them useful.

## Finish, report, and resume

Read [the report contract and example](references/reporting.md) before writing.
Lead with the user's experience and highest-impact opportunities, then include the
complete prioritized findings. Use plain language, short concrete entries, and
progressive detail. Concision comes from precise wording and deduplication, never
from silently dropping minor observations or hiding the full report behind a summary.

Finish when all discovered in-scope areas have been visited and relevant journeys,
states, and the detail sweep are either exercised or explicitly listed as untested
with a reason. For an explicit timebox or interrupted run, checkpoint coverage,
remaining areas, finding IDs, and safe fixture state; label the report partial.
Do not declare the entire product exhaustively tested because the reachable sample
worked. On resume, verify the target/build, preserve earlier evidence and findings,
and finish remaining coverage; distinguish a changed build's observations.

State what worked well when it helps preserve a useful behavior, without praise
padding. If no actionable issues were observed, say so for the actual coverage and
retain limitations. If a report file was requested or is needed for a large result,
use the project's existing location/format and link the complete report in the reply.

For skill evaluation, use [realistic scenarios](references/evaluation-scenarios.md).
They are acceptance cases, not claims that a model or product passed them.
