# Assets and timing

## Technical and editorial indexes

Index explicit local video, audio and raster-image files with the dependency-free
helper. Expand a folder into a reviewed file list first; the helper does not crawl
folders or download assets. An explicit list avoids accidentally probing private
or unrelated files. It follows the selected local file paths; review symlink targets.

```sh
python3 <skill-root>/scripts/index_assets.py \
  /absolute/assets/shot.mp4 /absolute/assets/voice.wav /absolute/assets/still.png \
  --output /absolute/output/assets-technical.json
```

Use `--ffprobe /absolute/path/ffprobe` for an existing binary outside PATH. Existing
indexes are preserved unless `--overwrite` names the intended task-owned index.
The helper hashes complete file contents and probes container/stream metadata via
[ffprobe](https://ffmpeg.org/ffprobe.html). It does not decode the complete media,
transcribe speech, establish clearance, or prove playback health.

The UTF-8 JSON output has `schema_version: 1` and an `assets` array. Each entry has
`asset_id` (SHA-256 prefixed with `sha256:`), resolved `path`, `bytes`, `container`,
finite `duration_seconds` or null, a `streams` array and empty `annotations`.
Streams retain ffprobe's indexes, codecs, dimensions, rational frame rates, sample
rates, channels, rotation/color tags and dispositions; absent fields remain absent.
Identical bytes share an ID even across different paths. A changed file gets a new
ID. No stream duration is invented from a filename or a missing container value.
Missing/empty files, probe errors/timeouts and invalid JSON fail before writing an
index. A metadata failure names its source; fix it or explicitly revise the asset
list, then rerun. Writes use a completed temporary file, preserving prior output.

Keep editorial annotations in `assets-editorial.json`, keyed by `asset_id`, so
reindexing cannot erase manual work. Record description, tags, usable ranges in
source seconds, orientation/color concerns, quality issues, provenance/license,
clearance status, transcript path and thumbnail/contact-sheet paths. Cite observed
ranges; label inferred content. A transcript refers to the original asset ID and
source clock. Font records belong to Typography's `fonts-index.json` and are linked
from the project, not fed to ffprobe. Generated speech, music and cleaned stems are
new indexed assets with lineage to their inputs.

## One timing owner

Reuse a native editor timeline when available; do not add a competing clock.
For a file-based edit, `timeline.json` extends Motion Design's existing `duration`
and `cues` contract. Use `schema_version: 1`, rational `fps` such as `30000/1001`,
positive integer `frames`, `duration = frames / fps`, finite named `cues` in seconds
within [0, duration], and `shots`. Optional `bpm` is consumed by Music Composition.
Its current synthesis starter supports at most 120 seconds; use another local
composition method or cue-aligned sections for longer films, not silent truncation.

Each shot has a unique `id`, indexed `asset_id`, `track`, half-open integer output
range `[start_frame, end_frame)`, source `[in_seconds, out_seconds)`, positive
`speed`, and any transition/keyframes. For constant speed,
`source_time = in_seconds + (output_frame - start_frame) / fps * speed`.
Ramps require an explicit monotonic source-time map; do not apply this constant-rate
formula to ramps. Stills have no source trim and use the output hold duration.
Scenes return local-frame renders plus their placement; audio records use sample
offsets and sample rate, converted from the same output frame clock.

Before rendering, validate IDs resolve, ranges are finite and ordered, source
trims fit observed duration, speed/duration agree within one output frame, cues fit,
and same-track overlaps are intentional transitions. Derive duration from the
output schedule; never sum full clip lengths and count transitions twice. Gaps must
be deliberate holds, silence or background, with the ending accounted for.
Unknown source duration needs a decode/inspection before committing a trim.
Version the timeline with asset hashes. Timing, font, script or asset changes
invalidate dependent previews and final evidence. Keep a checkpoint of accepted
beats, selected assets, backend/version, last successful render and pending fixes.
