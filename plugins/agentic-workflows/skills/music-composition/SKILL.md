---
name: music-composition
description: Compose original instrumental music, procedural sound effects, and scene-synchronized audio by writing editable synthesis code. Use for a soundtrack, sonic logo, musical loop, or timed cues; pair with Motion Design for video and keep one shared timeline. Supports local deterministic WAV synthesis without a music-generation service.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Python runtime** — Install Python 3.10 or newer for local standard-library synthesis and WAV inspection.
- **Optional: FFmpeg and ffprobe** — Provide FFmpeg and ffprobe when encoding compressed audio or mixing with video; Motion Design owns final video verification.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Music Composition

Turn a sound brief into original editable music and an inspected audio file.
Code can synthesize oscillators, noise, envelopes, percussion, harmony, and effects;
it does not require a music service. The bundled synthesizer is a starting palette,
not a substitute for composing and listening to this particular piece.

## Compose from the brief

Establish purpose, mood, duration, pace, instrumentation, ending or loop, and any
voiceover space. Infer routine choices. Read [composition and delivery](references/composition-and-delivery.md)
for arrangement, sound design, the input contract, and verification limits.

1. Write the musical idea: motif, harmonic movement, rhythmic accents, sections,
   and silence. Use original material; record provenance for supplied samples.
2. Choose an existing audio/timeline owner before adding one. For a video, read
   `motion-design` and consume its timeline; return WAV and cue evidence. Motion
   Design owns visual timing, final muxing, and checks of the encoded video.
   For a standalone track, this skill owns timing and the requested audio output.
3. Start from the [editable brief](examples/brief.json) and the synthesizer below,
   or write a different local synthesis program when the palette does not suit
   the brief. Revise notes, rhythm, timbre, arrangement, and envelopes deliberately.
   Preserve seeds, dependencies, and source so edits can be reproduced.
4. Listen to the actual delivered candidate with available playback tools. Check
   harshness, clipping, rhythm, intelligibility around speech, and cue placement.
   For loops, listen across the seam. Revise and listen again. If listening is
   unavailable, say so; waveform statistics do not establish musical quality.
5. Deliver the audio, editable source/brief, shared timeline when used, provenance,
   and concise checks. Keep generated media in the task's output folder.

## Local synthesis starter

```sh
python3 <skill-dir>/scripts/synthesize_score.py \
  --brief <skill-dir>/examples/brief.json --output /absolute/output/score.wav
```

For scene synchronization, add `--timeline /absolute/path/timeline.json`.
The timeline supplies duration, named cue times, and tempo if declared; never copy
cue constants into another independent clock. Use `--overwrite` only to replace
an intended task-owned output. Invalid inputs fail before any output is written.
The helper emits a decoded PCM report, including duration, frame count, peak,
RMS, and SHA-256; inspect those against the brief. Optional FFmpeg encoding or
mixing must be followed by decoding and listening to the final encoded candidate.

This workflow authorizes local composition within the task, not paid generation
or publishing. State exactly how the audio was made and whether any samples or
services were used. Do not promise legal exclusivity from an originality claim.
