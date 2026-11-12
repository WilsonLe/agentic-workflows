# Projects, deployments, secrets and recovery

Use the [CLI-token contract](../../agentic-workflows/references/service-browser-operations.md).
Resolve exact team/project/environment, source revision and active deployment via
CLI reads. Deployment, promotion, production routing, domains and rollback have
distinct effects; perform only effects covered by the request.

Inspect the installed CLI's deployment/build/source inputs and repository runbook.
Complete required build/tests locally, then use the authorized CLI deployment
command with explicit target selection. Review source upload/ignore rules; exclude
agent authentication, environment files and unrelated local state.

Request environment names/metadata without decrypted values. Secret changes need
supported concealed stdin/file input, captured output and verified presence. Never
put values in flags or visible arguments. Missing input/output support blocks the
operation. Bound logs to the deployment/time window and sanitize before tool output.

For protected previews, inspect the CLI's supported access mechanism, preserve
protection and conceal token-bearing URLs. Do not fall back to connected tools;
report absent CLI support. Use supported browser controls for the actual user flow.

Before deployment or rollback, record the last healthy revision and whether recovery
also needs configuration/database/integration changes. Wait for terminal deployment
state, verify active revision/alias and relevant flows, and read back persistent
configuration separately. A successful upload or queued deployment is insufficient.
