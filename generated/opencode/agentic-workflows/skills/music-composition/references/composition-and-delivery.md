# Composition and delivery

## Make a piece, not a tone test

Sketch a short motif that has a destination. Match harmonic movement and density
to the visual or narrative sections. A product film may need a restrained bed,
a stronger reveal, a readable hold, and a deliberate landing; another brief may
need silence or an entirely different instrumentation. Leave spectral and dynamic
room for speech. Do not use a service or import a sample just because it is easy.

The starter offers warm sine-based chords, a plucked motif, bass, kick, clap,
hi-hats, and seeded transition noise. Edit its palette or write new synthesis
functions when another sound is needed. Keep attack/release envelopes and phase
continuity deliberate. Use headroom before mixing; peak normalization alone can
leave an unpleasant or overly loud track. A fade avoids abrupt file boundaries
but does not make a musical loop. Compose a compatible ending and verify the
seam across repeated playback for a requested loop.

## Brief contract

`brief.json` is a UTF-8 JSON object. Unknown fields, duplicate keys, non-finite
numbers, invalid ranges, or unsupported types fail. Defaults are for a quick
starting palette, not user requirements.

| Field | Contract |
| --- | --- |
| `duration` | Seconds, greater than zero and at most 120; default 15. At most 5,760,000 stereo frames. Rounded to the nearest sample. |
| `bpm` | Tempo, 30–240; default 128. |
| `sample_rate` | One of 8000, 16000, 24000, 44100, 48000; default 48000. |
| `seed` | Integer 0–4294967295; default 2301. Reproducible noise on the same Python runtime. |
| `beats_per_chord` | Integer 1–32; default 8. |
| `chords` | 1–16 chords of 1–8 integer MIDI notes, 24–84; default A minor/C/F/G palette. |
| `percussion` | Boolean, default true. |
| `cues` | Object with at most 256 entries mapping nonempty names to finite seconds in [0, duration]; default empty. Cue at the end has only its pre-roll. |

`--timeline` accepts Motion Design's JSON object with required `duration` and
`cues`, and optional `bpm`; other scene fields are retained by the scene owner and
ignored here. These shared values replace brief timing. Cue sounds start up to
0.28 seconds before each marker and place a short tonal accent exactly at it;
negative pre-roll is clipped to the file boundary, preserving the envelope's time.
Only events intersecting the track are synthesized. Output is 16-bit little-endian
stereo PCM WAV, normalized to 0.85 peak with 12 ms entrance and 320 ms exit fades
(short tracks proportionally reduce these). The helper prints a report from the
written WAV. Synthesis and encoding are Python standard library only.

## Handoff and evidence

Return the WAV path and editable brief/program, timeline path and effective cue
seconds, sample rate/frame count, peak/RMS, provenance, and listening status.
Motion Design retains the scene timeline and muxes the final video; timing edits
return to that owner and require re-synthesis and affected render checks. UI Design
handles interactive audio controls when the output becomes a live interface.
YouTube Media Operations retrieves authorized source assets; permission to retrieve
an asset does not establish permission to use it in a soundtrack.

Inspect the decoded file, not just the program's buffers. Check duration rounding,
stereo channels, silence or clipping, fades, and each cue against the authoritative
timeline. A deterministic file hash shows reproducibility, not quality. Technical
checks cannot prove melody, subjective sound, sample clearance, or smooth loop
playback. Clearly report dimensions not observed. Recheck compressed outputs after
conversion, and report external assets and their actual license separately.
