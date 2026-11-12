# OpenRouter transcription

Use this option only when the user selects OpenRouter. The helper sends one
selected clip's extracted mono WAV to the hosted Whisper Large V3 Turbo model.
It returns words on the original source clock. Keep the editing timeline,
caption creation, sample review, rendering and export with the local owner.

Before asking for approval, compute the selected file's SHA-256 from its bytes
and record it with the source path in the private task record. Confirm that
file, the audio that will leave the machine, the model, and the expected cost.
Use the saved hash when making the request. If the source changes, inspect the
new bytes and get approval again. Extraction uses a private temporary snapshot
that must match the approved hash. Local scratch space needs room for that
snapshot. Check the
[OpenRouter transcription contract](https://openrouter.ai/docs/guides/overview/multimodal/stt)
and [current model rates](https://openrouter.ai/openai/whisper-large-v3-turbo).
The helper requests word timestamps and asks OpenRouter to exclude providers
that collect data. OpenRouter can route within its service. Review its
[provider routing and data policies](https://openrouter.ai/docs/guides/routing/provider-selection)
alongside the decision to upload audio.

This route takes one local clip up to 60 seconds, with one audio stream and a
zero-based source clock. Use a separately approved, explicitly prepared clip
for a longer or unsupported source and retain the source-time mapping. The
helper requires FFmpeg, ffprobe, Python, and POSIX owner-only artifact modes.
Use [Infisical Account Operations](../../infisical-account-operations/SKILL.md) to
fetch the named OpenRouter key from the explicitly selected instance/project/
environment and `/providers/openrouter` folder. Map its stored key name (including
an existing `OpenRouter` key) to `OPENROUTER_API_KEY` inside the approved runtime
process environment; capture secret-bearing output before tool responses. This
selects credentials only and does not authorize an audio upload or charge. It does not require a Git checkout, project
credential directory, or worktree key-copy step. Never put its value in shell
commands, chat, logs, or Git; do not extract a Codex connector credential. Missing
runtime configuration blocks only the hosted request. Media subprocesses receive
an environment with this key removed, and offline recovery needs no key.

```sh
python3 <plugin-root>/scripts/openrouter_transcribe.py \
  --source /absolute/approved-clip.mp4 \
  --approved-source-sha256 "$approved_source_sha256" \
  --output-dir /absolute/private-task/transcript --language en
```

Set `approved_source_sha256` to the saved 64 lowercase hexadecimal characters,
without the `sha256:` prefix. Use `auto` only when language detection is intended.
Give each request a fresh private output directory outside Git. Keep the raw
provider response, request evidence, and `transcript.json` local. The normalized
record includes the source identity and clock, uploaded audio hash, and provider
provenance. Missing or malformed word timing blocks caption handoff. The helper
makes one submission without resending on timeout or normalization failure.
Once a successful response is saved, the receipt records its raw SHA-256.
Inspect the retained response before any further request.

If the provider times the last word beyond the audio, verify the word's end
against the local waveform. Run the same command with the existing output
directory and `--recover-final-word-end SECONDS` in place of
`--approved-source-sha256`. Recovery checks the original source, extracted audio,
language, and raw response hash against the saved receipt. It records the
reviewed endpoint and creates `transcript.json` exclusively from the retained
response, without another upload or replacement of an existing transcript.
Other malformed or missing timings remain blocked.
