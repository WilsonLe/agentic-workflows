# OpenRouter transcription

Use this option only when the user selects OpenRouter. The helper sends one
selected clip's extracted mono WAV to the hosted Whisper Large V3 Turbo model.
It returns words on the original source clock. Keep the editing timeline,
caption creation, sample review, rendering and export with the local owner.

Before sending audio, confirm the selected file, the audio that will leave the
machine, the model, and the expected cost. Check the
[OpenRouter transcription contract](https://openrouter.ai/docs/guides/overview/multimodal/stt)
and [current model rates](https://openrouter.ai/openai/whisper-large-v3-turbo).
The helper requests word timestamps and disallows provider data collection.
Treat provider retention policy separately from the fact that audio is uploaded.

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
  --output-dir /absolute/private-task/transcript --language en
```

Use `auto` only when language detection is intended. Give each request a fresh
private output directory outside the source checkout. Keep the raw provider
response, request evidence, and `transcript.json` local. The normalized record
includes the source identity and clock, uploaded audio hash, and provider
provenance. Missing or malformed word timing blocks caption handoff. A recorded
submission prevents an automatic resend even if the provider times out or
normalization fails. Inspect the retained response before any further request.

If the provider times the last word beyond the audio, verify the word's end
against the local waveform. Rerun the same command with
`--recover-final-word-end SECONDS` and the existing output directory. The
helper checks the original source and extracted audio against the saved
request, records the reviewed endpoint, and normalizes the retained response
without another upload. Other malformed or missing timings remain blocked.
