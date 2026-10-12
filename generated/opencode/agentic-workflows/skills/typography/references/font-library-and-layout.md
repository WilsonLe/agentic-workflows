# Font library and layout

## Discover and download static assets

Search existing local libraries, the exact foundry or an open library such as
[Google Fonts](https://github.com/google/fonts). Inspect the selected family files
and license; download actual TTF/OTF static faces and their license/model metadata
from the authoritative source into the task's font library. A stylesheet URL or
preview image is not a downloaded font. Font engine and font file licenses differ.
Retain source URL/revision and embedding/redistribution terms. Paid or proprietary
fonts need authorized access; do not extract them from protected applications.

Inspect file tables with an existing [fontTools TTFont](https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html)
installation or an equivalent font inspector. Read name records, OS/2 weight/width,
cmap and `fvar` when present. Prefer real static styles. If only a variable file is
available and its license permits, use the existing
[fontTools instancer](https://fonttools.readthedocs.io/en/latest/varLib/instancer.html)
to pin **all** axes, including optical size if present. Verify the result has no
remaining `fvar` axes and record original hash plus axis values. Renaming a variable
file does not make it static. Inspect shaping/rendering of each selected instance.

## Index contract

`fonts-index.json` has `schema_version: 1` and a `fonts` array. Each static face has
content-hash `font_id`, local path, family/subfamily/PostScript names, weight, width,
italic flag, file format, source URL/revision, license path/status and editorial
labels. Record coverage evidence (cmap/codepoint ranges and tested language sample),
and derived-from hash/axis values for generated instances. Keep unknown values
null rather than guessed; mark unverified licenses as unavailable for final use.
Deduplicate by content hash and preserve manual labels during rescans. Validate
hash/path match, unique records, static status, required faces and intended text
coverage before rendering. A changed file receives a new ID; index stale paths as
missing and resolve them before the next render. Do not silently substitute a face.

## Size, formatting and shaping

Declare size in output-canvas pixels for video; scale the complete layout when
changing export dimensions. Define roles (title/subtitle/body/caption), weight/style,
line height, tracking, word spacing, alignment, text box, padding and safe area.
Use actual bold/italic files instead of synthetic styling where fidelity matters.
Choose font size by testing the longest required text at intended phone/desktop
size; no one numeric size works for every aspect ratio and language. Reflow text
for portrait versions instead of clipping a landscape layout.

Render script-specific shaping, ligatures, combining marks, RTL/bidirectional text,
emoji and punctuation with the selected renderer. Cmap coverage does not prove
correct shaping. Use a shaping-capable backend for complex scripts; inspect a
language sample before committing the full cut. Explicitly index fallback fonts
and test mixed-script text. Preserve semantic text and accessible caption sidecars
where requested; line-break choices should not change the words.

For browser scenes, load local faces with explicit family/style/weight mappings,
await font readiness and inspect the rendered sample before capture. A ready font
set can still contain fallback glyphs. Keep font files local for reproducible
offline renders; Motion Design owns capture readiness. For FFmpeg `drawtext`,
inspect the installed build's shaping/font options before promising advanced layout.

For kinetic type, specify anchor/pivot, masking, motion path, easing and readable
holds using Motion Design's keyframes. Review entry/exit extremes, subtitles during
transitions, contrasting backgrounds and the encoded output. Return the layout,
font IDs and checked frame ranges; report untested scripts or monitoring limits.
