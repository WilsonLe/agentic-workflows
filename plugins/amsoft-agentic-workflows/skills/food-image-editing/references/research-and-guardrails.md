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
| JPEG quality | 90–95 | delivery copy; retain lossless intermediate if needed |

These are review thresholds. A dark-key barbecue image, white-background delivery
menu image, glossy beverage, or deliberate silhouette may validly exceed them
when the reason is recorded and the output is visually checked.

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
