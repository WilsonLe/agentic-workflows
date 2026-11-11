# Editonny backend

Use this handoff when the user selects Editonny or supplies an existing Editonny
project to resume. Start new jobs with a short local BT.709 SDR video at a
constant frame rate, one audio track, and a brief for speech cleanup, captions,
or both. For other profiles, explain the limitation and offer a supported route
before changing backend, format, or scope. If the user also selects OpenRouter,
use the [hosted transcription handoff](#hosted-transcription-handoff) before
running intake or speech tooling.

1. Resolve the installed Editonny skill through Codex.
   Load its instructions in the same session and follow its preflight, including
   the upstream update check. Use the physical package root and `doctor --json` to
   identify the version, engine and code fingerprint. Check the actual FFmpeg
   route and, as needed, the pinned renderer/browser and working local OCR.
   Check the cached speech model only when using local transcription. A
   successful doctor is only one check. If the skill or a prerequisite is missing,
   report the specific gap and offer upstream setup or the regular Video Editing
   route. Setup and updates require their own authority.
2. Carry the selected local paths, brief, requested scope, caption language,
   protected pauses or intervals, destination and sample reviewer into Editonny.
   For a new job, write the requested overrides as JSON in temporary session
   storage using the upstream field names. Run the canonical CLI with
   `inspect`, the selected paths, and `--requested REQUEST_JSON --json`. Save
   the returned inspection and proposal for workspace creation. Check
   `proposalBlocked` even when the process exits successfully. If
   `proposal.config` differs from the brief, resolve the difference and inspect
   again before presenting any settings for approval. Base the upstream
   settings card on that same proposal and use its settings and source hashes
   for confirmation. Wait for the user's subsequent reply before full
   transcription, workspace creation or rendering. For a resumed job, use
   `workspace status` and the upstream revision and confirmation commands for
   changes to accepted settings.
3. Let the upstream workflow own the native `project.json`, cut decision list,
   review evidence and render. Use its representative sample and the selected
   reviewer, then deliver through `workspace export` only after the current
   candidate clears its checks. Return the project revision, verified MP4,
   requested original-language SRT/VTT and the delivery manifest under the
   revision's `edit/deliveries/`. Keep local paths and evidence in the task.
   Surface stale review, missing checks, and failed export as incomplete.

## Hosted transcription handoff

Use this route when the user explicitly selects OpenRouter for an Editonny edit.
The first supported route is a full speech cleanup with one selected source and
a native rendered and checked cut. Use the regular Video Editing workflow for
a captions-only request when the native project has no compatible checked cut.
The bridge is verified against Editonny 1.1.0 at the revision below. Resolve the
trusted upstream installation and run the bridge with its existing engine
Python. Stop if the version or contract is unsupported. Check the local
rendering and OCR prerequisites, and skip speech-model setup and cached-model
checks for this route.

```sh
"/absolute/editonny/engine/.venv/bin/python" <skill-root>/scripts/editonny_transcript.py \
  inspect --engine-root /absolute/editonny/engine --source /absolute/selected.mp4 \
  --requested /absolute/private-session/request.json > /absolute/private-session/inspection.json
```

This uses upstream metadata inspection with language inference disabled. Resolve
any blocked proposal or missing facts. If an override needs a source ID, inspect
the source for that ID, then pass the complete overrides and inspect again. Show
the actual settings and get the subsequent reply as in step 2. Include the
chosen transcription provider, authorized audio, and its cost in that decision.
Keep the selected source SHA-256 from that inspection with the approval. Use
upstream workspace creation with the saved inspection and actual approval.

Run the [OpenRouter audio-only route](../../speech-to-text/references/openrouter.md)
on the confirmed source. Pass the selected entry's `sha256` value from the
confirmed revision's `edit/source_manifest.json` as `--approved-source-sha256`.
It must match the hash recorded before approval. Then import the normalized
transcript and map its words onto the measured cut clock after native cut
verification.

```sh
"/absolute/editonny/engine/.venv/bin/python" <skill-root>/scripts/editonny_transcript.py \
  import --engine-root /absolute/editonny/engine --project /absolute/revision/project \
  --transcript /absolute/private-transcript/transcript.json
# Build the cut and run Editonny's native verify_cut.py after importing the transcript.
"/absolute/editonny/engine/.venv/bin/python" <skill-root>/scripts/editonny_transcript.py \
  map-cut --engine-root /absolute/editonny/engine --project /absolute/revision/project
# If captions are enabled, use the mapped cut transcript to build their cues.
"/absolute/editonny/engine/.venv/bin/python" /absolute/editonny/engine/helpers/captions.py \
  --edit-dir /absolute/revision/edit --from cut
```

Skip upstream speech-model commands, including `transcribe.py` and
`audit_cut.py`. The local waveform checks and alignment can still run. Use
`--from cut` to read the mapped `transcripts/cut.json` even when the edit decision
list uses a source alias. Inspect the imported words and cut boundaries, preserve
raw speech evidence and record any verified spelling corrections separately.
Resume at Editonny's normal sample, review, OCR and export gates. Existing
burned-in source marks can cause a layout finding. Resolve it within the
confirmed source and settings contract before publishing.

Use the upstream timeline as the only editable clock for that job. Other skills
can consume an exported video and its sidecars as assets in a later edit. The
handoff does not require installing Editonny for ordinary Video Editing or
shipping its runtime, website, scenes or media in Agentic Workflows.

The handoff and the spoken footage guidance were informed by Editonny 1.1.0 at
[`49714f2`](https://github.com/soumatheusgomes/editonny/tree/49714f2fba6eafb76b903376e1fe9f50b685506a).
Use the resolved installation's instructions for its
[setup](https://github.com/soumatheusgomes/editonny/blob/49714f2fba6eafb76b903376e1fe9f50b685506a/skills/editonny/references/setup.md)
and [managed editing workflow](https://github.com/soumatheusgomes/editonny/blob/49714f2fba6eafb76b903376e1fe9f50b685506a/skills/editonny/engine/WORKFLOW.md).
