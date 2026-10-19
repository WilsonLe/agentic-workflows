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

## Study a supplied music reference

Treat the soundtrack as the source, even when the video is scenery rather than a
composition lesson. Resolve which passage or quality matters from the brief; for
a long video without a specified passage, begin with a short opening excerpt and
state that scope. Expand only when a contrast, transition or ending needs study.
Use YouTube Content Inspection for page metadata and YouTube Media Operations for
authorized retrieval when those capabilities are available. A user-selected browser
download route may supply the asset instead; verify the actual file and provenance.

Keep a compact study note in the existing musical brief's notes, outside the strict
starter JSON. Include URL/local source, time ranges, evidence method and these
observations where supported:

- Pulse and meter: estimate tempo with uncertainty; distinguish a flowing subdivision
  from the beat and check half/double-tempo ambiguity or expressive timing.
- Musical roles: separate the main melody, bass, inner harmony and accompaniment.
  Describe register, density, repeated patterns and rests rather than guessing notes.
- Harmony and form: mark chord-change rate, tension/release, phrase boundaries,
  returns and the ending. Name a key or chords only when the evidence supports them.
- Performance and sound: note melodic emphasis, articulation, dynamic shape, timing,
  pedal/decay and room character, separating heard effects from inferred production.

Finish with a few observation-to-choice pairs, such as an observed sparse melody
leading to longer rests in the new piece. Transfer broad techniques into an original
motif, contour and arrangement; do not reproduce the reference's distinctive melody.
Record what to preserve and what to change before rendering.

Keep page inspection, signal measurements, model-assisted music analysis and direct
listening separate. A playable page or downloaded file does not prove audition. If the
host cannot receive audio, try an available waveform-consuming music model or piano
transcriber within the task's authority before stopping at loudness, spectra or tempo
estimates. For a transcriber, inspect note/onset/duration events as a provisional score:
trace melodic contour and phrase answers, bass movement, chord-change points, and how
accompaniment fills the spaces around longer melody notes. Note counts alone are not
a musical study. Do not assign hands, key, chords or pedal solely from pitch thresholds
or a model caption.

Check that the selected route actually receives the decoded audio. Test silence and a
known audible example; a silence-only pass can hide a route that treats every input
as silent. For transcription, compare recovered pitches and onsets with a known score.
For audio-language analysis, use neutral filenames/prompts without the expected
instrument or source title. Preserve input hashes, source ranges, model/version,
settings, prompts or transcription, and failures in the task output folder. Compare
separated excerpts and cross-check claims against note events or another grounded
method. Reject routes that confuse silence with audible input or fail to recover known
content, and exclude contradictory captions. Record transcription errors and limit
conclusions to relationships the method can support; agreeing models alone do not
establish correctness.

Automated notes, tempo and chord estimates remain provisional; harmonics, overlapping
notes and reverb can mislead them. Distinguish score-based interpretation from verified
listening, especially for timbre, touch, balance and pedal. If no usable audio route
remains, record the concrete failure, retain the source and continue independent work.
Ask for an accessible excerpt only when reference-specific work still depends on it.
Reuse the existing study note when access becomes available.

Supplied reference case: [JAPAN ODYSSEY's Sunset Drive in Kamakura](https://www.youtube.com/watch?v=mw06wpMDFPo).
For this scenic driving soundtrack, local yt-dlp retrieved only 00:00–05:00 in
public mode; the MP3 decoded successfully and measured 300.0135 seconds. The media
stayed outside the skill package. No browser-cookie export was needed.

A local [piano transcriber](https://github.com/qiuqiangkong/piano_transcription_inference)
(`piano_transcription_inference` 0.0.6, Note_pedal CRNN, CPU, default thresholds;
[released checkpoint](https://zenodo.org/records/4034264)) converted three separated
excerpts into provisional MIDI/note events: 00:00–00:30, 01:30–02:00 and 04:00–04:30.
The source MP3's SHA-256 was
`21bc538c5d6849b06037e840300ad43dc09eaf731e23b721f8df043fd50ca7f3`;
checkpoint SHA-256 was
`c3fa9730725bf4a762f1c14bc80cd5986eacda01b026f5a4a2525cd607876141`.
Media, environment, raw note events, controls and the study report stayed in the task
output folder. This is score-based interpretation of actual audio, not direct audition
or a verified transcription.

| Source passage | Provisional musical reading | Choice for an original piano piece |
| --- | --- | --- |
| 00:08–00:16 | An upper G–A–B rise returns about four seconds later, while the lower part moves from C-based notes toward A-based notes. The repeated idea survives a changed harmonic setting. | Repeat a small rhythmic/contour idea over a new bass or voicing, then change its answer; do not generate a new melody for every chord. |
| 00:13–00:20 | The low attacks move A–A♭–G while upper/inner notes connect across them. The chromatic bass is more informative here than a guessed four-chord label. | Write a purposeful bass destination and connect the inner voices before adding extensions; use a chromatic passing or approach bass deliberately. |
| 01:43–01:46 | Lower F–C–F–C attacks continue beneath longer upper A/F material. Melody and accompaniment operate at different rhythmic speeds. | Keep a quiet supporting figure moving while the melody holds or breathes; align selected phrase accents rather than doubling every attack. |
| 04:05–04:29 | An upper stepwise rise and fall returns several times; one answer reaches higher before returning. Inner chord tones support the upper line. | Establish a recognizable cell, vary one answer's register or destination, and reserve the larger lift for a phrase peak. |

These readings come from inspecting pitch/onset relationships, not just event counts
or spectra. Note names and role assignments remain provisional. The transcriber
produced no notes on silence and recovered all seven expected pitch/onset pairs in
a known piano control, alongside two octave false positives and imperfect note lengths.
The study therefore does not promote every event, velocity or pedal estimate to fact. Audio-language alternatives gave conflicting instruments or
failed input controls and were excluded. Do not infer touch, instrument quality,
pedal use, an exact chord sequence, a single global key, or the full video's form
from these excerpts. The earlier first-20-second pulse estimates near 59.5/117.2 BPM
also remain unresolved; the note patterns are useful without choosing either grid.
The following exercise is an independent original teaching sketch, not a source
transcription or an asserted match to its sound.

## Write and perform a piano passage

Start with the phrase and its emotional destination. For a gentle background brief,
try a moderate pulse, an uncluttered melody and a quiet accompaniment, then adjust
from the actual reference study. These are composition choices, not universal piano
rules or measurements of the supplied video.

1. Write a singable one- or two-bar right-hand idea with a clear rhythm, a small
   range and a rest. Repeat enough of it to be recognizable, including across a
   changed bass or chord, then vary one feature: the ending, rhythm, register or
   harmonic setting. Give the phrase a high point
   and a release instead of filling every beat with new notes.
2. Choose a harmonic route and bass line that support that destination. Decide when
   chords change before adding decorative notes. Hold common tones and move inner
   voices by small intervals when a connected sound is wanted; keep low voicings
   open and put close extensions higher. These are useful starting techniques from
   [Open Music Theory's voicing guidance](https://viva.pressbooks.pub/openmusictheory/chapter/jazz-voicings/),
   rather than a required progression or style.
3. Give the left hand one supporting role: held bass plus light chords, a broken
   chord, or a repeated figure. Let it move beneath a longer melody note or rest;
   the voices need not attack together. Keep its attacks and register clear of the melody.
   Write the actual notes and durations, check hand spans, leaps and overlapping
   held notes at tempo, and redistribute or roll wide chords deliberately. A chord
   symbol alone does not specify a playable arrangement.
4. Shape a short form, for example A–A′–B–A with one purposeful lift and a quieter
   return. Vary density or register at phrase boundaries, leave breathing space,
   and compose the cadence. A repeated chord loop alone is not development.
5. Perform the voices differently: bring the melody forward, support it with a
   softer accompaniment and shape dynamics across phrases. Use small, intentional
   timing changes instead of random jitter. For video, preserve the timing owner's
   cue positions while shaping expression between them.

An editable four-bar exercise: C major, 4/4, quarter note = 72, one chord per bar.
These are suggested starting values. Octave numbers use C4 for middle C. Each left
hand note below lasts one beat; right hand durations are in quarter-note beats.

| Bar / chord | Left hand, beats 1–4 | Right hand, note(duration) |
| --- | --- | --- |
| 1 / C | C3 G3 E3 G3 | E4(1), G4(1), A4(1), G4(1) |
| 2 / Am | A2 E3 C3 E3 | E4(2), C4(1), rest(1) |
| 3 / F | F2 C3 A2 C3 | F4(1), A4(1), G4(1), E4(1) |
| 4 / G | G2 D3 B2 D3 | D4(2), G4(1), rest(1) |

The A over C and E over F are intentional color tones. To develop eight bars,
repeat the idea with a changed answer and resolve the final phrase to C; score the
new notes and durations explicitly. Audition melody alone, accompaniment alone and
both together. This notation belongs in editable score/MIDI/program notes, not in
unsupported starter JSON fields.

Choose an available piano instrument or renderer suited to the desired sound; record
the patch/library, license and performance settings when external assets are used.
Check note attacks, changing tone with dynamics, decay, releases and pedal response.
The sustain pedal lets strings continue vibrating after key release
([Yamaha's piano mechanism explanation](https://hub.yamaha.com/pianos/p-acoustic/how-does-a-piano-work/));
listen across harmony changes and clear the pedal where accumulated notes blur the
intended harmony. Reverb adds room character; it cannot repair voicing or phrasing.

The bundled sine/pluck starter does not implement an acoustic piano, independent
melody events, expressive note velocities or sustain-pedal control. Setting
`percussion: false` removes drums but does not supply those capabilities. Use an
existing suitable renderer or editable custom program within the task's authority;
label a synthetic approximation honestly when that is the available option.

Before expanding the arrangement, audition a short phrase at comparable playback
level to the reference. Check melodic identity, accompaniment balance, playable
movement, phrase breathing, attacks, resonance and ending. Revise the specific
musical cause, then inspect and listen to the actual final export. If audition is
unavailable, deliver the editable sketch and technical evidence with that limitation;
do not describe the result as a verified match to the reference.

## Revise sound and vocals

Keep qualitative feedback in the existing editable musical brief/program or its
notes, outside the strict starter JSON fields below. Translate timbre feedback into
an audible revision hypothesis: fuller harmony/bass or sustained layers for a thin
sound; softer attacks, less noisy percussion or a warmer lead for unwanted rasp.
Preserve tempo, duration and accepted material unless the correction changes them.
Compare short level-matched versions through the existing Audio Editing workflow;
technical export checks cannot confirm that the requested sound was achieved.

For requested vocals, settle the lyric direction and density before a new take when
the user asks for lyrics first. Offer short alternatives in text; track the selected
version, later corrections, repeats, fillers and instrumental space. Sparse vocals
mean fewer phrases and music carrying the arrangement, not merely shorter sentences
packed into every bar. Abstract or surreal wording should still evoke the brief's
feeling; a sound-alike phrase or technical term needs a meaningful reason to stay.
For a supplied song reference, apply the study method above to broad pacing, texture
and vocal spacing; write original words/music.
Later feedback can supersede a selected lyric without undoing accepted vocal density.

Singing requires a capability that actually generates sung music; access to a TTS
service alone proves only a possible narration path. When a service is selected,
verify its current official input/output, duration, access and cost contracts before
using it within the user's existing scope and budget. Missing singing access blocks
that take, not lyric work or local instrumental revisions. Keep the accepted text,
prompt/settings, model, returned take, measured duration, cost and listening status
with the existing music assets. A generated take becomes new indexed audio; it does
not replace the cut's soundtrack until selected and handed to the timing owner.
No past project's credential or spending approval authorizes a new project's calls.

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

`--timeline` accepts the video timing owner's JSON object with required `duration` and
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
Video Editing retains a footage cut timeline; Motion Design retains a standalone
scene timeline. The selected owner muxes the final video; timing edits
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
