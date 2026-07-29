# Scene backup, recovery, and incidents

Before updating, replacing, or deleting an existing scene, store metadata and
content in one protected JSON backup outside Git. The parent directory and
backup file must be owner-only. Verify the backup parses before writing.

Backups are evidence and recovery inputs, not permission to overwrite. A
restore uses authoritative PUT and therefore needs a new exact preview plus
write and replacement approvals.

If a write response is lost:

1. Do not retry.
2. GET metadata and content.
3. Compare the exact intended fields/elements.
4. Classify the outcome as confirmed, not observed, partial, or unknown.
5. Present recovery choices. Never automatically send the inverse write.

If PATCH readback differs because of concurrent editing, preserve both the
backup and canonical readback. Do not escalate to PUT merely to force the
planned state.
