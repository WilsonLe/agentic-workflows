# Photo adjustment parameter guide

Research reviewed 28 July 2026. This is the user-facing adjustment vocabulary for
Food Image Editing. It standardizes intent across editors; it does not claim
pixel-equivalent parity with the unidentified mobile editor in the supplied
screenshots.

## How to expose an adjustment request

When proposing or reporting an edit, include an `adjustment_brief` with every
control below. Use `0` for a neutral signed control, `1` for a neutral ratio, and
`null` when a structured control is unused. Values are recommendations, not a
license to skip visual review.

```json
{
  "adjustment_brief": {
    "lightness": 0,
    "contrast": 0,
    "warmth": 0,
    "tint": 0,
    "saturation": 1,
    "curves": null,
    "hsl": {
      "red": [0, 1, 0],
      "orange": [0, 1, 0],
      "yellow": [0, 1, 0],
      "green": [0, 1, 0],
      "aqua": [0, 1, 0],
      "blue": [0, 1, 0],
      "purple": [0, 1, 0],
      "magenta": [0, 1, 0]
    },
    "fade": 0,
    "highlights": 0,
    "shadows": 0,
    "color": null,
    "hue": 0,
    "vignette": 0,
    "sharpen": 0,
    "grain": 0,
    "film_grain": null
  }
}
```

The HSL tuple is `[hue_shift_degrees, saturation_ratio, luminance_shift]`.
`color` is an explicit tint object such as `{"hex":"#d98b55","amount":0.05}`;
never treat the screenshot label alone as a defined algorithm. `film_grain` is a
structured intent such as
`{"amount":0.08,"size":"fine","roughness":0.25,"midtone_bias":0.5}`.

This brief is not the executable `food_image.py` recipe. Map only supported,
justified controls into the recipe. Never add an unknown recipe key and assume
it worked. If the current helper cannot execute a requested control
deterministically, report that gap and either use a separately recorded,
non-generative editor operation or leave it unapplied.

## Control map

| Control | What it changes | Use it when | Avoid or reduce it when | Combine with |
| --- | --- | --- | --- | --- |
| Lightness | Overall perceived brightness or midtone placement | the whole dish reads too dark or too bright after white balance | only highlights or shadows are wrong; use targeted tone controls instead | Highlights/Shadows, then Curves |
| Contrast | Separation between light and dark values, usually strongest in midtones | the image is flat and food edges lack separation | sauce gloss clips, char blocks up, or white crockery loses texture | Curves for finer placement |
| Warmth | Blue-to-yellow/orange white-balance axis | capture lighting is too cool or too warm | warmth is part of the cuisine or ambient-light truth | Tint, then inspect neutral and food-critical areas |
| Tint | Green-to-magenta white-balance axis | fluorescent or mixed lighting leaves a green/magenta cast | no trustworthy neutral evidence exists | Warmth; adjust as one white-balance decision |
| Saturation | Global color intensity | the entire image is plausibly dull or over-vivid | only one ingredient family is wrong | HSL for selective correction |
| Curves | Input-to-output tone mapping; points can target shadows, midtones, highlights, or RGB channels | basic tone controls cannot place contrast precisely | the same result is available with one simpler slider | Lightness first; use a restrained curve afterward |
| HSL | Hue, saturation, and luminance of eight broad color families | one ingredient color is distracting or inaccurate | similar colors belong to different ingredients or surfaces | global white balance and saturation first |
| Fade | Lifted black floor and/or compressed tonal separation for a washed look | a deliberate editorial matte look is required | menu truth, glossy sauces, char, or depth need faithful blacks | restrained Curve; reassess saturation |
| Highlights | Bright tonal range | specular areas or white plates need recovery or controlled emphasis | the source is already clipped; no slider restores missing texture | Shadows, then Curves |
| Shadows | Dark tonal range | near-facing food contains recoverable structure | opening them reveals noise or removes depth | denoise before sharpening if needed |
| Color | An explicitly named tint/colorize operation | a controlled creative grade is requested | “Color” is the only specification; obtain hue and amount | tonal-range color grading or a previewed local mask |
| Hue | Global rotation of all hues | a deliberate stylized palette is requested | realistic food color or ingredient identity matters | rarely with HSL; prefer HSL for corrections |
| Vignette | Edge luminance relative to the center | subtle edge control supports the hero dish | overhead spreads fill the frame, plates touch edges, or corners are already dark | place after crop; inspect plate rims |
| Sharpen | Edge contrast, not recovered focus | a correctly focused image needs restrained output crispness | motion blur, missed focus, halos, or high-ISO noise are visible | denoise first; size for final output |
| Grain | General synthetic noise/texture | light texture prevents a clinically smooth finish or masks mild banding | clean menu/product output, noisy capture, tiny export, or smooth sauce gradients | use alone for neutral texture |
| Film Grain | Analog-film simulation with controlled size, roughness, and tonal bias | a clearly requested editorial or film look needs organic, luminance-aware texture | accurate menu/product output or the source already has strong noise | usually use instead of Grain |

Adobe documents Temperature and Tint as the blue/yellow and green/magenta
white-balance axes, and describes HSL as selective hue, saturation, and
luminance control across red, orange, yellow, green, aqua, blue, purple, and
magenta ranges:
<https://helpx.adobe.com/lightroom/mobile/adjust-light-and-color/adjust-colors.html>
<https://helpx.adobe.com/ca/lightroom-classic/help/color-mixer.html>

Adobe describes curves as input-to-output tonal mapping and recommends basic
light controls before granular curve work:
<https://helpx.adobe.com/ca/lightroom/mobile/adjust-light-and-color/adjust-tonal-range-using-curve.html>

Adobe describes sharpening as edge-definition enhancement and warns through its
radius/detail controls that excessive settings can look unnatural. It describes
vignette as edge darkening or lightening and grain as an analog-film effect:
<https://helpx.adobe.com/ae_en/lightroom-cc/using/edit-panel-android.html>

## Grain versus Film Grain

For this skill, `grain` and `film_grain` are deliberately different:

- **Grain** means a general texture/noise layer. Its primary controls are amount,
  scale, monochrome versus chroma, and seed. It need not imitate a film stock.
- **Film Grain** means a luminance-aware analog simulation. It should expose
  amount, size/coarseness, roughness, midtone bias, and seed. Darktable's
  documented film-grain model works on Lab luminance and provides coarseness,
  strength, and midtone bias; that is evidence for treating film grain as more
  than uniform noise:
  <https://docs.darktable.org/usermanual/development/en/module-reference/processing-modules/grain/>

Neither control removes sensor noise. Existing capture noise is a source defect
to measure and, when justified, denoise before adding intentional texture.

### Combination matrix

| Scenario | Grain | Film Grain | Decision |
| --- | ---: | ---: | --- |
| Faithful delivery-menu or product image | Off | Off | Preserve clean surfaces and ingredient truth |
| Natural social food post, digital look retained | Very low, fine, monochrome | Off | Add only enough texture to avoid sterile smoothness |
| Editorial analog look | Off | Low to moderate, fine or medium, midtone-biased | Prefer the structured simulation by itself |
| Strong vintage campaign explicitly requested | Very low optional texture | Moderate film grain | Stack only after separate previews prove the first effect leaves a specific texture gap |
| High-ISO or underexposed source | Off | Off | Denoise selectively first; adding texture compounds noise |
| Macro/detail with crisp garnish or glossy sauce | Off or very low | Usually off | Grain can obscure the focus plane and specular texture |
| Large print | Low and sized at final resolution | Low to moderate with output-aware size | Judge at print size and 100%; avoid screen-only decisions |
| Small compressed social export | Off or extremely low after resize | Off or fine/low after resize | Coarse texture aliases or turns into compression artifacts |
| Flat background shows banding after grading | Very low monochrome | Off | General texture may dither the transition without imposing a film look |
| Adjacent video stills must match | Match the sequence exactly | Match the sequence exactly | Never introduce a one-frame texture discontinuity |

Default rule: choose neither, Grain only, or Film Grain only. Use both only when
the user explicitly wants a strong stylized finish and side-by-side previews
show distinct, non-duplicative roles. If both are used, apply the structural
Film Grain first and a much weaker fine Grain pass second. Record both seeds for
reproducibility.

## Interaction and ordering matrix

| First decision | Second decision | Why this order matters |
| --- | --- | --- |
| Crop/rotate | Vignette | edge placement depends on the final canvas |
| Warmth + Tint | Saturation/HSL | a color cast can masquerade as weak or excessive saturation |
| Lightness + Highlights/Shadows | Curves | broad corrections should precede precise tonal shaping |
| Global Saturation | HSL | use the selective tool only for remaining color-family problems |
| Denoise | Sharpen | sharpening first amplifies source noise |
| Tone/color/HSL | Grain or Film Grain | texture should not interfere with color and clipping judgments |
| Resize | final Sharpen and texture sizing | edge radius and grain scale are output-resolution dependent |
| Film Grain | optional fine Grain | the film model carries the look; generic texture may only fill a demonstrated gap |

## Food-specific decision rules

1. Correct white balance before judging saturation. A warm cast can make
   browned food look more cooked and greens look dull; a green cast can make
   meat or sauces look unappetizing.
2. Use Highlights to protect believable gloss, not erase it. Specular cues help
   communicate moisture, oil, and freshness, while clipping removes texture.
3. Use Shadows to reveal readable structure without flattening depth. Stop when
   noise, gray blacks, or implausible fill light becomes more visible than food.
4. Use HSL only after identifying every major object sharing that color range.
   Red changes may affect tomato, chili, ceramic, and reflected light together.
5. Prefer luminance over saturation when a colorful garnish merely needs more
   separation. Large saturation moves change perceived ripeness, doneness, and
   ingredient identity.
6. Treat Fade, global Hue, Color tint, Vignette, Grain, and Film Grain as
   creative controls. They are off by default for evidence-led correction.
7. Preview at normal viewing size and 100%. Normal size reveals hierarchy;
   100% reveals halos, noise, mask seams, and grain scale.
8. Compare against the unchanged original and any adjacent campaign or video
   frames. A technically attractive single edit can still fail consistency.

Food-perception research cited in
[research-and-guardrails.md](research-and-guardrails.md) supports protecting
plausible saturation and luminance distribution, but it does not establish a
universal appetizing preset. Every numeric move remains image-specific.
