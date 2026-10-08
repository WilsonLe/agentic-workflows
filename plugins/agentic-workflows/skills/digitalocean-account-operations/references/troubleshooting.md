# DigitalOcean browser and optional doctl diagnosis

Establish the control-panel team/account/project/resource and incident window
first. Use [service browser operations](browser-selection.md) as the base.

For a needed read-only diagnostic, reuse authorized protected authentication and
verify `doctl --context default account get --output json` through the bundled
launcher, then match the identity and exact resource/region/project to the browser.
Do not use a stored non-default context or switch context silently. If matching
cannot be established, stop that diagnostic and continue safe browser work.

Inspect installed read-command help. Bound output, pagination, timeouts, and logs.
Avoid raw trace/verbose output, credentials, connection strings, or environment
values; sanitize any necessary diagnostic before reporting.

- Authentication/access failure: report identity and denied scope; do not broaden
  permission or replace credentials automatically.
- Missing/empty resource: recheck account, project, region, filters, and pagination.
- Unknown syntax: use installed help and official documentation for exact reads.
- Transient read error: bounded backoff is appropriate; unknown writes need readback.

If credential setup for this optional diagnostic is authorized, retain the
`digitalocean_configure_credentials.py` protected private-file, verification, and
archival contract. Normal browser onboarding never asks for an API-token file.
Management and mitigation use the UI; CLI logs/status authority excludes writes.
Report the supplemental channel, verified scope, sanitized result, and limitations.
