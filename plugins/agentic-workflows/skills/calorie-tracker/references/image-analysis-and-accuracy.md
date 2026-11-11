# Image analysis and accuracy

A single photograph can support a useful estimate, but it cannot directly measure edible weight,
oil absorbed during cooking, hidden ingredients, recipe proportions, or the amount already eaten.
Accuracy therefore comes from reducing uncertainty in layers, not from assigning a more precise
number to the same uncertain pixels.

## Accuracy process

### 1. Check whether the image can answer the question

Confirm that the image is clear enough to identify the main foods. Record occlusion, poor light,
extreme camera angle, missing scale, cropped containers, mixed dishes, and partly eaten portions.
If the image cannot distinguish plausible foods with materially different nutrition, stop and ask
for another view or a description.

### 2. Create a visible inventory

List each visible component separately: staple, protein, vegetables, sauce, garnish, drink, and
inedible material. Record packaging, brand, barcode, nutrition panel, utensils, plate/container
shape, preparation cues, and remaining portion. Phrase observations narrowly: “golden breaded
piece” is visible; “deep-fried chicken breast containing 18 g oil” is not.

### 3. Separate evidence from inference

Every material statement belongs to one class:

| Class | Examples | Authority |
| --- | --- | --- |
| Visible | label text, barcode, counted pieces, apparent preparation cue | Direct but limited to pixels |
| User | weighed grams, recipe, product name, portion consumed | Highest for the supplied fact |
| Provider | nutrient values and serving basis from a matched record | Authoritative only for that record |
| Inference | likely oil, edible fraction, visual portion range | Explicit assumption, never fact |

Do not silently turn an inference into a provider query or final row.

### 4. Resolve food identity before weight

Prefer an exact visible/user label and barcode. For generic food, compare a small USDA candidate
set by description, preparation, form, and data type. A visually similar candidate is not an exact
match. If two reasonable matches would materially change the result, show at most three candidates
and ask the user.

### 5. Estimate edible amount as a range

Use evidence in descending order:

1. measured edible weight supplied by the user;
2. label serving and number of servings consumed;
3. recipe quantity and fraction consumed;
4. standardized package/container size;
5. familiar count or household measure;
6. visual volume/plate estimate with a deliberately wider range.

Subtract or separately represent bones, shells, pits, packaging, broth left behind, and food
already eaten. Record low, central, and high grams for every item. Mixed dishes, curries, soups,
restaurant meals, sauces, and fried foods need wider ranges because recipe and oil dominate error.

### 6. Normalize nutrition deterministically

Normalize provider nutrients to kcal, grams, and milligrams per 100 g, retaining provider ID,
original serving context, retrieval time, and match reason. Multiply by edible amount. Missing
optional values remain null; they are not zero. Do not combine incompatible “as prepared” and “as
sold” records.

### 7. Calculate and cross-check

Sum item central estimates. Derive calorie low/high values from the item amount ranges. Compare the
provider energy with `4 × protein + 4 × carbohydrate + 9 × fat`; flag a material discrepancy but
preserve provider energy because fiber, alcohol, organic acids, rounding, and methods can differ.

### 8. Assign confidence from the weakest material link

- **High (about 0.85–1.00):** weighed portion or exact label, strong product match, little hidden
  preparation uncertainty.
- **Medium (about 0.60–0.84):** credible identity and household/visual portion range, with bounded
  oil or recipe uncertainty.
- **Low (below 0.60):** mixed or occluded food, weak scale, uncertain recipe, unmatched provider,
  or materially different plausible candidates.

Confidence is not a statistical probability unless a validated model establishes it. Tracking
should stop when confidence is too low to support the user's intended use.

### 9. Report useful precision

Show a central estimate, plausible range, assumptions, and the inputs that would improve it. Round
the presentation in proportion to uncertainty; do not display false single-kcal certainty from a
wide visual portion estimate. Make clear that this is a wellness estimate, not medical advice.

## Questions that materially improve accuracy

Ask for the consumed weight, number of servings, product/restaurant name, cooking method, added
oil/butter, sauce quantity, recipe ingredients, whether the whole pictured portion was eaten, or a
clear label photo only when the answer could change food identity or totals. Do not interrogate the
user about inconsequential garnish or force questions when a broad range already communicates the
uncertainty honestly.
