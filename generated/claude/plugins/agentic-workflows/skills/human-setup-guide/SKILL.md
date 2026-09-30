---
name: human-setup-guide
description: Prepare a verified, step-by-step guide or optional interactive script for provider setup, secrets, migration, or cutover steps that require human action.
---

<!-- catalog-prerequisites:start -->
## Prerequisites

- No additional setup beyond installing this plugin.

<!-- catalog-prerequisites:end -->

# Human setup guide

Use this skill for manual steps the agent cannot complete with the user's current authorization and tools. Inspect the real repository configuration and current provider documentation or interface first. Do the authorized preparatory work before handing the user a procedure.

1. List each human action and the value or state it produces. Map each value to its destination, such as a local environment file, provider setting, or CI secret. Mark secrets without reading or printing their values.
2. Verify the current route to every control and the exact target account or project. If a dashboard step is unknown, investigate it or label the uncertainty. Do not invent menu paths or claim a saved setting proves the end-to-end flow.
3. Order steps by dependency. Give each step a visible completion check and a safe resume point. Place a clear confirmation immediately before an irreversible migration or cutover.
4. When repetition justifies a script, use hidden input for secrets, idempotent writes, no secret-bearing logs, and narrow names for variables. Validate syntax and review the destinations statically before asking the human to run it. Keep a one-off script out of the maintained package unless reuse is intended.
5. After the human completes the steps, read back the resulting configuration through the authorized surface and verify the actual flow separately. Report each stage at its observed status.

This skill does not enlarge the task's external-mutation authority. Follow the repository's delivery rules and the Codex Standard Development Workflow when available if a reusable guide or script is committed.
