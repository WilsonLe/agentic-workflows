# Railway token contract

Use the [shared CLI-token contract](../../agentic-workflows/references/service-browser-operations.md)
and [Infisical Account Operations](../../infisical-account-operations/SKILL.md).
Fetch the appropriate named token from Infisical for every remote CLI operation.
`RAILWAY_TOKEN` is a project token; `RAILWAY_API_TOKEN` is an account/workspace token.
Set exactly the appropriate one in the child environment and remove the other.
Do not infer account-level permissions from a project token or automatically fetch
broader access after denial. Verify workspace/project/environment/service IDs
through read-only commands with the selected token before dependent operations.

Missing or expired access blocks dependent work until Infisical authentication or
the authorized token is repaired. No cached login, connector or dashboard fallback.
Do not copy local token files or export bootstrap credentials. Application environment
values remain separate runtime secrets under the shared concealed-secret contract.
