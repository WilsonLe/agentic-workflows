# Photo curation reporting

Use this contract for food-photo shortlists that involve multiple candidates,
angles, dishes, or editing handoff.

## Report set

Create two report levels:

1. A main HTML report for the whole shoot, menu, or curation batch.
2. A detailed HTML report for each dish that has completed candidate review.

The main report is the stable entry point. It shows the current selected images,
not the full decision narrative. Each dish report holds the complete ranked
evidence. Link them in both directions.

## Main report content

For every dish, include:

- exact dish label and confidence state;
- requested angles in a consistent order;
- selected stems or filenames under each angle;
- actual selected-image previews;
- approved rotation where applicable;
- a detailed-report link when that dish has been reviewed;
- a visibly empty state for an unavailable angle.

Keep search, lightbox, and responsive behavior only when they materially help
review. Avoid repeating instructions, provenance prose, or change logs that the
audience already knows.

## Detailed dish report content

Include:

- dish label, label confidence, delivery aspect ratio, and composition
  constraints;
- the final selected set, grouped by angle;
- every candidate, grouped and ranked within its angle;
- exact stem or filename, visible selected/not-selected state, actual source
  preview, approved rotation, and one image-specific reason;
- a link back to the main report.

Reasons must describe visible evidence. Cover the decisive factors only:
sharpness at the food, appetising texture, food-facing direction, plate
orientation, crop viability, background distraction, glare, clipped plating,
or redundancy with a stronger frame. Do not invent ingredients, preparation
methods, or menu status.

## Selection rules

- Inspect every candidate at a useful size before ranking.
- Use measurements only as supporting evidence. Never select solely from
  sharpness, brightness, or histogram metrics.
- Rank within angle, not across incomparable angles.
- Prefer complementary selected frames over near-duplicates.
- Preserve explicit user composition constraints.
- Keep missing angles empty.
- Record exact rotation; do not silently bake it into an untraceable copy.
- Keep the original image and matching RAW source unchanged.

## Source of truth

Prefer one structured data source that drives the main report, detailed reports,
and machine-readable shortlist manifest. If an existing repository already uses
an HTML data block as the curated source, update that source and regenerate the
manifest rather than maintaining parallel manual lists.

## Verification

Before handoff, verify:

- every referenced image exists;
- every selected source has its expected RAW pair when the shoot contract
  requires one;
- candidate and selected counts agree with the structured source;
- one source is not assigned to multiple dishes unless explicitly approved;
- rotations and angle labels agree across reports and manifest;
- main-to-detail and detail-to-main links resolve;
- HTML and embedded JavaScript parse;
- desktop and narrow layouts render when a permitted local browser is
  available;
- generated hashes or inventory records are refreshed when the repository
  maintains them.
