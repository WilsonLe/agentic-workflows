---
name: speech-to-text
description: Transcribe local audio/video into source-linked timed text for asset search, dialogue editing and captions. Use for STT, transcripts or subtitle assets; preserve source timing, language and uncertainty rather than treating recognized text as verified speech.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Speech recognition capability** — Use an available host transcription tool or local STT runtime with a compatible model; cloud uploads require scoped authority and access. Install FFmpeg when preparing analysis copies.

<!-- catalog-prerequisites:end -->

<!-- catalog-capabilities:start -->
## Companion capabilities

When another workflow would help, consult the [suite capability map](../../CAPABILITIES.md) and read the selected skill before using it. Check availability and prerequisites; carry the user's brief, accepted decisions, artifacts, and verification limits into the handoff. Keep one owner for shared state and timing. A capability listing does not authorize publishing, paid calls, messaging, or delegation.

<!-- catalog-capabilities:end -->

# Speech-to-Text

Produce a searchable transcript tied to the exact audio asset. Inspect source
language, channels, sample rate, duration and intended use. Use an available host
transcription capability or existing local runtime first. A local option is
[whisper.cpp](https://github.com/ggml-org/whisper.cpp); consult the installed
`whisper-cli --help` and [CLI source](https://github.com/ggml-org/whisper.cpp/blob/master/examples/cli/cli.cpp)
for supported JSON/subtitle output and model/input requirements. Pin the runtime
and model identity. Models are local task dependencies, not bundled plugin assets.

For a supported local installation, a starting command is:

```sh
whisper-cli -m /absolute/models/model.bin -f /absolute/output/speech.wav \
  --output-json --output-vtt --output-file /absolute/output/transcript
```

Prepare an analysis copy in the runtime's required format; retain the original
asset ID, selected stream, source offset and any resampling/trim map. Select the
source language deliberately and retain original-language text unless translation
is requested. If a cloud provider is selected, verify current official capabilities,
cost, upload authority and secret-safe access before sending source audio.
No missing runtime or inaccessible audio can be replaced with guessed speech.

## Transcript contract

Keep the raw provider/runtime response, plus a normalized UTF-8 transcript record:
`schema_version: 1`, source `asset_id`, source duration/stream, language,
runtime/model/version, timestamp granularity, analysis-to-source mapping and
`segments`. Each segment has finite source `start_seconds`, `end_seconds`, text,
optional speaker and optional word ranges. Sort by start time and require
`0 <= start < end <= source_duration` with rounding tolerance declared.
Allow genuine overlapping speakers rather than silently flattening them. Word
timestamps and diarization are optional capabilities; do not fabricate them from
segment text, assume each segment is a sentence, or name speakers without evidence.
Keep unavailable confidence null; provider confidence values are not interchangeable.

Convert chunk-local times to the original source clock and reconcile overlapping
chunk text before indexing. Do not delete repeated phrases that occur at different
source times. Listen to uncertain names/numbers, music/noise and apparent speech
in silence. Mark uncertainty and human corrections with provenance. Automated
timestamps need spot checks at edits; lexical correctness alone cannot prove sync.

## Captions and handoff

Return transcript paths, asset ID, runtime/model, language, observed gaps and checked
ranges. Video Editing maps source transcript times through trims/speed to output
time, including removed segments; captions use the delivered cut's clock. Render
line breaks, reading holds and safe placement with Typography. Translation is a
separate text layer; do not overwrite the original transcript.

Index the transcript beside the audio asset for search. Review exported SRT/VTT
for valid ordered timings, text escaping, dialogue coverage and rendered sync.
Preserve raw/corrected versions and rerun only changed source chunks. A transcript
for an old asset hash is stale, even when its filename is unchanged. Report
unlistened or unsupported timestamp/diarization dimensions explicitly.
