# Compositing, transitions and keyframes

## Pace and continuity

Default footage to normal real-time speed unless the current brief calls for
retiming. Energy can come from action, shot choice and sound. When speed variation
is rejected, set footage to 1× and adjust source trims against the existing output
schedule, preserving accepted grade, framing, text and duration where feasible.
If a source handle is too short, choose another range or surface the pacing tradeoff.

Assess shot length together with camera movement and subject position. Repeated
fast pans plus short holds can disorient even when each shot is technically valid.
Use steadier ranges, longer holds and motivated cutaways; inspect neighboring
frames for a subject jumping across the screen when switching angles of one action.
Treat repeated activity across different sources as repetition, not extra variety.

Synchronize to the actual music asset and its measured duration/offset. Use phrases,
section changes and selected accents while retaining the accepted hold lengths and
scene coverage. A detected beat is a candidate cut, not a command to cut. Recheck
source motion, trims, ending and audio placement after snapping; music-only changes
do not silently reset the accepted edit, and cut changes return to the timing owner.

## Blend and transition deliberately

Use the selected editor/compositor's existing tracks and effect stack. For FFmpeg,
consult the installed filter help and [filter documentation](https://ffmpeg.org/ffmpeg-filters.html)
for `blend`, `overlay`, `xfade`, `acrossfade`, `setpts`, `fps` and color conversions.
Backend support and alpha/pixel formats vary; validate one representative transition.

Normalize participating inputs to compatible frame rates, dimensions, time bases
and intended color handling before transitions. Honor rotation, pixel aspect,
HDR/SDR and premultiplied versus straight alpha. Avoid implicit HDR clipping or
double-premultiplication. Use layout/reframing to preserve text and subjects.
Choose blend modes for a purpose: alpha overlay for a title, screen/add for light,
multiply for shadow, masks/chroma keys for selective compositing. Inspect fringes,
spill and semi-transparent edges over the actual background. Do not claim normal
H.264 MP4 preserves transparency; use an alpha-capable intermediate when required.

For two 5-second shots with a 1-second overlap, place B at output second 4; the
cut lasts 9 seconds. Verify both source handles exist across the overlap. A fade
through black has different placement from a crossfade. Pair visual transitions
with intentional audio cuts, crossfades or J/L cuts, preserving dialogue. Use motion
direction and match cuts before arbitrary effects. Inspect the first/last transition
frames and midpoint for frozen shots, double exposure, scale jumps and black gaps.

## Keyframe contract

Reuse the native editor's keyframes or Motion Design's seekable scene timeline.
Represent property animation by target/track, property, coordinate space/unit,
sorted unique output frame/value pairs, interpolation/easing and explicit hold
behavior outside the key range. Validate finite values, supported properties,
bounds and easing availability; choose an equivalent supported curve explicitly
when interchange cannot preserve one. An empty range or unresolved target fails.

Keyframe position, scale, rotation, opacity, masks, crop, color and audio gain where
the backend supports them. Distinguish step/hold, linear and eased interpolation;
Bezier handles change velocity, not merely endpoint values. Declare anchor/pivot
and transform order. Keep spatial paths and temporal easing separate. Retime
source media independently of transforming its appearance. Prevent unintended
overshoot at masks, opacity and audio gain boundaries.

For animated shots, hand Motion Design local-frame timing plus the placement offset.
It owns implementation and deterministic seeking; see its scene contract. Seek A,
B, A and reverse/boundary frames on the same rendering stack. Inspect the encoded
cut for motion continuity and sync. Keyframe availability in source does not prove
the exporter honored curves or that playback is smooth.
