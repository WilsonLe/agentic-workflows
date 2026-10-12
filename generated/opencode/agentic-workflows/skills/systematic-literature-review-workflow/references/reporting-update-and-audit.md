# Reporting, update, and audit

Generate reporting from authoritative ledgers. Include flow counts, study/report characteristics,
excluded full texts and reasons, unavailable evidence, appraisal domains, synthesis results,
certainty summaries when applicable, protocol deviations, automation, funding, contributor
conflicts, data/code availability, limitations, last search date, and update/living status.

Select reporting guidance by review family. PRISMA 2020, an extension, SWiM, or another checklist
supports reporting; a populated checklist is not proof that conduct was correct or complete. Record
each item as reported, not applicable with reason, or unresolved.

Every state transition records prior/new state, actor identity and type, timestamp, basis, and
blockers. Valid forward states are feasibility, protocol, search, screening, extraction, appraisal,
synthesis, reporting, and complete; `blocked`, `update_due`, and `superseded` remain explicit audit
states. Do not erase a prior transition.

Mark `complete` only after every protocol-required structural, evidence, and human gate passes.
Expired search currency becomes `update_due`. A new protocol/version may supersede the old review
without deleting its evidence.
