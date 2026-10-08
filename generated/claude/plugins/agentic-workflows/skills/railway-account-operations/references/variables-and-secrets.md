# Railway variables and secrets

Apply [service browser operations](browser-selection.md) and
[task authority and concealed secrets](task-authority-and-secrets.md).
Treat variable values as secrets; use names and metadata for inspection.

1. Resolve the exact browser account/workspace/project/service/environment.
2. Inspect variable names without revealing or capturing values. For optional CLI
   inventory, use the wrapper's `variable-names` operation only after matching its
   identity and target; ordinary variable-list output can reveal values.
3. For an authorized change, use supported dashboard variable controls and a
   verified concealed entry path. If the tool would expose a value in arguments,
   captures, or output, let the user enter it privately and resume after entry.
4. Identify whether Save stages changes or triggers deployment, and whether the
   new value/reference affects production or shared services.
5. Save within exact task authority, then verify the key's presence, deployment
   state, and relevant live behavior without reading back its value.

Do not use `variable set/delete`, `run`, `shell`, environment dumps, or decrypted
output as the default management path. Deletion needs exact-key scope and recovery.
Browser sessions need no account token; protected credentials are optional for a
separately needed read-only diagnostic, not a prerequisite for this workflow.
