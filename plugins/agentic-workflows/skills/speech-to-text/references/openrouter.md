# OpenRouter transcription

Use this option only when the user selects OpenRouter. The helper sends one
selected clip's extracted mono WAV to the hosted Whisper Large V3 Turbo model.
It returns words on the original source clock. Keep the editing timeline,
caption creation, sample review, rendering and export with the local owner.

Before asking for approval, compute the selected file's SHA-256 from its bytes
and record it with the source path in the private task record. Confirm that
file, the audio that will leave the machine, the model, and the expected cost.
Use the saved hash when making the request. If the source changes, inspect the
new bytes and get approval again. Check the
[OpenRouter transcription contract](https://openrouter.ai/docs/guides/overview/multimodal/stt)
and [current model rates](https://openrouter.ai/openai/whisper-large-v3-turbo).
The helper requests word timestamps and asks OpenRouter to exclude providers
that collect data. OpenRouter can route within its service. Review its
[provider routing and data policies](https://openrouter.ai/docs/guides/routing/provider-selection)
alongside the decision to upload audio.

This route takes one local clip up to 60 seconds, with one audio stream and a
zero-based source clock. Use a separately approved, explicitly prepared clip
for a longer or unsupported source and retain the source-time mapping. The
helper requires Git, FFmpeg, ffprobe, Python, and POSIX owner-only file modes.
It reads the selected Git
checkout's ignored, untracked `.cli/openrouter/api-key`. Keep the key as a single
line in a file with mode `0600` inside private directories. Use the
[worktree copy command](../../agentic-workflows/references/task-authority-and-secrets.md#carry-the-openrouter-key-into-a-worktree)
when an authorized worktree of that same repository needs the key.

```sh
python3 <plugin-root>/scripts/openrouter_transcribe.py \
  --project-root /absolute/checkout --source /absolute/approved-clip.mp4 \
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
