# Excalidraw browser failure handling and optional diagnostics

A login/access denial, missing collection/scene, UI error, or save uncertainty
requires checking the browser identity/workspace and exact target first. Do not
switch accounts, weaken permissions, or move to REST writes to avoid a restriction.

After an unknown save/create/delete outcome, reopen/list the exact target and
compare saved state before retrying. If persistence cannot be established, report
confirmed, partial, not observed, or unknown evidence and recovery choices.

Optional protected read-only helper diagnostics must independently match browser
identity and scope. Inspect current documented errors/rate limits; use bounded
backoff for safe reads and sanitize error bodies. Never print authorization
headers, credentials, private scene contents, or unreviewed logs. Do not blindly
retry writes or infer live saved state from an API acknowledgement.
