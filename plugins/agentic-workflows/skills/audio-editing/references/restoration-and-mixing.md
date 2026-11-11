# Restoration and mixing

## Diagnose and process

Probe format, duration, start offset, sample rate, channel layout and peak levels.
Listen to representative speech, quiet passages, loud peaks and edits. Preserve
room tone and breath unless the brief requests their removal. Identify hum, hiss,
plosives, sibilance, clipping, reverb and crosstalk separately; one aggressive denoiser
is not a universal repair. Already-clipped recordings may remain unrecoverable.

Use suitable tools for spectral repair, de-clicking, de-humming, denoising,
de-reverberation, source separation and dialogue isolation when available. Compare
level-matched dry/processed passages for lost consonants, watery artifacts and
damaged transients. Preserve an untouched source and state when a separation model
hallucinates or removes useful sound. Never present it as a clean original stem.

Apply corrective EQ before chasing loudness: remove only unwanted low-frequency
energy, tame resonances and sibilance, then use compression/expansion deliberately.
Set attack/release for the material; audition pumping and breath modulation. Use
limiting for delivery peaks, not to hide overload earlier in the chain. Tune reverb,
delay, stereo width and panning to the scene; keep narration intelligible and check
mono folds for cancellation. Crossfade edits and fill unnatural holes with matching
room tone. For time stretch/pitch shifts, inspect formants and transient artifacts.

## Mix against the timeline

Use explicit sample offsets, trims and fade lengths in the shared edit timeline.
Gain automation has target stem/bus, ordered time/value pairs, units (dB versus
linear), interpolation and holds. Do not confuse 0 dB with digital silence.
Sidechain ducking uses the actual dialogue as a detector; audition attack/release
and ensure pauses do not create distracting surges. J/L cuts may cross visual
boundaries while preserving the intended speech placement. Compensation for plugin
latency and resampling must preserve sync and total duration.

Export dialogue, music and effects stems plus mix when needed. Stems share sample
rate, channel layout and time origin, with padding for a common duration. Declare
whether stems are pre/post bus processing; their sum may differ from a nonlinear
master. Keep speech generation takes and score sources linked by asset hashes.

## Tools and evidence

For FFmpeg, inspect installed filter help and the official
[audio filter documentation](https://ffmpeg.org/ffmpeg-filters.html). Relevant tools
include `afftdn`, `highpass`, `equalizer`, `acompressor`, `sidechaincompress`,
`afade`, `acrossfade`, `amix`, `loudnorm`, `ebur128` and `astats`. Select parameters
from measured/listened evidence, not a universal preset. Check filter availability
before promising advanced restoration; a DAW or specialized model may be needed.

Take the target from the actual delivery specification; no single LUFS value fits
every platform. For two-pass normalization, measure pass one and feed its values
to pass two, then measure the exported result. Distinguish sample peak, true peak,
integrated loudness and loudness range. Recheck after lossy encoding. A true-peak
claim requires a suitable true-peak meter, not a sample-peak statistic.

Reject missing/empty outputs, wrong duration/channel layout, failed decodes and
unexpected clipping. Record candidate hash, tool/version, treatment, measurements,
listened ranges and unresolved damage. Listen on the available monitoring path and
report its limits. Source changes invalidate transcript-derived trims; timeline or
processing changes invalidate old mix/encoded-video evidence.
