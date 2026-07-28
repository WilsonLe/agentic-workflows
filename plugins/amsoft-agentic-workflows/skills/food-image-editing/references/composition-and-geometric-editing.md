# Composition, crop, and geometric editing

Research reviewed 28 July 2026. This reference turns composition into an
auditable editing decision without pretending that one grid, score, or crop is
universally best. It applies only to source-derived, non-generative food-image
editing.

## Research-supported principles

- Composition guides attention, but food-image judgments depend on interactions
  among camera angle, light, background, color, and decorative placement.
  Murakoshi et al. found no single factor or arrangement that wins in every
  condition:
  <https://www.jstage.jst.go.jp/article/ijae/21/1/21_TJSKE-D-20-00076/_article/-char/en>
- Crops tend to be preferred when salient regions remain in a balanced
  arrangement. Abeln et al. also found that simple single-rule models are
  insufficient and that gaze-informed crops can outperform fully automatic
  crops:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC7739184/>
- A crop must be judged as a new frame, not merely as retained subject matter.
  Lu et al. model both content saliency and where that content lands inside each
  crop candidate:
  <https://ojs.aaai.org/index.php/AAAI/article/view/6896>
- Rule of thirds is a useful hypothesis, not a law. In a controlled
  single-object experiment, Wang et al. found a strong preference for centered
  placement:
  <https://openreview.net/forum?id=uynrv2jQOP>
- Nikon food-photography guidance describes overhead framing for arrangement,
  varied prop scale, deliberate partial prop crops, triangles, negative space,
  and a clear hero:
  <https://www.nikonusa.com/learn-and-explore/c/nikon-creators/cooking-up-mouthwatering-food-photographs>
  <https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/create-your-light-food-photography-at-home>
- ImageMagick Perspective is a four-point source-to-destination mapping.
  Distortion viewports can reveal pixels outside the valid source region, so
  this workflow maps one reviewed source quadrilateral directly to a bounded
  rectangle:
  <https://usage.imagemagick.org/distorts/>
- Seam carving removes or inserts low-energy paths. Mesh-based aesthetic warp
  can reposition salient regions and lines. Those capabilities deliberately
  change spacing or geometry and therefore fall outside this truth-preserving
  food workflow:
  <https://www.cs.jhu.edu/~misha/ReadingSeminar/Papers/Avidan07.pdf>
  <https://doi.org/10.1016/j.gmod.2011.12.002>

The sources support comparative judgment and bounded geometric correction. They
do not establish universal crop coordinates, appetite scores, or automatic
composition rankings.

## Required composition brief

Before changing geometry, record a schema-version-3 `composition_brief`:

```json
{
  "composition_brief": {
    "intent": "hero-led",
    "target_aspect_ratio": "4:5",
    "balance_strategy": "centered",
    "primary_anchor": [0.18, 0.16, 0.64, 0.68],
    "secondary_anchors": [
      [0.72, 0.10, 0.18, 0.20]
    ],
    "visual_flow": "The eye enters at the garnish and follows the plate curve.",
    "negative_space_side": "top",
    "plate_edge_policy": "preserve",
    "text_safe_side": "top",
    "truth_risks": [
      "Do not compress the visible bowl height.",
      "Keep the garnish attached to the hero dish."
    ]
  }
}
```

Allowed values:

- `intent`: `hero-led`, `contextual`, `pattern`, `process`, or `detail`;
- `balance_strategy`: `centered`, `thirds`, `diagonal`, `triangle`, `symmetry`,
  `asymmetry`, `pattern`, or `negative-space`;
- `negative_space_side` and `text_safe_side`: `none`, `top`, `right`, `bottom`,
  `left`, or `mixed`;
- `plate_edge_policy`: `preserve`, `intentional-crop`, or `detail-exception`.

`primary_anchor` and `secondary_anchors` are normalized boxes on the
auto-oriented source used for planning. They record what must survive; they do
not move objects or drive automatic cropping.

## Repeatable composition workflow

1. **Define the delivery.** Record destination, aspect ratio, dimensions,
   neighboring frames, text or motion-safe space, and whether the image must
   read at thumbnail, menu, social-feed, or print size.
2. **Name the hero.** Identify the one food region that explains why the image
   exists. Record supporting anchors separately. A prop does not become the hero
   merely because it is bright.
3. **Mark truth risks.** Note plate and bowl edges, food height, hands, utensils,
   ingredient boundaries, intentional perspective, and any edge whose loss
   would change portion, preparation, or identity.
4. **Read visual weight.** Compare size, contrast, saturation, sharpness,
   brightness, isolation, and recognizable detail. These are review prompts,
   not an automatic score.
5. **Trace visual flow.** Look for plate curves, utensil lines, repeated bowls,
   diagonals, gaze or hand direction, garnish trails, and light-to-dark paths.
   Remove a line only when it distracts; preserve it when it leads toward the
   hero.
6. **Choose two viable hypotheses when crop room permits.** One may be centered
   or symmetric; another may use thirds, asymmetry, a diagonal, or deliberate
   negative space. Do not manufacture a second option when the source has only
   one truthful crop.
7. **Inspect edge relationships.** Reject accidental slivers, near-tangencies,
   chopped handles, barely clipped rims, and objects that appear to collide with
   the canvas. A strong partial crop cuts decisively through a prop or plate and
   leaves enough context to read the object.
8. **Compare at delivery size and 100 percent.** Delivery size establishes
   hierarchy. Full size reveals interpolation, softness, halos, noise, and
   distorted geometry.
9. **Record the choice.** State why the chosen crop better serves the purpose,
   what was removed, which edges were intentional, and why rejected variants
   were weaker.
10. **Verify against the unchanged original.** Confirm the edit did not alter
    perceived portion size, plate shape, food height, ingredient identity, or
    the relationship among dishes and props.

## Composition-technique matrix

| Technique | Strong when | Food-specific use | Failure signal |
| --- | --- | --- | --- |
| Centered | one hero is strong, circular, frontal, or iconic | menu hero, single plate, symmetric bowl, package-ready product | static frame with no supporting rhythm or useful negative space |
| Thirds | the hero needs directional space or a secondary anchor | dish plus drink, hand entering, garnish or utensil leading inward | forced off-center plate with dead space and weaker hierarchy |
| Diagonal | lines or repeated elements already cross the frame | utensil, plate sequence, garnish trail, pouring action | added tilt makes the table or crockery look unstable |
| Triangle | three anchors differ in scale but belong together | three plates, ingredient clusters, hero plus two supports | every object competes equally or the triangle points out of frame |
| Symmetry | shape, ritual, repetition, or frontal structure matters | overhead place setting, paired drinks, layered cake | tiny alignment errors look accidental; crop trims only one side |
| Asymmetry | unequal visual weights still balance around the frame | large plate balanced by small bright garnish or prop | visually heavy corner with no counterweight |
| Pattern | repetition is the subject | dumplings, pastries, ingredient rows, table spread | one partial repeat looks accidental or breaks the rhythm |
| Negative space | the destination needs calm, text, or directional room | campaign copy, menu label, motion path | empty area is brighter or more detailed than the hero |
| Frame-within-frame | a plate, board, cloth, or hand naturally encloses food | bowl rim, tray, table setting | enclosing edge becomes a tangent or hides food |
| Layered depth | foreground, hero, and background explain scale | three-quarter spreads and process scenes | perspective correction flattens intended depth |

Do not combine techniques by checklist. Use the smallest set that explains the
actual frame.

## Camera-angle matrix

| Camera angle | Preserve | Useful strategies | Crop hazards | Perspective policy |
| --- | --- | --- | --- | --- |
| Overhead / near 90 degrees | plate geometry, arrangement, pattern, utensil lines | centered, symmetry, triangle, pattern, deliberate negative space | accidental rim clips, weak narrow crop around a round plate | rectify only when a planar surface that should read rectangular has visible keystone |
| Three-quarter / about 30–60 degrees | top surface, front edge, height, layers, diner-like depth | thirds, asymmetry, diagonal, layered depth | cutting the bowl lip at a tangent or hiding the visible height | convergence usually communicates depth; do not flatten it by default |
| Side / near eye level | silhouette, stack, drip, crumb, supporting baseline | centered, thirds, negative space, horizontal rhythm | trimming height before empty tabletop or breaking the baseline | perspective correction is exceptional because it can distort height and volume |
| Macro / detail | focus plane, texture, gloss, recognizable context | thirds, diagonal, pattern, tight centered detail | crop becomes abstract or loses ingredient identity | avoid perspective warp unless rectifying a genuinely planar detail |

## Purpose and aspect-ratio matrix

Aspect ratio follows delivery, not fashion. Confirm the actual platform
requirements when they matter.

| Purpose | Common planning ratio | Composition priority | Typical sacrifice |
| --- | --- | --- | --- |
| Delivery menu or product tile | 1:1 or 4:5 | immediate hero recognition, faithful portion, clean plate geometry | peripheral props before food context |
| Social feed portrait | 4:5 | strong thumbnail hierarchy and modest contextual support | excess tabletop or ceiling space |
| Story, Reel, Short, or vertical still | 9:16 | vertical flow, headroom for interface/text, readable hero at center-safe area | wide side props; do not squeeze a round plate into a weak strip |
| Landscape video or web hero | 16:9 | horizontal flow and intentional text-safe side | redundant foreground/background before hero structure |
| Editorial spread | source-dependent | narrative props, gesture, place, and controlled asymmetry | rigid platform ratios when print layout allows flexibility |
| Macro ingredient detail | source-dependent | texture and focus plane | complete plate, but not ingredient identity |

Never set `resize` until the geometric crop already matches the target ratio.
The helper rejects a crop-to-resize ratio mismatch over 0.5 percent rather than
stretching the food.

## Crop decision matrix

| Source condition | Crop action | Reason | Reject when |
| --- | --- | --- | --- |
| Hero and supporting objects already balance | none or minimal trim | preserve resolution and shooting intent | output ratio truly requires a new frame |
| Distracting edge object | trim decisively | simplify hierarchy | trim creates an unexplained sliver or clips truth-critical food |
| Complete circular plate is the hero | preserve the full rim with breathing room | plate geometry stabilizes the frame | deliberate close detail is the actual intent |
| Plate or prop used as an anchor | intentional partial crop | a strong edge entry can hold the composition | only a few pixels are clipped or the object becomes unrecognizable |
| Excess empty tabletop | crop before food height or plate structure | remove low-information area | space is needed for text, motion, or visual rest |
| Hand, pour, utensil, or gaze enters frame | leave room in the direction of action | maintain visual flow | the added room contains a stronger distraction |
| Pattern fills the frame | crop between repeated units deliberately | preserve rhythm | one leftover fragment reads as a mistake |
| Target ratio conflicts with hero geometry | choose another source or reshoot | aspect ratio alone does not justify damage | never outpaint or stretch to force the ratio |

## Rotation, perspective crop, and warp matrix

| Situation | Safe rotation | Perspective crop | Rectangular crop | Decision |
| --- | ---: | ---: | ---: | --- |
| Strong framing and no geometric defect | no | no | optional | reframe only for purpose or aspect |
| Camera roll or tilted tabletop edge | yes | no | usually | rotate to level, remove unsupported corners, then compose |
| Overhead planar scene has unwanted keystone | optional | yes | optional | rectify the reviewed plane only |
| Rectification plus menu or social aspect | optional | yes | yes | rectify first; compose the delivery frame second |
| Three-quarter or side convergence conveys depth | usually no | usually no | optional | preserve the photographed depth |
| Need to move, slim, widen, enlarge, or separate food or props | no | no | no | reshoot; local or mesh warp is prohibited |
| Need canvas outside the source | no | no | no | reshoot; outpainting and content-aware expansion are prohibited |
| Need different object spacing after crop | no | no | no | choose another source; seam carving is prohibited |

### Why crop and perspective crop are different

- `crop` changes the canvas boundary. It keeps every retained pixel in the same
  geometric relationship.
- `rotate_deg` corrects global roll, then takes the largest centered rectangle
  supported entirely by source pixels.
- `perspective_crop` maps one four-corner planar source region to a rectangle.
  It changes sampling geometry across that plane, so use it only for a
  defensible rectification.
- A free-form warp moves different regions independently. That can widen meat,
  slim a glass, move garnish, change plate proportions, or alter perceived
  portion size. It is not allowed.

## Perspective-crop recipe and coordinate contract

```json
{
  "schema_version": 3,
  "perspective_crop": {
    "source_quad": [
      [0.10, 0.12],
      [0.90, 0.16],
      [0.86, 0.90],
      [0.14, 0.88]
    ]
  },
  "crop": [0.05, 0.00, 0.90, 1.00]
}
```

- `source_quad` is normalized against the auto-oriented, safely rotated canvas.
- Point order is top-left, top-right, bottom-right, bottom-left.
- The quadrilateral must remain inside the source, be convex, be consistently
  ordered, and enclose a non-degenerate area.
- Destination width is derived from the average of the top and bottom source
  edge lengths. Destination height is derived from the average of the left and
  right edge lengths. There is no independent stretch control.
- The optional ordinary `crop` is normalized against the rectified rectangle
  and runs after perspective mapping.
- Operation order is auto-orient, safe rotation, perspective crop, rectangular
  crop, global corrections, local layers, sharpening, resize, and export.
- The edit and verification reports record normalized and pixel source points,
  destination points, derived dimensions, operation order, hashes, and the
  exact ImageMagick command.

If the four points cannot be selected confidently on one plane, omit the
perspective crop. A visual hunch is not enough justification to change geometry.

## Edge, hierarchy, and truth review

Before accepting a crop, answer:

1. What is the first visible food anchor at delivery size?
2. Does the second anchor support the hero or compete with it?
3. Are the brightest, sharpest, most saturated, and largest regions cooperating?
4. Is empty space intentional, and does it have a named use?
5. Does any rim, handle, utensil, hand, garnish, or repeated unit nearly touch
   the frame without a clear decision?
6. Does a partial crop look decisive rather than accidental?
7. Did perspective correction change intended height, depth, or portion?
8. Does the plate remain circular or elliptical in a way consistent with the
   camera angle?
9. Did the crop remove context needed to identify the dish or preparation?
10. Would another source frame satisfy the delivery with less geometric change?

Reject the edit when the answer depends on invented pixels, hidden content, or
moving an object. Record a reshoot limitation instead.
