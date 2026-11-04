# Editonny backend

Use this handoff when the user selects Editonny or supplies an existing Editonny
project to resume. Start new jobs with a short local BT.709 SDR video at a
constant frame rate, one audio track, and a brief for speech cleanup, captions,
or both. For other profiles, explain the limitation and offer a supported route
before changing backend, format, or scope.

1. Resolve the installed Editonny skill through the host on Codex or Claude Code.
   Load its instructions in the same session and follow its preflight, including
   the upstream update check. Use the physical package root and `doctor --json` to
   identify the version, engine and code fingerprint. Check the actual FFmpeg
   route, cached speech model and, as needed, the pinned renderer/browser and
   working local OCR. A successful doctor is only one check. If the skill or a
   prerequisite is missing, report the specific gap and offer upstream setup or
   the regular Video Editing route. Setup and updates require their own authority.
2. Carry the selected local paths, brief, requested scope, caption language,
   protected pauses or intervals, destination and sample reviewer into Editonny.
   For a new job, let its canonical CLI `inspect --json` produce the proposal.
   Read `proposalBlocked` even when the process exits successfully. Compare the
   actual proposed settings with the brief and show the upstream settings card.
   Wait for the user's subsequent reply before full transcription, workspace
   creation or rendering. For a resumed job, use `workspace status` and the
   upstream revision and confirmation commands for changes to accepted settings.
3. Let the upstream workflow own the native `project.json`, cut decision list,
   review evidence and render. Use its representative sample and the selected
   reviewer, then deliver through `workspace export` only after the current
   candidate clears its checks. Return the project revision, verified MP4,
   requested original-language SRT/VTT and the delivery manifest under the
   revision's `edit/deliveries/`. Keep local paths and evidence in the task.
   Surface stale review, missing checks, and failed export as incomplete.

Use the upstream timeline as the only editable clock for that job. Other skills
can consume an exported video and its sidecars as assets in a later edit. The
handoff does not require installing Editonny for ordinary Video Editing or
shipping its runtime, website, scenes or media in Agentic Workflows.

The handoff and the spoken footage guidance were informed by Editonny 1.1.0 at
[`49714f2`](https://github.com/soumatheusgomes/editonny/tree/49714f2fba6eafb76b903376e1fe9f50b685506a).
Use the resolved installation's instructions for its
[setup](https://github.com/soumatheusgomes/editonny/blob/49714f2fba6eafb76b903376e1fe9f50b685506a/skills/editonny/references/setup.md)
and [managed editing workflow](https://github.com/soumatheusgomes/editonny/blob/49714f2fba6eafb76b903376e1fe9f50b685506a/skills/editonny/engine/WORKFLOW.md).
