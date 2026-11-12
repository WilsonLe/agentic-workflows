# Railway variables and secrets

Use the [Infisical-backed CLI channel](../../agentic-workflows/references/service-browser-operations.md).
Treat variable values as secrets. Inspect the installed command's input/output
behavior. Capture both streams in the concealed subprocess and project only
names/metadata before tool output; client-side redaction after a tool has returned
values is insufficient. If no safe projection is available, keep inventory blocked.

For authorized changes, resolve the exact environment/service and variable name,
check existence by metadata, and use a supported concealed stdin/file input. Do not
put `NAME=value` secrets in argv, chat or tool calls. If this CLI version requires
exposed arguments, report the capability gap rather than using a connector or
inventing a flag. Do not trigger a deployment merely to verify token access.

Confirm whether the change stages or triggers deployment and match its actual
production/write effect to existing authority. Verify presence, resulting deployment
state and health without exposing the value. Deletion needs the exact key/target,
impact, recovery source and authority covering that destructive effect.
