---
name: audio-editing
description: Edit, restore and mix dialogue, music and effects with noise reduction, EQ, dynamics, automation, spatial processing and loudness checks. Use for advanced audio post-production, stems or a final mix; original score writing belongs to Music Composition and speech generation to TTS.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Audio post-production tools** — Provide an existing DAW or FFmpeg/ffprobe with the selected filters, playback and suitable metering; specialized restoration requires its own installed runtime.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Audio Editing

Deliver an editable treatment and an inspected mix. Reuse the user's DAW/editor,
or an existing local FFmpeg/audio toolchain; keep originals and isolated stems.
Read [restoration and mixing](references/restoration-and-mixing.md) for advanced
processing, automation, verification and failures.

Establish the source problems, intended sound, dialogue language, delivery platform,
duration, channel layout and any specified loudness/true-peak target. Inspect and
listen before choosing processing. In a video, consume the edit owner's timeline
and return stems/mix at its sample rate and offsets. For standalone audio this
skill owns timing. Do not create another video clock or independently move cues.

Use [Speech-to-Text](../speech-to-text/SKILL.md) for searchable dialogue and edit
ranges, [Text-to-Speech](../text-to-speech/SKILL.md) for requested narration, and
[Music Composition](../music-composition/SKILL.md) for original score. Transcripts
help locate edits; they do not prove a clean splice or correct pronunciation.

Work from dialogue to supporting layers, using short level-matched A/B comparisons.
Keep reversible processing settings or a reproducible filter/automation recipe.
Measure and listen to the actual exported candidate, including encoded outputs;
statistics alone do not establish natural speech or a good mix. Check silence,
clipping, edit clicks, phase/mono compatibility, speech intelligibility and seams.

Deliver original-to-output lineage, processed stems, mix, settings/source project,
sample rate/channels/duration, gain/loudness evidence and listening limitations.
The video owner muxes and checks sync in the final encoded video. Preserve failed
renders/logs and prior masters, fix a specific cause and rerender the affected stage.
Missing tools or source channels are explicit limits, not invented audio evidence.
Uploading private audio, paid services and publishing need authority for that effect.
