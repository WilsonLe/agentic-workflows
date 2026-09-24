# Literature Review

Build auditable narrative, integrative, critical, conceptual/theoretical, and state-of-the-art
reviews without representing purposive or iterative discovery as a systematic review.

The package provides:

- `literature-review-workflow`, a review-type and academic-integrity gated workflow;
- progressive method, search, appraisal, synthesis, writing, and research-basis references;
- versioned Markdown, CSV, JSON, and BibTeX project templates;
- complete synthetic narrative and integrative examples plus an invalid pseudo-systematic example;
- a Python standard-library initializer, validator, and deterministic summary command.

It does not search subscription databases, bypass access controls, register protocols, conduct
meta-analysis, or claim exhaustive/PRISMA-compliant coverage.

## Local project tooling

```bash
python skills/literature-review-workflow/scripts/literature_review.py \
  init ./my-review --title "Review title" --review-type narrative
python skills/literature-review-workflow/scripts/literature_review.py validate ./my-review
python skills/literature-review-workflow/scripts/literature_review.py summary ./my-review
```

Add `--require-final` to validation only when the project is intended to be complete. Initialization
refuses non-empty destinations and never overwrites source papers or prior artifacts.
