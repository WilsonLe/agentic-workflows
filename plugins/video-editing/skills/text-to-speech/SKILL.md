---
name: text-to-speech
description: Generate narration and spoken audio assets from scripts with voice/model provenance, measured duration and pronunciation review. Use for TTS or voiceover takes, including edit-timed narration; transcription belongs to Speech-to-Text.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Speech synthesis capability** — Use an available host speech tool or local TTS runtime and licensed voice model; cloud synthesis requires scoped authority and access. Provide an audio decoder for output checks.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Text-to-Speech

Turn the user's script into editable narration takes and inspected audio. Establish
language, pronunciation, tone, pace, intended voice and output use. Reuse an available
host tool or local speech runtime. A local option is
[Piper](https://github.com/OHF-Voice/piper1-gpl); read the current
[CLI documentation](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md)
and installed help. Pin the runtime and selected voice model/configuration; keep
voice files and their license/model card in the task's local asset library.

For an existing Piper installation and selected downloaded voice:

```sh
python3 -m piper -m /absolute/voices/voice.onnx \
  --input-file /absolute/output/script.txt -f /absolute/output/narration-take-01.wav
```

Choose a voice the runtime actually provides. Inspect sample pronunciation before
generating a long script; validate intended language/accent, names, abbreviations
and numbers. Retain the script and pronunciation substitutions separately. Do not
infer a voice from a reference speaker or clone an identifiable voice without
authorization. Ordinary TTS work does not imply voice cloning.
Check engine and voice-model licenses separately; source availability is not
permission for every use. Cloud synthesis requires current official capability,
voice, cost and secret-safe access checks plus authority for sending the script.

## Takes and timing

Split by editorial phrases where revision and breathing benefit, retaining context
for prosody. Generate to new take files, preserve accepted takes, and measure the
decoded output duration/sample rate/channels. Compare against the script and listen
for missing words, duplicated phrases, odd stresses, clipped phonemes and endings.
STT can assist alignment but cannot replace listening or certify pronunciation.

Keep `narration.json` with `schema_version: 1` and takes containing script path/hash,
text or script range, language, engine/version, model/voice ID and local model hash
when available, settings, audio path/hash, measured duration, pronunciation notes,
license/provenance and listening status. Word alignment is optional; declare the
aligner and uncertainty. Do not estimate cue timestamps from word counts.

For video, return takes to Video Editing's timing owner. If the take exceeds its
slot, revise wording/delivery or change the cut within the brief. Audition modest
time stretching with Audio Editing; do not silently rush or truncate speech to fit.
Generate changed phrases with consistent context/voice, then check their joins.
Accepted script/timing/voice changes invalidate dependent captions, score cues and
final video checks. A failed or empty synthesis never becomes a completed asset.

Deliver the speech files, script/manifest, measured metadata and listening limits.
Index accepted outputs as new assets and pass them to Audio Editing for treatment.
Disclose synthetic narration in delivery metadata and include any required provider
or platform disclosure in the artifact. Missing voice/runtime/access blocks synthesis
only; continue independent edit planning and report the concrete gap.
