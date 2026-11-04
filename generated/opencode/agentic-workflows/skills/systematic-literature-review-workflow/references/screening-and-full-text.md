# Screening and full text

Pilot eligibility rules and record the protocol version and exclusion vocabulary. Each
title/abstract and full-text entry includes the record/report, contributor, contributor type,
qualification/role, independence status, decision, timestamp, rationale or locator, and automation
assistance.

Allowed working states include `include`, `exclude`, `maybe`, `conflict`,
`awaiting_full_text`, `duplicate_report`, `retracted`, and `withdrawn`. Full-text exclusion uses
exactly one protocol-defined primary reason plus optional notes. Retain unavailable full text and
attempt history explicitly.

When the chosen method requires independent duplicate decisions, accept only distinct qualified
human identities. AI assistants, subagents, repeated prompts, or human confirmation of an AI
decision do not create independence. Conflicts block progression until a real resolution or
adjudication record identifies the people, basis, and timestamp.

Included reports link to a verified full-text file, byte count, hash, metadata record, retrieval
version, and notes with exact locators. Retractions and withdrawals remain visible and trigger an
impact review; they are never silently removed.
