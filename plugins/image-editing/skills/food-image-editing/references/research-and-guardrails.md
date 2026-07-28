# Research basis and editing guardrails

Research reviewed 27 July 2026. Sources are linked directly. This document
distinguishes published findings from operational guardrails chosen for this
workflow.

## What research supports

- Adobe documents histogram clipping as pixels shifted to the maximum or minimum
  value with lost detail, and recommends inspecting channel-specific highlight
  and shadow clipping while adjusting tone:
  <https://helpx.adobe.com/uk/lightroom-classic/help/image-tone-color.html>
- Adobe’s export documentation treats color space as output-dependent and
  supports tagged sRGB for broadly compatible SDR delivery:
  <https://helpx.adobe.com/lightroom-classic/desktop/export-photos/export-files-disk-or-cd.html>
- The CIE standardizes CIEDE2000 as a color-difference formula. It is appropriate
  for comparing a measured neutral/reference before and after, not for deciding
  whether a dish is aesthetically appetizing:
  <https://www.cie.co.at/publications/colorimetry-part-6-ciede2000-colour-difference-formula-1>
- Sharma, Wu, and Dalal document CIEDE2000 implementation pitfalls and publish
  reference test data. The workflow must not label another distance calculation
  as CIEDE2000:
  <https://doi.org/10.1002/col.20070>
  <https://hajim.rochester.edu/ece/sites/gsharma/ciede2000/>
- ImageMagick defines `-fuzz` as a spherical similarity distance in the active
  color space and recommends perceptual Lab or Luv when RGB distance does not
  reflect visible similarity. This workflow uses that efficient runtime
  behavior for full-resolution masks; the percentage is not ΔE00:
  <https://usage.imagemagick.org/color_basics/>
- ImageMagick seed flood fill affects only matching pixels connected to the
  selected point. Its documentation also warns that fuzzy fills can stop before
  an edge or leak through weak boundaries:
  <https://imagemagick.org/command-line-options/>
  <https://usage.imagemagick.org/draw/>
- ImageMagick morphology defines Open, Close, Erode, Dilate, Edge, EdgeIn,
  EdgeOut, and distance gradients. These operations support deterministic mask
  cleanup, outline inspection, and feather construction:
  <https://usage.imagemagick.org/morphology/>
- ImageMagick connected-components labeling reports region count, area, bounds,
  and related shape measures. The workflow uses component count as a review
  signal, never as semantic recognition:
  <https://imagemagick.org/connected-components/>
- ImageMagick alpha composition implements grayscale mask influence and
  Porter-Duff/W3C-style operators. A soft mask controls how much of the adjusted
  duplicate affects each destination pixel:
  <https://imagemagick.org/compose/>
- Porter and Duff formalized image compositing as source/destination color and
  coverage algebra. The workflow uses normal source-over-style masked blending
  and does not use layering as permission to introduce a new scene:
  <https://keithp.com/~keithp/porterduff/>
- Levin, Lischinski, and Weiss show that natural-image matting can infer soft
  alpha from local color-line assumptions, while He, Sun, and Tang show guided
  filtering can refine mattes with edge-aware linear-time filtering. Both are
  relevant future techniques, but neither is required for this ImageMagick-only
  deterministic implementation:
  <https://people.csail.mit.edu/alevin/papers/Matting-Levin-Lischinski-Weiss-CVPR06.pdf>
  <https://doi.org/10.1007/978-3-642-15549-9_1>
- Ruseva, Giesel, and Hesse found decreasing saturation reduced reported craving
  and perceived palatability, especially for perishable foods. This supports
  protecting plausible color; it does not justify maximal saturation:
  <https://doi.org/10.1016/j.appet.2025.108323>
- Liu et al. found higher saturation can increase online food purchase intention,
  mediated by freshness and tastiness, but the effect depended on visual distance
  and social context. Close food does not necessarily benefit from the same
  saturation increase as distant food:
  <https://doi.org/10.1016/j.jbusres.2022.06.061>
- Ueda et al. found changes in the standard deviation of food-image luminance
  affected expected moistness, wateriness, and deliciousness. Preserve useful
  local luminance variation rather than flattening texture:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC7528116/>
- Arce-Lopera et al. linked luminance-distribution statistics to perceived
  vegetable freshness:
  <https://doi.org/10.1016/j.foodqual.2012.03.005>
- Murakoshi et al. experimentally manipulated camera angle, background,
  lighting, light color, and decoration in food photography, confirming these
  factors interact in judgments of deliciousness:
  <https://www.jstage.jst.go.jp/article/ijae/21/1/21_TJSKE-D-20-00076/_article/-char/en>
- The Institute of Culinary Education describes three practical food angles:
  overhead for top surfaces and arrangement, side for structure/height/layers,
  and 45 degrees for a diner-like view:
  <https://www.ice.edu/blog/food-photography-angles-and-composition>
- YouTube documents 16:9 as its standard computer aspect ratio and square or
  vertical video as Shorts-compatible. The workflow offers 9:16 and 16:9 output
  plans but requires composition review before either crop:
  <https://support.google.com/youtube/answer/6375112>
  <https://support.google.com/youtube/answer/12779649>

## Operational guardrails, not scientific optima

The literature does **not** provide universal Lightroom-style slider numbers for
all cuisines, cameras, lighting, and platforms. The following limits are
conservative engineering defaults selected to prevent aggressive first passes:

| Measurement or control | First-pass guardrail | Reason |
|---|---:|---|
| Highlight clipping | under 0.5% | retain texture; specular exceptions documented |
| Shadow clipping | under 0.5% | retain readable structure; silhouettes excepted |
| Increase in either clipping | at most 0.25 percentage points | catch destructive edits |
| Exposure | ±0.35 EV | visible but recoverable first pass |
| RGB neutral-patch gain | 0.80–1.25 per channel | reject implausible automatic WB |
| Global saturation ratio | 0.90–1.15 | protect realism and cuisine identity |
| Sigmoidal contrast | ±2.0 | preserve highlight and shadow gradients |
| Global sharpening amount | 0–1.0 | reduce halos and false texture |
| Adjustment-layer opacity | 0.05–1.0 | make layer strength explicit; start low and inspect mask transitions |
| Adjustment layers | at most 8 | bound complexity and preserve auditable provenance |
| Color-mask fuzz | 0.1–20%; start at 3–8% | bound similarity expansion; inspect every threshold |
| Mask Open/Close radius | 0–12 px | remove small noise/fill small holes without reshaping the subject wholesale |
| Mask grow/shrink | −24–24 px | small boundary correction only |
| Mask feather | 0–64 px | continuous alpha transition; choose relative to resolution and edge character |
| Mask combinations | at most 8 | keep mask algebra auditable and non-recursive |
| JPEG quality | 90–95 | delivery copy; retain lossless intermediate if needed |

These are review thresholds. A dark-key barbecue image, white-background delivery
menu image, glossy beverage, or deliberate silhouette may validly exceed them
when the reason is recorded and the output is visually checked.

Layer opacity and count are workflow limits, not research-derived aesthetic
optima. A valid stack may use fewer layers; zero is preferred when global or one
local correction is sufficient. The stack may only composite corrected copies of
the current source-derived image through geometric or source-derived
color-similarity masks. It may not introduce, clone, relocate, or synthesize
scene content.

## Color-derived mask decision model

Color similarity is evidence about pixels, not evidence about objects. Two
different ingredients can share a color; one ingredient can span many colors
because of light, gloss, char, sauce, or shadow. Use this sequence:

1. Choose a seed well inside the intended region, away from antialiased edges,
   specular highlights, cast shadows, or mixed-light transitions.
2. Bound the search with the smallest ROI that contains the intended connected
   region. Flood fill occurs within the cropped ROI so it cannot leave and
   re-enter through an external path.
3. Start with Lab unless luminance/chroma separation is visibly poor; compare
   Luv only by preview, not by assumption.
4. Begin at 3–8% fuzz. Raise it only while inspecting the binary mask and
   outline. Values over 12% receive an explicit high-fuzz warning.
5. Use Open for small selected protrusions/noise, Close for small holes, and
   grow/shrink for a visibly justified boundary offset. Do not use morphology to
   manufacture missing food edges.
6. Combine masks in order. Intersect narrows the selection, union adds a known
   geometric zone, and subtract protects a known region. Nested color-derived
   masks are deliberately rejected so provenance stays finite.
7. Inspect the binary selection, its outline, the soft alpha, and a colored
   overlay. A clean histogram or component count cannot replace this review.

The tool rejects an empty mask. It warns on near-full or large canvas coverage,
multiple foreground components, ROI-boundary contact, and high fuzz. Those
warnings identify review risk, not failure by themselves. Inversion legitimately
creates large affected areas, so coverage is reported for both the filled binary
selection and final alpha influence.

The cleaned binary mask is the reproducible selection. The morphological outline
is a QA artifact showing where the selection changes. The alpha mask is the
filled selection after feather, inversion, and layer opacity; it is the artifact
used for compositing.

## Measurements used by the tool

- Luma: Rec. 709 coefficients on an sRGB analysis rendering.
- Clipping: fraction of samples at the extreme 8-bit endpoints, reported for
  luma and for any RGB channel.
- Percentiles: p01, p05, p50, p95, and p99 of luma.
- Contrast: luma standard deviation and RMS contrast (`stddev / mean`).
- Saturation: HSV-style chroma ratio `(max(R,G,B)-min(R,G,B))/max(R,G,B)`.
- Edge energy: mean absolute first difference in luma. This is a coarse texture
  indicator, not a proof of focus.
- Zones: mean luma and saturation in a 3×3 grid, plus an attention proxy combining
  local contrast, saturation, and edge energy. It is not object recognition.

Measurements are computed on a downsampled, auto-oriented sRGB rendering for
speed. They guide review; they do not replace visual judgment or a color-managed
monitor.
