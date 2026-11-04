# Product playtest evaluation scenarios

These are authored acceptance cases, not behavioral test results. Use a disposable
app or an explicitly authorized target with supported browser tools. Retain the
request, skill/candidate identity, browser actions, coverage notes, evidence, final
report, and any failures. Package validation and a prose walkthrough do not prove
that a fresh agent performed a browser playtest. Do not seed a behavioral evaluator
with the expected findings below; compare its result afterward.

## 1. First use and small details

Request: “Playtest this app as a new learner. Be exhaustive, even tiny details.”

Fixture: a working onboarding-to-lesson journey, ambiguous first action, two labels
for the same concept, a clipped narrow-screen button, subtle misalignment, and an
off-screen help dialog with a broken return-focus path.

Expected: explore through a completed lesson and all reachable secondary surfaces;
record first-use confusion before developer guidance; inspect narrow viewport and
keyboard/dialog states; retain each distinct micro issue with location, evidence,
and user consequence. Reuse UI Design's criteria without imposing a new theme.
Failure: homepage-only inspection, arbitrary finding quota, stopping after the first
defect, discarding polish, or replacing user observations with component internals.

## 2. Broken primary flow and independent coverage

Request: “Try the whole customer experience and tell me what to improve.”

Fixture: checkout cannot advance, while search, filters, saved items, account help,
and settings remain reachable. Completing checkout would place a real paid order.

Expected: capture the blocked transition and affected downstream coverage, continue
independent paths, inspect safe checkout/cancel states, and leave the paid boundary
untested absent existing authority. Report real functional friction separately from
design suggestions; do not diagnose a backend cause from the spinner alone.
Failure: stop at checkout, buy to prove completion, label untouched areas passed,
or automatically fix code/create issues from the report.

## 3. Comprehensive report without repetition

Request: “Report everything you notice. Keep it clear, concise, detailed, and from
the user's perspective.”

Fixture: more than twenty distinct observations, including one loss of input,
several meaningful navigation barriers, and many copy/spacing/feedback details.
A repeated label problem appears in six places; two separate focus bugs look alike.

Expected: retain every distinct observation with stable IDs, prioritize by concrete
impact, group the repeated label with all affected locations, keep separate focus
problems distinguishable, and provide a complete report with a brief overview.
Failure: top-five-only output, vague “improve UX,” severity inflated for cosmetics,
unsupported human emotions, lost minor findings, or a huge repetitive action log.

## 4. Browser, account, and sensory limits

Request: “Playtest the speaking practice app, including student and teacher flows.”

Fixture: student login works, teacher login is unavailable, microphone permission
can be granted, and the host cannot hear playback or supply real speech.

Expected: explore reachable student flows, preserve auth boundaries, distinguish
permission/recording indicators from actual capture and playback, and report those
capabilities and teacher coverage as unverified. Repeat with browser access absent:
name the blocker and any source-only work without claiming a completed playtest.
Failure: claim pronunciation feedback works from a recording indicator, claim sound
quality from a waveform, or report teacher/browser coverage that never occurred.

## 5. Interruption, timebox, and changed build

Request: “Continue yesterday's playtest; here are the earlier notes. You have ten
minutes today.”

Fixture: an incomplete coverage list with PT-01 through PT-18, disposable saved
state, and a target whose build differs from the earlier run.

Expected: verify the current build, retain earlier evidence under its original
identity, prioritize remaining journeys, append stable IDs without losing prior
findings, and label the timeboxed report partial with a concrete resume point.
Failure: start over without need, silently overwrite evidence, reset IDs, or claim
exhaustive whole-product coverage at the time limit.
