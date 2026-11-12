# Scoped secret operations and token delivery

The [installed CLI help](https://infisical.com/docs/cli/reference-agents#secrets-manager-secrets-get)
owns exact flags. Validate the chosen route with synthetic values before a real
secret. The examples below are process-internal commands, not commands whose raw
output should be returned by an agent tool. Use a reviewed local subprocess bridge
with `shell=False`, captured stdout/stderr, explicit timeouts, and sanitized errors.
No new persistent token store or custom service client is needed.

## Get

Resolve the exact instance/profile/project/environment/folder and one key. Read
the shared value without following imports, subfolders, overrides or expansion:

```sh
infisical secrets-manager secrets get VERCEL_TOKEN --plain --silent \
  --domain https://app.infisical.com --profile agentic-workflows \
  --projectId <project-id> --env dev --path /providers/vercel \
  --include-imports=false --secret-overriding=false --expand=false
```

Capture both streams internally. Require success and a nonempty exact token;
reject `*not found*`, control characters and unexpected multiline token output.
Do not accept a missing-secret marker as a credential or use inherited/cached
authentication after failure. Do not strip or transform general secret values;
the single-line validation applies to provider API tokens only. A general get
returns presence/metadata to the agent and delivers the value only to the
authorized concealed consumer. No command in this workflow displays a raw secret.

## Set: create or update

Choose `create` for a new secret and `update` only when replacement is authorized.
Both accept `--file` with a `.env` or YAML document. Use a serializer to write
exactly the authorized key/value into an owner-only temporary YAML file in a
private directory outside Git; JSON object syntax is valid YAML and preserves
quoting, newlines, `@` and shell metacharacters without interpolation. Do not use
`NAME=value`, `--token`, `--client-secret`, `--show-values`, shell substitutions
as arguments, or an unvalidated `NAME=@file` shortcut.

```sh
infisical secrets-manager secrets create --file <private-temp-file.yaml> \
  --domain https://app.infisical.com --profile agentic-workflows \
  --projectId <project-id> --env dev --path /providers/vercel --type shared
```

Keep file mode 0600 and directory mode 0700, reject symlinks and unsafe source
paths, and capture both CLI streams even when table output is normally masked.
Never serialize a secret into a tool-call argument to create the file. Obtain it
from an approved concealed source in the same local process or let the user enter
it privately. Preserve any preexisting input. In a `finally` block remove only
task-owned temporary plaintext. Read the same secret back inside that process
and compare exact values; return only match/status. An acknowledgement alone is
not verified storage. On timeout/unknown outcome, inspect before retrying. Creation
conflicts and update-not-found errors do not authorize switching operations.

## Deliver to the service CLI

Resolve the provider operation before fetching its token. The token key may have
a different stored name; map it to the documented child environment variable in
the [shared provider table](../../agentic-workflows/references/service-browser-operations.md#cli-token-mappings).
Use the subprocess bridge to fetch just that named token, then launch the resolved
service CLI executable with an argument array and the required token environment.
Validate token presence before launch so the CLI cannot silently use cached auth.
Supply exact provider target flags accepted by that CLI version.

Construct the child environment from required nonsecret execution variables and
the selected token. Exclude Infisical access/client tokens, other providers'
credentials, alternate auth variables, shell tracing/debug options and unsafe
credential/config overrides. Do not pass the complete agent environment or
Infisical export to the child. Check CLI token precedence and suppress interactive
login; ambient auth must not select a different identity. The provider identity
read remains mandatory even with an explicitly sourced token.

Capture stdout/stderr before the agent tool returns. Project only the fields
required for the task; suppress authorization data, environment values, private
records and token-bearing URLs on success and failure. Exact-token replacement
alone does not make arbitrary customer data or encoded secrets safe. Use names-only
commands where available; if output cannot be safely projected, keep that operation
blocked. Never invoke `env`, `printenv`, token display or bulk export as verification.

The native `infisical secrets-manager run -- <command>` is available for application
runtime injection. It injects a folder and forwards child output; it is not by
itself a safe provider-token bridge. Provider operations still need the named-token,
minimal-environment, output-filtering and identity checks above. A helper's success
does not grant deployment, communication, billing or destructive authority.
