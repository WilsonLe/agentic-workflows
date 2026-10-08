# Scene backup, recovery, and incidents

Apply [authenticated CLI and browser assistance](browser-selection.md): verify
CLI identity and exact project target, authenticate via the built-in browser when
needed, and use browser operations only for an authenticated client capability gap.

Before updating, replacing, or deleting an existing scene, store metadata and
content in one protected JSON backup outside Git. The parent directory and
backup file must be owner-only. Verify the backup parses before writing.

Backups are evidence and recovery inputs, not permission to overwrite. A
restore uses authoritative PUT and therefore needs an explicit restore request
and a new exact preview, but no typed token or second confirmation.

If a write response is lost:

1. Do not retry.
2. GET metadata and content.
3. Compare the exact intended fields/elements.
4. Classify the outcome as confirmed, not observed, partial, or unknown.
5. Present recovery choices. Never automatically send the inverse write.

If PATCH readback differs because of concurrent editing, preserve both the
backup and canonical readback. Do not escalate to PUT merely to force the
planned state.
