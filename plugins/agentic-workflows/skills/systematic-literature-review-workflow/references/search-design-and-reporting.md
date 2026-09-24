# Search design and reporting

For every database, platform, register, website, grey-literature source, citation chain,
handsearch, author contact, and update, preserve:

- exact strategy as run, including controlled vocabulary and text terms;
- database/source, provider and interface, coverage when known, run timestamp, and operator;
- limits, filters, translations, and justifications;
- returned and exported counts plus any cap, partial export, or access failure;
- raw export path, format, byte count, SHA-256, export batch, importer version, and strategy file;
- dedup batch and whether the search is initial, update, or supplementary.

Raw exports are immutable inputs. Never modify one after hashing; add a new batch instead. Each
normalized record retains search-run and export-batch lineage. Search peer review is recorded only
with the real reviewer, method (for example PRESS when applicable), outcome, and date. Never
invent a librarian or information specialist.

Search breadth follows the protocol. Missing access, provider caps, partial exports, or unexplained
count mismatches block claims of completeness. Report the last search date and update status.
PRISMA-S can guide search reporting but does not create or validate the search.
