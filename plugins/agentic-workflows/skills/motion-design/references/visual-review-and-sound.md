# Visual review and sound

Inspect scenes at their named beats, readable holds, and handoffs. Use sparse
stills for composition, dense strips for fast transitions, and draft playback for
rhythm. A sheet sampled once per second can miss a single-frame flash.

Judge the brief's actual intent: focal hierarchy, art continuity, readable type,
safe margins, masks, collision/occlusion, pace, and ending. Existing reference
styles guide choices; they do not mandate particles, gradients, constant movement,
bounce, or fixed spring presets. Text may move on entrance and exit but needs a
readable state. Scale a review to the intended screen size. For loops, inspect both
position and direction/speed through the seam, with frames on both sides.

Write the few worst concrete issues with timestamps, correct those causes, and
review the changed render. Keep iteration bounded by the brief and actual defects;
report unresolved limitations instead of inventing a passing aesthetic score.

## One timeline for sound

Store scene changes, accents, holds, and the ending in the composition's existing
timeline. Sound reads those same cues; avoid separately maintained magic timestamps.
Use provided/licensed music, locally synthesized tones/noise, or silence according
to the brief. Record asset sources and license terms for externally sourced media.
Paid generation or publishing requires authority for that effect.

Give every HyperFrames audio element a unique ID and explicit finite timing.
Place transient peaks on the intended visual event, fade tails, leave headroom,
and duck music when narration needs it. Listen for clicks, unintended silence,
clipping, and rhythm; a present audio stream does not prove audibility or quality.
Loudness targets depend on destination. Measure normalization instead of treating
one LUFS value as universal. Keep the final video length controlled by its timeline;
an accidentally short soundtrack must not truncate the video through `-shortest`.

## Review the encoded file

These commands illustrate final-file inspection; choose enough samples to cover
the actual timeline, not a single fixed sheet for every duration.

```sh
ffmpeg -i final.mp4 -vf "fps=2,scale=480:-1,tile=5x6" -frames:v 1 final-sheet.png
ffmpeg -ss 4.8 -i final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 transition.png
ffmpeg -i final.mp4 -af volumedetect -vn -f null -
```

For a longer piece, paginate sheets or extract frames at explicit cue timestamps;
the example overview covers only the first 15 seconds. Inspect extracted images
with the host's image viewer. Verify metadata with the bundled script and play the
final artifact through a video-capable preview. Distinguish technical validation,
visual frame inspection, observed playback, and listened audio in the handoff.
