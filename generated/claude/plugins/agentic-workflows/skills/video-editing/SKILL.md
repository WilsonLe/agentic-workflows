---
name: video-editing
description: Plan and edit videos from footage, images, speech and sound with storyboards, searchable asset indexes, reference analysis, keyframes, blending and transitions. Coordinates Motion Design, Typography, Audio Editing, STT, TTS and Music Composition around one edit timeline.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Local media tools** — Provide FFmpeg and ffprobe plus an existing editor or compositor; Python 3.10 or newer runs the asset index helper. Motion Design's rendering runtime is needed only for animated scenes.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

<!-- claude-code-notes:start -->
## Claude Code

This skill's references write `<skill-root>` for `${CLAUDE_SKILL_DIR}`. Use those absolute paths in commands you run or give to the user; never show the placeholders.

Run each shell command on its own with absolute paths, without `cd`, chaining, or shell variables; run helpers with `python3` (or `uv run` where shown) and write input files with the file-writing tool. If a command is denied, run it again alone in that form before concluding that the shell is unavailable.

<!-- claude-code-notes:end -->

# Video Editing

Turn the brief and available assets into an editable cut and an inspected final
video. Reuse the user's editor/project when available; otherwise choose an
existing local backend such as FFmpeg and Motion Design's renderer. This skill
owns editorial decisions and timing, not a new rendering engine.

## Plan and index

Establish purpose, audience, duration, aspect ratio, frame rate, delivery format,
language, captions and sound direction. Infer routine choices from the brief.
Carry later feedback into the existing project checkpoint: current constraints,
accepted choices, superseded directions and the next requested stage. A broad mood
such as energetic does not prescribe retiming, rapid cuts or constant camera motion.
For a targeted revision, identify what changes and preserve the accepted remainder.
Inspect assets before proposing shots. Preserve originals and keep generated
media, fonts, models and evidence in the task's output folder, outside Git by default.

Read [assets and timing](references/assets-and-timing.md) for indexing and the
project contract. Build a technical index, then inspect contact sheets, selected
source frames and audio to add searchable content labels and useful source ranges.
Use [Speech-to-Text](../speech-to-text/SKILL.md) for timed dialogue indexing and
captions. Technical metadata alone cannot identify what a shot depicts.

For a supplied reference, read [learn from reference](references/learn-from-reference.md).
Translate observed pacing, framing, typography and sound into original decisions.
Unavailable references remain explicit gaps; do not pretend to have watched them.

Use the [storyboard](templates/storyboard.md) to connect each beat to indexed assets,
source ranges, output frames, text, motion and audio cues. A concise beat list is
enough for a small edit. Resolve missing or unsuitable assets before dependent work;
label placeholders so a draft cannot be mistaken for a finished cut.

## Build the cut

Keep one project timeline. Read [compositing and keyframes](references/compositing-and-keyframes.md)
for retiming, transition overlap, masks, blend modes and deterministic animation.
Cut for meaning and continuity first; add effects where they serve the piece.
Check repeated activities across the whole cut, subject position across neighboring
shots, camera movement and requested day/night coverage. Musical accents guide
cuts within the accepted pacing; they do not require cutting on every beat.

- [Motion Design](../motion-design/SKILL.md) returns editable animated shots and
  rendered intermediates against the edit's timing. It retains scene-local animation.
- [Typography](../typography/SKILL.md) selects and indexes static fonts, lays out
  titles/captions and checks rendered text at the actual delivery size.
- [Text-to-Speech](../text-to-speech/SKILL.md) returns measured narration takes.
  Fit the cut to the actual speech or revise the script; never assume reading time.
- [Music Composition](../music-composition/SKILL.md) consumes the shared duration
  and cues and returns an original score with editable source.
- [Audio Editing](../audio-editing/SKILL.md) restores dialogue and returns timed
  stems and a final mix with measured evidence and listening status.

These are capability handoffs, not permission to spawn agents. Video Editing owns
final assembly, mix placement and muxing. A timing revision returns to affected
skills and invalidates their old cue/render evidence. For a standalone animated
piece Motion Design may own the timeline instead; select the owner once.

## Review and deliver

Inspect a rough cut for story, pacing, continuity and text before expensive exports.
Review transition boundaries, keyframe extremes and speech sync. Export a new
version, then run the existing [video verifier](../motion-design/scripts/verify_video.py)
with the brief's dimensions, rational FPS and integer frame count. Inspect frames
extracted from that encoded file and play/listen to it when available. Check opening,
ending, captions, sound, phone readability and any loop seam. Fix timestamped issues.

Deliver the final video, native edit/project or reproducible edit recipe, indexed
assets and fonts, storyboard/timeline, speech sidecars, stems and provenance.
Report technical, visual and listening evidence separately, including unavailable
checks. Preserve prior masters on failures; resume from the last verified asset or
render stage rather than repeating generation. Local editing authority does not
authorize paid services, uploading private media or publishing.

Use [feedback evaluations](examples/feedback-evaluations.md) when rehearsing changes
to this workflow. Instruction/package checks establish coverage and reachability;
an actual edit and listening review need their own candidate evidence.
