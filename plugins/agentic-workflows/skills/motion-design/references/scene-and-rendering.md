# Scene and rendering

## Existing renderer first

Use a project-local pinned HyperFrames CLI and animation dependencies. The first
working evaluation used HyperFrames 0.8.145 and GSAP 3.14.2 on macOS arm64 with
Node 22. Read the installed version's help before choosing flags; pin updates and
recheck frames when versions change. Do not install a collection of overlapping
agent skills or change global agent configuration to render one film.

```sh
npm install --save-exact hyperframes@0.8.145 gsap@3.14.2
# Copy the starter to index.html and the pinned gsap/dist/gsap.min.js beside it.
npx hyperframes doctor --json
npx hyperframes check
npx hyperframes snapshot --at 0,1,3,5
npx hyperframes render --quality draft --output draft.mp4
npx hyperframes render --quality delivery --output final.mp4
```

Doctor exits zero even when required capabilities are missing: inspect its checks.
Optional transcription or generative-audio tools are required only when selected.
Supply existing binaries through `HYPERFRAMES_FFMPEG_PATH`,
`HYPERFRAMES_FFPROBE_PATH`, or `HYPERFRAMES_BROWSER_PATH` when needed.
`HYPERFRAMES_NO_TELEMETRY=1` keeps renderer usage telemetry disabled for local work.
Use the task's resource budget to choose workers; do not hardcode one machine's
capacity. Rendering an authorized deliverable needs no additional preview approval.

HyperFrames owns compositor capture, clip lifecycle, media seeking, encoding, and
render readiness. The scene owns its appearance and seekable animation state.
Do not build a competing production capture engine unless the existing backend
cannot express the requested scene. Honor an explicitly chosen alternative.

## Composition contract

Use a standalone root directly in the body with `data-composition-id`, `data-width`,
`data-height`, `data-fps`, and a finite `data-duration`. Its CSS fills the canvas.
Register the complete paused GSAP timeline at `window.__timelines[id]`; the key
matches the root ID. Animate interior elements rather than overriding framework
visibility on timed clips. Read the backend's sub-composition rules before nesting.

All frame-critical state comes from time/frame plus frozen inputs. Load fonts,
images, models, and textures before readiness. Use seeded randomness; precompute
stateful physics or store deterministic simulation checkpoints. Await asynchronous
drawing/media work before capture. Preview may use a clock to call the same seek
function; export never derives scene state from elapsed wall time.

GSAP timelines can be paused and sought. Anime.js uses `seek(milliseconds)`;
WAAPI animations can be paused with `currentTime` set explicitly. Prefer the
backend's adapter for each runtime rather than inventing a second time owner.

For independent Playwright inspection of a standalone scene, await
`window.motionReady`, call `window.seek(seconds)`, then take screenshots. Seek A,
B, A and compare the two A images on the same browser/font/GPU stack. A mismatch
exposes hidden state or unfinished work. Test boundary frames and random order,
including reverse seeks. Exact pixels across different machines require a pinned
render environment; seekability alone cannot promise cross-platform identity.

## Failure and output behavior

Treat browser exceptions, unavailable assets, empty duration, stalled readiness,
failed encoders, and missing/partial frames as failures. Keep the failed log and
candidate; fix the identified cause before retrying. Write outputs under a unique
task/version directory, preserve prior masters, and resume an existing live render
rather than launching a competing one. Check the process exit status and final
artifact, not only a progress bar.

Ordinary MP4 delivery uses H.264, yuv420p, and faststart. Request alpha explicitly
when needed and select an alpha-preserving intermediate such as ProRes 4444 MOV;
the normal MP4 preset does not preserve it. PNG sequences are useful for debugging
and resuming; direct frame streaming reduces temporary disk use. Match aspect
ratios through layout/reframing rather than cropping readable content.

Real-time Playwright video is suitable for interaction recordings and rough
previews. Set its video dimensions explicitly and await context closure. For exact
motion export, seek each frame rather than recording at wall-clock speed.
