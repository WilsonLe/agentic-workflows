---
name: motion-design
description: Create or revise code-authored animated artwork, kinetic typography, explainers, and product showcase videos with editable browser scenes, exact-frame rendering, synchronized sound, and visual review. Use for a finished motion graphic or video; interactive interface animation remains with UI Design.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- **Required: Motion rendering runtime** — Install Node.js 22 or newer, a project-local pinned HyperFrames CLI and animation dependencies, and a compatible Chromium browser. Use an existing project setup when available.
- **Required: FFmpeg and ffprobe** — Provide FFmpeg and ffprobe on PATH or through the documented local binary overrides.
- **Required: Python runtime** — Install Python 3.10 or newer for the bundled final-video verifier; it uses only the standard library.

<!-- catalog-prerequisites:end -->

# Motion Design

Turn the brief into an editable browser composition and a video whose actual
rendered frames have been inspected. Use the existing HyperFrames renderer for
seekable HTML/SVG/Canvas/Three.js scenes; Playwright is useful for real product
captures and independent frame inspection. FFmpeg handles encoding and sound.

## Frame the piece

Read supplied artwork, references, and the product's current code or documentation.
Find the visual idea, intended audience, duration, format, and sound direction.
Infer routine choices from the brief; ask only when missing information materially
changes the deliverable. A request for a finished video authorizes local renders
and revisions; it does not authorize publishing or paid generation.

For a product showcase, capture the actual UI in an isolated browser context with
task-owned sample media. Show supported features and source any numbers. Recreated
screens or simulated AI replies need an illustrative label. Existing raster art
supports camera moves and masks; independent subject movement needs layers or
geometry. Preserve supplied artwork and accepted style rather than imposing a look.

## Build and look

1. Describe the timed visual beats and sound cues. Make movement carry the idea:
   hierarchy, readable holds, transformations, anticipation, easing, and continuity
   should serve this specific piece. Keep one timeline as the owner of timing.
2. Read [scene and rendering](references/scene-and-rendering.md). Start from the
   [editable composition](templates/index.html) when there is no existing owner.
   Choose DOM/SVG for type and vector art, Canvas for procedural drawing, and
   Three.js for meaningful depth. Keep assets and dependencies local and pinned.
3. Inspect key-moment stills and a fast draft. Read
   [visual review and sound](references/visual-review-and-sound.md); inspect phone
   readability, overlap during handoffs, motion rhythm, and any requested loop seam.
   Fix concrete timestamped problems and render the affected candidate again.
4. Export the requested formats. Run the bundled technical verifier, extract review
   frames from the **encoded final file**, and inspect them. Metadata validation and
   contact sheets do not prove smooth playback or pleasing sound: play/listen with
   available tools and report any unobserved dimension. Never describe an earlier
   draft's review as evidence for a changed final render.

Deliver the video, editable HTML/timeline/local assets, and a short account of
technical and visual checks. Keep drafts and evidence in the task's output folder;
do not add large media or dependencies to a source repository by default. In a Git
repository, follow its delivery workflow for tracked skill/code edits.

## Technical verification

```sh
python3 <skill-dir>/scripts/verify_video.py final.mp4 \
  --width 1920 --height 1080 --fps 60 --frames 900 --require-audio
```

Supply the actual brief's dimensions, frame rate, and integer frame count. Omit
`--require-audio` for an intentionally silent piece. `--ffprobe` selects an existing
binary when it is outside PATH. A technical pass proves decoded frame count,
timing, dimensions, and requested audio presence; it never grants visual approval.

Read [research and reuse](references/research-and-reuse.md) when choosing a
different backend, borrowing upstream code, or expanding beyond this workflow.
