# Hermes research stack

Verified against the official NousResearch `hermes-agent` repository at commit `ef60509a26d07b40c4f512f864c8242a5bce4076` (2026-07-26).

## Relevant built-in skills

| Skill | Official path | Role |
|---|---|---|
| `arxiv` | `skills/research/arxiv` | Search arXiv by keyword, author, category, or ID; retrieve metadata; generate BibTeX; read remote PDFs; use Semantic Scholar citation and recommendation APIs; preserve version suffixes. |
| `research-paper-writing` | `skills/research/research-paper-writing` | Full ML/AI publication pipeline. Its literature phase requires `arxiv`, breadth-then-depth search, two-source verification, programmatic BibTeX, and claim validation. Use its citation workflow here, not its experiment or venue-specific phases. |
| `ocr-and-documents` | `skills/productivity/ocr-and-documents` | Extract text from remote or local PDFs. Tries `web_extract` first, then PyMuPDF, then heavier OCR for scans, equations, or complex layouts. |
| `humanizer` | `skills/creative/humanizer` | Remove formulaic AI prose while preserving meaning and intended voice. Recheck citations and technical statements after applying it. |
| `pdf` | `skills/productivity/pdf` | PDF creation and manipulation. Useful for inspection or conversion, but not a substitute for full-paper reading. |

The official built-in `skills/research/` directory currently contains two skills: `arxiv` and `research-paper-writing`.

## Load commands in Hermes

```text
skill_view("arxiv")
skill_view("ocr-and-documents")
skill_view("research-paper-writing", "references/citation-workflow.md")
skill_view("humanizer")
```

Check availability for the active profile:

```text
skills_list()
```

CLI verification:

```bash
hermes -p academic-writer skills list --enabled-only
```

If `arxiv` is missing, search the hub and install the exact official slug shown by the current Hermes version. Official documentation has used:

```bash
hermes skills install official/research/arxiv
```

Restart or reset the session when Hermes reports that newly installed skills require a fresh prompt cache.

## Important boundaries

- `arxiv` can read a remote PDF through `web_extract`, but it does not by itself require saving the PDF locally, hashing it, or writing a per-paper research note. This plugin adds those controls.
- arXiv is a preprint repository, not a universal peer-review signal.
- Semantic Scholar adds citation graphs and related-paper discovery; Crossref/DOI metadata is better for published bibliographic records.
- The general `research-paper-writing` skill targets ML/AI publication and experiments. Coursework and literature-review tasks should reuse its citation verification, not invent experimental results.

## Primary sources

- https://github.com/NousResearch/hermes-agent/blob/main/skills/research/arxiv/SKILL.md
- https://github.com/NousResearch/hermes-agent/blob/main/skills/research/research-paper-writing/SKILL.md
- https://github.com/NousResearch/hermes-agent/blob/main/skills/productivity/ocr-and-documents/SKILL.md
- https://github.com/NousResearch/hermes-agent/blob/main/skills/creative/humanizer/SKILL.md
- https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md
