# Protocol and registration

Create the protocol before formal screening. Version it and cover objectives, question, eligibility,
information sources, complete draft strategies, selection, data items, appraisal, synthesis,
certainty, missing data, subgroup and sensitivity work, reporting bias, automation, human
verification, conflict handling, amendments, dissemination, search currency, and update policy.

`protocol-state.json` records one truthful protocol status:

- `prospective_unregistered`
- `prospective_registered`
- `prospective_published`
- `amended`
- `retrospective_reconstructed`

Registration or publication requires an exact registry/publisher, identifier, URL, version, and
verification date. A planned submission is not registration. PROSPERO is conditional on current
scope eligibility and is never assumed universally.

After approval, append each change to `amendments.csv` with timing (`prospective` or
`retrospective`), rationale, affected artifacts, actor, and timestamp. Preserve the prior protocol.
Propagate staleness to searches, decisions, extraction, appraisal, or synthesis when eligibility or
analysis changes.
