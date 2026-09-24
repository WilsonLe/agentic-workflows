# Systematic Literature Review

This standalone Agentic Workflows plugin helps a real review team plan, conduct, audit, and report a
systematic review. It separates conduct guidance from reporting guidance, preserves a reversible
record/report/study identity chain, and blocks unsupported completion claims.

The bundled standard-library CLI creates a review-project skeleton, imports a bounded set of local
records, emits conservative duplicate candidates, derives flow counts, validates structural and
human gates, and produces a redacted status summary. It does not search databases, decide
eligibility, perform appraisal or meta-analysis, simulate reviewers, register protocols, or publish.

## CLI

```bash
python skills/systematic-literature-review-workflow/scripts/systematic_review.py init ./review
python skills/systematic-literature-review-workflow/scripts/systematic_review.py import ./review export.ris \
  --search-run-id search-run-001 --source medline
python skills/systematic-literature-review-workflow/scripts/systematic_review.py dedup-candidates ./review
python skills/systematic-literature-review-workflow/scripts/systematic_review.py counts ./review
python skills/systematic-literature-review-workflow/scripts/systematic_review.py validate ./review
python skills/systematic-literature-review-workflow/scripts/systematic_review.py validate ./review --require-final
python skills/systematic-literature-review-workflow/scripts/systematic_review.py summary ./review
```

Review data belongs in a user-selected project outside this plugin source. Raw exports are copied
as immutable inputs and hashed before normalized records are appended.

## Method boundary

Use the workflow skill for systematic, scoping, rapid, mapping, umbrella, qualitative,
mixed-methods, or other explicitly selected evidence-synthesis families. An ordinary narrative or
integrative literature review is a different capability: route to a separately installed
`literature-review-workflow` capability when available, otherwise explain the boundary and use
ordinary research support without claiming a systematic method.
